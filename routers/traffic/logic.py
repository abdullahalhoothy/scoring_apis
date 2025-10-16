import aiohttp
from typing import Dict, Any
from datetime import datetime
import asyncio
from request_models import ReqTraffic
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Database module loaded successfully")

async def calculate_traffic_score(req: ReqTraffic) -> Dict[str, Any]:
    """Calculate traffic score based on location and storefront parameters"""
    
    # Login to get auth token
    auth_token = await login_to_traffic_api()
    
    # Submit traffic analysis job
    job_id = await submit_traffic_job(req, auth_token)
    
    # Poll for results
    job_result = await poll_job_status(job_id, auth_token)
    
    # Extract and format results
    score_data = format_traffic_results(job_result, req)
    
    return score_data


async def login_to_traffic_api() -> str:
    """Login to traffic API and get auth token"""
    
    login_url = f"{CONF.traffic_api_base_url}/login"
    login_data = {
        "username": "admin",  # Default from the example
        "password": "123456"  # Default from the example
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, data=login_data) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data["access_token"]


async def submit_traffic_job(req: ReqTraffic, token: str) -> str:
    """Submit traffic analysis job"""
    
    analyze_url = f"{CONF.traffic_api_base_url}/analyze-traffic"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "locations": [
            {
                "lat": req.lat,
                "lng": req.lng,
                "storefront_direction": req.storefront_direction,
                "day": req.day,
                "time": req.time,
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(analyze_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            result = await response.json()
            return result["job_id"]


async def poll_job_status(job_id: str, token: str) -> Dict[str, Any]:
    """Poll job status until completion"""
    
    status_url = f"{CONF.traffic_api_base_url}/job/{job_id}"
    headers = {"Authorization": f"Bearer {token}"}
    max_attempts = 60  # 5 minutes with 5-second intervals
    attempt = 0
    
    while attempt < max_attempts:
        async with aiohttp.ClientSession() as session:
            async with session.get(status_url, headers=headers) as response:
                response.raise_for_status()
                job_data = await response.json()
                
                status = job_data.get("status")
                
                if status == "done":
                    return job_data
                elif status in ("failed", "canceled"):
                    error_msg = job_data.get("error", "Unknown error")
                    raise Exception(f"Traffic analysis job {status}: {error_msg}")
                elif status in ("pending", "running"):
                    # Wait 5 seconds before polling again
                    await asyncio.sleep(5)
                    attempt += 1
                else:
                    await asyncio.sleep(5)
                    attempt += 1
    
    raise Exception(f"Traffic analysis job {job_id} timed out after {max_attempts} attempts")


def format_traffic_results(job_result: Dict[str, Any], req: ReqTraffic) -> Dict[str, Any]:
    """Format traffic analysis results"""
    
    results_data = job_result.get("result", {}).get("results", [])
    
    if not results_data:
        return {
            "score": 0.0,
            "storefront_score": 0.0,
            "area_score": 0.0,
            "screenshot_filename": "",
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "explanation": "No traffic analysis data available"
        }
    
    # Get the first (and only) result since we submitted one location
    result = results_data[0]
    
    if result.get("error"):
        return {
            "score": 0.0,
            "storefront_score": 0.0,
            "area_score": 0.0,
            "screenshot_filename": "",
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "explanation": f"Traffic analysis failed: {result['error']}"
        }
    
    # Extract scores
    traffic_score = result.get("score", 0)
    storefront_score = result.get("storefront_score", 0)
    area_score = result.get("area_score", 0)
    screenshot_url = result.get("screenshot_url", "")
    screenshot_filename = screenshot_url.split("/")[-1] if screenshot_url else ""
    
    # Generate explanation
    score_quality = "excellent" if traffic_score >= 80 else "good" if traffic_score >= 60 else "moderate" if traffic_score >= 40 else "below average" if traffic_score >= 20 else "poor"
    storefront_quality = "high" if storefront_score >= 70 else "moderate" if storefront_score >= 40 else "low"
    area_quality = "busy" if area_score >= 70 else "moderate" if area_score >= 40 else "quiet"
    
    explanation = f"Overall traffic score {traffic_score} indicates {score_quality} traffic conditions. Storefront visibility: {storefront_quality} ({storefront_score}), Area activity: {area_quality} ({area_score}). Analysis for {req.storefront_direction}-facing storefront on {req.day} at {req.time}"
    
    return {
        "score": traffic_score,
        "storefront_score": storefront_score,
        "area_score": area_score,
        "screenshot_filename": screenshot_filename,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "explanation": explanation
    }

# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
