"""
Complementary business scoring router module  
Handles complementary business scoring requests and related operations
"""

from fastapi import APIRouter
from request_processor import request_handling
from request_models import ReqComplementary
from response_models import ResComplementary
from routers.complimentary.logic import calculate_complementary_score

from config_factory import CONF


complementary_router = APIRouter()


@complementary_router.post(CONF.complementary_score, response_model=ResComplementary)
async def complementary_score_ep(req: ReqComplementary):
    """
    Calculate complementary business score based on location and business categories
    
    Args:
        req: Complementary request containing lat, lng, radius, categories, target_num
        
    Returns:
        Complementary score response
    """
    response = await request_handling(
        req,
        ReqComplementary,
        ResComplementary,
        calculate_complementary_score,
    )
    return response