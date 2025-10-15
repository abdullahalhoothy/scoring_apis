"""
Competition scoring router module
Handles competition scoring requests and related operations
"""

from fastapi import APIRouter
from request_processor import request_handling
from request_models import ReqCompetition
from response_models import ResCompetition
from routers.competition.logic import calculate_competition_score

from config_factory import CONF


competition_router = APIRouter()


@competition_router.post(CONF.competition_score, response_model=ResCompetition)
async def competition_score_ep(req: ReqCompetition):
    """
    Calculate competition score based on location and business categories
    
    Args:
        req: Competition request containing lat, lng, radius, categories, target_num
        
    Returns:
        Competition score response
    """
    response = await request_handling(
        req,
        ReqCompetition,
        ResCompetition,
        calculate_competition_score,
    )
    return response