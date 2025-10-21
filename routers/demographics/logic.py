from typing import Dict, Any
from request_models import ReqDemographics
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module
from scoring_algorithms import calculate_demographics_score

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Demographics module loaded successfully")


async def calculate_demographics_score_endpoint(req: ReqDemographics) -> Dict[str, Any]:
    """Calculate demographics score based on location and target age"""
    
    logger.info(f"Starting demographics score calculation for location: lat={req.lat}, lng={req.lng}, radius={req.radius}, target_age={req.target_age}")
    
    # Use the shared package function that does everything (database query + calculate)
    score_data = await calculate_demographics_score(
        database_url=CONF.database_url,
        lat=req.lat,
        lng=req.lng,
        radius=req.radius,
        target_age=req.target_age,
        sex_preference=req.sex_preference
    )
    
    logger.info(f"Final demographics score data: {score_data}")
    
    return score_data


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
