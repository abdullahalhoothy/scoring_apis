from typing import Dict, Any
from request_models import ReqCompetition
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module
from scoring_algorithms import calculate_competition_score

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Executing Competition Score logic")


async def calculate_competition_score_endpoint(req: ReqCompetition) -> Dict[str, Any]:
    """Calculate competition score based on location and business categories"""
    
    logger.info(f"Starting competition score calculation for location: lat={req.lat}, lng={req.lng}, radius={req.radius}")
    
    # Use the shared package function that does everything (login + fetch + calculate)
    score_data = await calculate_competition_score(
        base_url=CONF.external_api_base_url,
        lat=req.lat,
        lng=req.lng,
        radius=req.radius,
        competition_business_categories=req.competition_business_categories,
        target_num_per_category=req.target_num_per_category
    )
    
    logger.info(f"Final competition score data: {score_data}")
    
    return score_data


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
