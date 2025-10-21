from typing import Dict, Any
from request_models import ReqIncome
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module
from scoring_algorithms import calculate_income_score

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Income module loaded successfully")


async def calculate_income_score_endpoint(req: ReqIncome) -> Dict[str, Any]:
    """Calculate income score based on location and target income level"""
    
    logger.info(f"Starting income score calculation for location: lat={req.lat}, lng={req.lng}, radius={req.radius}, target_income={req.target_income_level}")
    
    # Use the shared package function that does everything (database query + calculate)
    score_data = await calculate_income_score(
        database_url=CONF.database_url,
        lat=req.lat,
        lng=req.lng,
        radius=req.radius,
        target_income_level=req.target_income_level
    )
    
    logger.info(f"Final income score data: {score_data}")
    
    return score_data


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
