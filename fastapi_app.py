import os
import time
import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from database import Database
from app_logger import get_logger

# Import routers
from routers.demographics.endpoints import demographics_router
from routers.competition.endpoints import competition_router
from routers.complimentary.endpoints import complementary_router
from routers.Income.endpoints import income_router
from routers.traffic.endpoints import router as traffic_router


logger = get_logger(__name__)
logger.info("FastAPI application module loaded successfully")


app = FastAPI()
logger.info("FastAPI app instance created")

# Include routers
app.include_router(demographics_router, prefix="/api/v1", tags=["Demographics"])
app.include_router(competition_router, prefix="/api/v1", tags=["Competition"])
app.include_router(complementary_router, prefix="/api/v1", tags=["Complementary"])
app.include_router(income_router, prefix="/api/v1", tags=["Income"])
app.include_router(traffic_router, prefix="/api/v1", tags=["Traffic"])

# Ensure static directory exists
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    logger.info(f"Created static directory: {static_dir}")

app.mount("/static", StaticFiles(directory="static"), name="static")


def cleanup_old_files(static_dir: str = "static"):
    """
    Remove all files older than 7 days from all subdirectories in static directory
    """
    try:
        current_time = time.time()
        max_age_seconds = 7 * 24 * 3600  # 7 days in seconds
        deleted_count = 0

        # Walk through all subdirectories and files
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                filepath = os.path.join(root, file)
                file_age = current_time - os.path.getctime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} old files (older than 7 days)")

    except Exception as e:
        logger.error(f"Error during file cleanup: {str(e)}")


app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Re-establish our logging configuration after uvicorn startup
    from app_logger import setup_logging

    setup_logging(force_reset=True)
    logger.info("FastAPI startup - logging re-configured")

    await Database.create_pool()
    # Clean up old plots on startup
    cleanup_old_files()
    logger.info("FastAPI startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI shutdown initiated")
    await Database.close_pool()
    # Run cleanup in a thread to not block
    await asyncio.get_event_loop().run_in_executor(None, cleanup_old_files)
    # Wait a moment to ensure threads are cleaned up
    await asyncio.sleep(1)
    logger.info("FastAPI shutdown completed")
