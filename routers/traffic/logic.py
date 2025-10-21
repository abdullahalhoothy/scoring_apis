from typing import Dict, Any
from request_models import ReqTraffic
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module
from scoring_algorithms import calculate_traffic_score

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Traffic module loaded successfully")

async def calculate_traffic_score_endpoint(req: ReqTraffic) -> Dict[str, Any]:
    """Calculate traffic score based on location and storefront parameters"""
    
    logger.info(f"Starting traffic score calculation for location: lat={req.lat}, lng={req.lng}, direction={req.storefront_direction}, day={req.day}, time={req.time}")
    
    # Use the shared package function that does everything
    score_data = await calculate_traffic_score(
        lat=req.lat,
        lng=req.lng,
        storefront_direction=req.storefront_direction,
        day=req.day,
        time=req.time,
        traffic_api_base_url=CONF.traffic_api_base_url
    )
    
    logger.info(f"Final traffic score data: {score_data}")
    
    return score_data

# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
