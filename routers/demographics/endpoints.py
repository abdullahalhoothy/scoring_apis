"""
Demographics scoring router module
Handles demographics scoring requests and related operations
"""

from fastapi import APIRouter
from request_processor import request_handling
from request_models import ReqDemographics
from response_models import ResDemographics
from routers.demographics.logic import calculate_demographics_score

from config_factory import CONF


demographics_router = APIRouter()


@demographics_router.post(CONF.fetch_dataset, response_model=ResDemographics)
async def fetch_dataset_ep(req: ReqDemographics):
    """
    Calculate demographics score based on location and target age
    
    Args:
        req: Demographics request containing lat, lng, radius, target_age
        
    Returns:
        Demographics score response
    """
    response = await request_handling(
        req,
        ReqDemographics,
        ResDemographics,
        calculate_demographics_score,
    )
    return response
