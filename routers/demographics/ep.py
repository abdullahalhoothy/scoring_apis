"""
Data & Layers Management router module
Handles dataset fetching, layer management, and related operations
"""

from typing import Any
from fastapi import APIRouter, Request
from request_processor import request_handling

from config_factory import CONF


demographics_router = APIRouter()



@demographics_router.post(CONF.fetch_dataset, response_model=ResDemographics)
async def fetch_dataset_ep(req: ReqDemographics, request: Request):
    response = await request_handling(
        req.request_body,
        ReqDemographics,
        ResDemographics,
        calculate_demographics_score,
    )
    return response
