"""
Traffic Scoring Algorithm

Complete traffic analysis including external API calls and result formatting.
This module can be used standalone on any server - just call calculate_traffic_score().
"""

import aiohttp
import asyncio
from typing import Dict, Any
from datetime import datetime


async def calculate_traffic_score(
    lat: float,
    lng: float,
    storefront_direction: str,
    day: str,
    time: str,
    traffic_api_base_url: str,
    username: str = "admin",
    password: str = "123456"
) -> Dict[str, Any]:
    """
    Complete traffic score calculation including API calls.
    Other servers can call this single function to get traffic scores.
    
    Args:
        lat: Latitude
        lng: Longitude
        storefront_direction: Direction storefront faces ("north", "south", etc.)
        day: Day of week for analysis
        time: Time of day for analysis
        traffic_api_base_url: Base URL of traffic API
        username: API username (default: "admin")
        password: API password (default: "123456")
    
    Returns:
        Dictionary containing traffic scores and analysis
    """
    
    # Login to get auth token
    auth_token = await login_to_traffic_api(traffic_api_base_url, username, password)
    
    # Submit traffic analysis job
    job_id = await submit_traffic_job(
        lat, lng, storefront_direction, day, time,
        traffic_api_base_url, auth_token
    )
    
    # Poll for results
    job_result = await poll_job_status(job_id, traffic_api_base_url, auth_token)
    
    # Format and return results
    score_data = format_traffic_results(job_result, storefront_direction, day, time)
    
    return score_data


async def login_to_traffic_api(
    base_url: str,
    username: str = "admin",
    password: str = "123456"
) -> str:
    """Login to traffic API and get auth token"""
    
    login_url = f"{base_url}/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, data=login_data) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data["access_token"]


async def submit_traffic_job(
    lat: float,
    lng: float,
    storefront_direction: str,
    day: str,
    time: str,
    base_url: str,
    token: str
) -> str:
    """Submit traffic analysis job"""
    
    analyze_url = f"{base_url}/analyze-traffic"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "locations": [
            {
                "lat": lat,
                "lng": lng,
                "storefront_direction": storefront_direction,
                "day": day,
                "time": time,
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(analyze_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            result = await response.json()
            return result["job_id"]


async def poll_job_status(
    job_id: str,
    base_url: str,
    token: str,
    max_attempts: int = 60,
    poll_interval: int = 5
) -> Dict[str, Any]:
    """
    Poll job status until completion
    
    Args:
        job_id: Job ID to poll
        base_url: Base URL of traffic API
        token: Auth token
        max_attempts: Maximum polling attempts (default: 60)
        poll_interval: Seconds between polls (default: 5)
    
    Returns:
        Job result data
    
    Raises:
        Exception: If job fails, is canceled, or times out
    """
    
    status_url = f"{base_url}/job/{job_id}"
    headers = {"Authorization": f"Bearer {token}"}
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
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
                    await asyncio.sleep(poll_interval)
                else:
                    await asyncio.sleep(poll_interval)
    
    raise Exception(f"Traffic analysis job {job_id} timed out after {max_attempts} attempts")


def format_traffic_results(
    job_result: Dict[str, Any], 
    storefront_direction: str,
    day: str,
    time: str
) -> Dict[str, Any]:
    """
    Format traffic analysis results into a standardized score
    
    Args:
        job_result: Raw traffic analysis job result from external API
        storefront_direction: Direction the storefront faces (e.g., "north", "south")
        day: Day of the week for the analysis
        time: Time of day for the analysis
    
    Returns:
        Dictionary containing formatted traffic scores and analysis
    """
    
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
    score_quality = (
        "excellent" if traffic_score >= 80 
        else "good" if traffic_score >= 60 
        else "moderate" if traffic_score >= 40 
        else "below average" if traffic_score >= 20 
        else "poor"
    )
    storefront_quality = (
        "high" if storefront_score >= 70 
        else "moderate" if storefront_score >= 40 
        else "low"
    )
    area_quality = (
        "busy" if area_score >= 70 
        else "moderate" if area_score >= 40 
        else "quiet"
    )
    
    explanation = (
        f"Overall traffic score {traffic_score} indicates {score_quality} traffic conditions. "
        f"Storefront visibility: {storefront_quality} ({storefront_score}), "
        f"Area activity: {area_quality} ({area_score}). "
        f"Analysis for {storefront_direction}-facing storefront on {day} at {time}"
    )
    
    return {
        "score": traffic_score,
        "storefront_score": storefront_score,
        "area_score": area_score,
        "screenshot_filename": screenshot_filename,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "explanation": explanation
    }
