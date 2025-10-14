"""
Data & Layers Management router module
Handles dataset fetching, layer management, and related operations
"""

from typing import Any
from fastapi import APIRouter, Request
from request_processor import request_handling

from config_factory import CONF


data_layers_router = APIRouter()


# @data_layers_router.get(
#     CONF.country_city, response_model=dict[str, list[CityData]]
# )
# async def country_city():
#     response = await request_handling(
#         None,
#         None,
#         dict[str, list[CityData]],
#         fetch_country_city_data,
#         wrap_output=True,
#     )
#     return response


# @data_layers_router.post(CONF.fetch_dataset, response_model=ResFetchDataset)
# async def fetch_dataset_ep(req: ReqFetchDataset, request: Request):
#     response = await request_handling(
#         req.request_body,
#         ReqFetchDataset,
#         ResFetchDataset,
#         fetch_dataset,
#         wrap_output=True,
#     )
#     return response
