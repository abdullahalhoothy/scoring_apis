"""
Competition Scoring Algorithm

Calculates competition scores based on nearby competing businesses.
Includes complete API integration for fetching competition data.
"""

import aiohttp
from typing import Dict, Any, List


async def login_to_external_api(base_url: str) -> str:
    """Login to external API and get auth token"""
    
    login_payload = {
        "message": "string",
        "request_info": {"additionalProp1": {}},
        "request_body": {
            "email": "u_je_u2008@live.com",
            "password": "12351235",
        },
    }
    
    login_url = f"{base_url}/fastapi/login"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data["data"]["idToken"]


async def fetch_competition_data_from_api(
    base_url: str,
    lat: float,
    lng: float,
    radius: int,
    categories: List[str],
    auth_token: str
) -> List[Dict]:
    """Fetch competition data from external API"""
    
    request_body = {
        "message": "string",
        "request_info": {"additionalProp1": {}},
        "request_body": {
            "lat": lat,
            "lng": lng,
            "user_id": "JnaGDCKoSoWtj6NWEVW8MDMBCiA2",
            "boolean_query": " OR ".join(categories),
            "action": "sample",
            "radius": radius,
        },
    }
    
    url = f"{base_url}/fastapi/fetch_dataset"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_body, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            businesses = data.get("data", {}).get("features", [])
            return businesses


async def calculate_competition_score(
    base_url: str,
    lat: float,
    lng: float,
    radius: int,
    competition_business_categories: List[str],
    target_num_per_category: int
) -> Dict[str, Any]:
    """
    Complete competition scoring with API integration.
    
    Args:
        base_url: External API base URL
        lat: Latitude of the location
        lng: Longitude of the location
        radius: Search radius in meters
        competition_business_categories: List of business categories to check
        target_num_per_category: Target number of competitors per category
    
    Returns:
        Dictionary containing competition score and detailed breakdown
    """
    
    # Login to get auth token
    auth_token = await login_to_external_api(base_url)
    
    # Fetch competition data from external API
    competition_data = await fetch_competition_data_from_api(
        base_url, lat, lng, radius, competition_business_categories, auth_token
    )
    
    # Calculate score from the data
    score_data = calculate_score_from_competition_data(
        competition_data, target_num_per_category
    )
    
    return score_data


def calculate_score_from_competition_data(
    competition_data: List[Dict[str, Any]], 
    target_num_per_category: int
) -> Dict[str, Any]:
    """
    Calculate competition score from external API data with detailed breakdown
    
    Lower score means higher competition (more competitors).
    Higher score means lower competition (better for new business).
    
    Args:
        competition_data: List of competing businesses from external API
        target_num_per_category: Target number of competitors per category
    
    Returns:
        Dictionary containing competition score and detailed breakdown
    """
    
    total_competitors = len(competition_data)

    # Group by category to count competitors per category
    category_counts = {}
    for business in competition_data:
        category = (
            business.get("types", ["unknown"])[0]
            if business.get("types")
            else "unknown"
        )
        category_counts[category] = category_counts.get(category, 0) + 1

    # Calculate competition intensity
    if total_competitors == 0:
        return {
            "score": 100.0,
            "total_competitors": 0,
            "category_breakdown": {},
            "competition_density": 0.0,
            "competition_factor": 1.0,
            "category_factor": 1.0,
            "explanation": "Perfect score: No competitors found in the area",
        }

    # Competition density factor (normalized per 1000 unit area)
    competition_density = total_competitors / 1000
    competition_factor = max(0, 1 - (competition_density / 10))

    # Category distribution factor
    avg_per_category = (
        total_competitors / len(category_counts) if category_counts else 0
    )
    category_factor = max(0, 1 - (avg_per_category / target_num_per_category))

    # Combine factors (lower competition = higher score)
    final_score = (competition_factor * 0.7 + category_factor * 0.3) * 100

    # Generate explanation
    competition_level = (
        "low"
        if competition_factor > 0.7
        else "moderate" if competition_factor > 0.4 else "high"
    )
    category_distribution = (
        "well-distributed"
        if category_factor > 0.6
        else "concentrated" if category_factor > 0.3 else "oversaturated"
    )

    top_categories = sorted(
        category_counts.items(), key=lambda x: x[1], reverse=True
    )[:3]
    top_cat_desc = ", ".join(
        [f"{cat}: {count}" for cat, count in top_categories]
    )

    explanation = (
        f"Score {round(final_score, 4)} indicates {competition_level} competition "
        f"({total_competitors} competitors). Competition is {category_distribution} "
        f"across categories. Top categories: {top_cat_desc}"
    )

    return {
        "score": round(final_score, 4),
        "total_competitors": total_competitors,
        "category_breakdown": category_counts,
        "competition_density": round(competition_density, 4),
        "competition_factor": round(competition_factor, 4),
        "category_factor": round(category_factor, 4),
        "explanation": explanation,
    }
