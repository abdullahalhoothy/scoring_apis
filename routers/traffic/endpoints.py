from fastapi import APIRouter, HTTPException
from request_models import ReqTraffic
from response_models import ResTraffic
from routers.traffic.logic import calculate_traffic_score_endpoint
from config_factory import CONF

router = APIRouter()


@router.post(f"{CONF.traffic_score}")
async def traffic_score(req: ReqTraffic) -> ResTraffic:
    """Calculate traffic score based on location and storefront parameters"""
    
    try:
        # Calculate traffic score
        score_data = await calculate_traffic_score_endpoint(req)
        
        # Return structured response
        return ResTraffic(**score_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating traffic score: {str(e)}")