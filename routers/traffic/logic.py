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
    
    logger.info(f"Starting traffic score calculation for location: lat={req.lat}, lng={req.lng}, direction={req.storefront_direction}, day={req.day}, time={req.time}")
    
    # Login to get auth token
    logger.info("Attempting to login to traffic API")
    auth_token = await login_to_traffic_api()
    logger.info("Successfully obtained auth token")
    
    # Submit traffic analysis job
    logger.info(f"Submitting traffic analysis job for location: {req.lat}, {req.lng}")
    job_id = await submit_traffic_job(req, auth_token)
    logger.info(f"Traffic analysis job submitted successfully with job_id: {job_id}")
    
    # Poll for results
    logger.info(f"Starting to poll for job status: {job_id}")
    job_result = await poll_job_status(job_id, auth_token)
    logger.info(f"Job completed. Full job result: {job_result}")
    
    # Extract and format results
    logger.info("Formatting traffic results")
    score_data = format_traffic_results(job_result, req)
    logger.info(f"Final traffic score data: {score_data}")
    
    return score_data


async def login_to_traffic_api() -> str:
    """Login to traffic API and get auth token"""
    
    login_url = f"{CONF.traffic_api_base_url}/login"
    login_data = {
        "username": "admin",  # Default from the example
        "password": "123456"  # Default from the example
    }
    
    logger.info(f"Sending login request to: {login_url}")
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, data=login_data) as response:
            logger.info(f"Login response status: {response.status}")
            response.raise_for_status()
            token_data = await response.json()
            logger.info(f"Login successful, token received: {token_data.get('access_token', '')[:20]}...")
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
    
    logger.info(f"Submitting job to: {analyze_url}")
    logger.info(f"Job payload: {payload}")
    async with aiohttp.ClientSession() as session:
        async with session.post(analyze_url, json=payload, headers=headers) as response:
            logger.info(f"Job submission response status: {response.status}")
            response.raise_for_status()
            result = await response.json()
            logger.info(f"Job submission response: {result}")
            return result["job_id"]


async def poll_job_status(job_id: str, token: str) -> Dict[str, Any]:
    """Poll job status until completion"""
    
    status_url = f"{CONF.traffic_api_base_url}/job/{job_id}"
    headers = {"Authorization": f"Bearer {token}"}
    max_attempts = 60  # 5 minutes with 5-second intervals
    attempt = 0
    
    logger.info(f"Starting polling for job {job_id} (max {max_attempts} attempts, 5 second intervals)")
    
    while attempt < max_attempts:
        attempt += 1
        logger.info(f"Polling attempt {attempt}/{max_attempts} for job {job_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(status_url, headers=headers) as response:
                logger.info(f"Poll response status: {response.status}")
                response.raise_for_status()
                job_data = await response.json()
                
                status = job_data.get("status")
                logger.info(f"Job {job_id} status: {status}")
                logger.debug(f"Full job data at attempt {attempt}: {job_data}")
                
                if status == "done":
                    logger.info(f"Job {job_id} completed successfully after {attempt} attempts")
                    logger.info(f"Job completion data: {job_data}")
                    return job_data
                elif status in ("failed", "canceled"):
                    error_msg = job_data.get("error", "Unknown error")
                    logger.error(f"Job {job_id} {status} after {attempt} attempts. Error: {error_msg}")
                    raise Exception(f"Traffic analysis job {status}: {error_msg}")
                elif status in ("pending", "running"):
                    logger.info(f"Job {job_id} still {status}, waiting 5 seconds before next poll (attempt {attempt}/{max_attempts})")
                    await asyncio.sleep(5)
                else:
                    logger.warning(f"Job {job_id} has unexpected status: {status}, waiting 5 seconds")
                    await asyncio.sleep(5)
    
    logger.error(f"Job {job_id} timed out after {max_attempts} attempts ({max_attempts * 5} seconds)")
    raise Exception(f"Traffic analysis job {job_id} timed out after {max_attempts} attempts")


def format_traffic_results(job_result: Dict[str, Any], req: ReqTraffic) -> Dict[str, Any]:
    """Format traffic analysis results"""
    
    logger.info("Starting to format traffic results")
    logger.info(f"Raw job_result keys: {job_result.keys()}")
    logger.info(f"Full job_result: {job_result}")
    
    results_data = job_result.get("result", {}).get("results", [])
    logger.info(f"Extracted results_data: {results_data}")
    logger.info(f"Number of results: {len(results_data) if results_data else 0}")
    
    if not results_data:
        logger.warning("No traffic analysis data available in job result")
        logger.warning(f"job_result structure: {job_result}")
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
    logger.info(f"Processing result index 0: {result}")
    
    if result.get("error"):
        logger.error(f"Result contains error: {result['error']}")
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
    
    logger.info(f"Extracted scores - traffic: {traffic_score}, storefront: {storefront_score}, area: {area_score}")
    logger.info(f"Screenshot URL: {screenshot_url}")
    logger.info(f"Screenshot filename: {screenshot_filename}")
    
    # Check if all scores are zero
    if traffic_score == 0 and storefront_score == 0 and area_score == 0:
        logger.warning("All scores are zero! This might indicate an issue.")
        logger.warning(f"Result keys available: {result.keys()}")
        logger.warning(f"Full result object: {result}")
    
    # Generate explanation
    score_quality = "excellent" if traffic_score >= 80 else "good" if traffic_score >= 60 else "moderate" if traffic_score >= 40 else "below average" if traffic_score >= 20 else "poor"
    storefront_quality = "high" if storefront_score >= 70 else "moderate" if storefront_score >= 40 else "low"
    area_quality = "busy" if area_score >= 70 else "moderate" if area_score >= 40 else "quiet"
    
    explanation = f"Overall traffic score {traffic_score} indicates {score_quality} traffic conditions. Storefront visibility: {storefront_quality} ({storefront_score}), Area activity: {area_quality} ({area_score}). Analysis for {req.storefront_direction}-facing storefront on {req.day} at {req.time}"
    
    logger.info(f"Generated explanation: {explanation}")
    
    formatted_result = {
        "score": traffic_score,
        "storefront_score": storefront_score,
        "area_score": area_score,
        "screenshot_filename": screenshot_filename,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "explanation": explanation
    }
    
    logger.info(f"Returning formatted result: {formatted_result}")
    return formatted_result

# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
