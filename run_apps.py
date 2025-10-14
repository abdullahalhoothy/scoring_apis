from app_logger import get_logger, setup_uvicorn_logging  # Initialize logging first
from fastapi_app import app
import threading
import subprocess
import sys
import os

logger = get_logger(__name__)


if __name__ == "__main__":
    logger.info("Starting application launcher...")
    
    logger.info("Starting FastAPI app on localhost:8000")
    
    # Configure uvicorn server
    from uvicorn.config import Config
    from uvicorn.server import Server
    
    config = Config(app, host="localhost", port=8000, log_level="info", access_log=True)
    server = Server(config)
    
    # Setup uvicorn logging to write to our centralized log file
    setup_uvicorn_logging()
    
    # Start the server
    server.run()
