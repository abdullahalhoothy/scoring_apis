"""
Data & Layers Management router module
Handles dataset fetching, layer management, and related operations
"""

from typing import Any
from fastapi import APIRouter, Request
from request_processor import request_handling

from config_factory import CONF


traffic_router = APIRouter()



# @traffic_router.post(CONF.fetch_dataset, response_model=ResFetchDataset)
# async def fetch_dataset_ep(req: ReqFetchDataset, request: Request):
#     response = await request_handling(
#         req.request_body,
#         ReqFetchDataset,
#         ResFetchDataset,
#         fetch_dataset
#     )
#     return response
