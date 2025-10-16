"""
Income scoring router module
Handles income scoring requests and related operations
"""

from fastapi import APIRouter
from request_processor import request_handling
from request_models import ReqIncome
from response_models import ResIncome
from routers.Income.logic import calculate_income_score

from config_factory import CONF


income_router = APIRouter()


@income_router.post(CONF.income_score, response_model=ResIncome)
async def income_score_ep(req: ReqIncome):
    """
    Calculate income score based on location and target income level
    
    Args:
        req: Income request containing lat, lng, radius, target_income_level
        
    Returns:
        Income score response
    """
    response = await request_handling(
        req,
        ReqIncome,
        ResIncome,
        calculate_income_score,
    )
    return response