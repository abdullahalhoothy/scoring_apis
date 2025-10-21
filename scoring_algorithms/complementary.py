"""
Complementary Business Scoring Algorithm

Calculates scores based on nearby complementary businesses that can drive traffic.
Includes complete API integration for fetching complementary data.
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


async def fetch_complementary_data_from_api(
    base_url: str,
    lat: float,
    lng: float,
    radius: int,
    categories: List[str],
    auth_token: str
) -> List[Dict]:
    """Fetch complementary business data from external API"""
    
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


async def calculate_complementary_score(
    base_url: str,
    lat: float,
    lng: float,
    radius: int,
    complementary_business_categories: List[str],
    target_num_per_category: int
) -> Dict[str, Any]:
    """
    Complete complementary scoring with API integration.
    
    Args:
        base_url: External API base URL
        lat: Latitude of the location
        lng: Longitude of the location
        radius: Search radius in meters
        complementary_business_categories: List of complementary business categories
        target_num_per_category: Target number of businesses per category
    
    Returns:
        Dictionary containing complementary score and detailed breakdown
    """
    
    # Login to get auth token
    auth_token = await login_to_external_api(base_url)
    
    # Fetch complementary data from external API
    complementary_data = await fetch_complementary_data_from_api(
        base_url, lat, lng, radius, complementary_business_categories, auth_token
    )
    
    # Calculate score from the data
    score_data = calculate_score_from_complementary_data(
        complementary_data, target_num_per_category
    )
    
    return score_data


def calculate_score_from_complementary_data(
    complementary_data: List[Dict[str, Any]], 
    target_num_per_category: int
) -> Dict[str, Any]:
    """
    Calculate complementary score from external API data with detailed breakdown
    
    Higher score means more complementary businesses available (better for new business).
    
    Args:
        complementary_data: List of complementary businesses from external API
        target_num_per_category: Target number of complementary businesses per category
    
    Returns:
        Dictionary containing complementary score and detailed breakdown
    """
    
    total_complementary = len(complementary_data)

    # Group by category to count complementary businesses per category
    category_counts = {}
    for business in complementary_data:
        category = (
            business.get("types", ["unknown"])[0]
            if business.get("types")
            else "unknown"
        )
        category_counts[category] = category_counts.get(category, 0) + 1

    # Calculate complementary business availability
    if total_complementary == 0:
        return {
            "score": 0.0,
            "total_complementary": 0,
            "category_breakdown": {},
            "complementary_density": 0.0,
            "density_factor": 0.0,
            "coverage_factor": 0.0,
            "balance_factor": 0.0,
            "explanation": "Low score: No complementary businesses found in the area",
        }

    # Complementary density factor (normalized per 1000 unit area)
    complementary_density = total_complementary / 1000
    density_factor = min(1.0, complementary_density / 5)

    # Category coverage factor (how well categories are covered)
    target_categories = len(category_counts)
    coverage_factor = min(
        1.0, target_categories / 5
    )  # Assuming 5 is ideal category coverage

    # Category balance factor (how evenly distributed the businesses are)
    if target_categories > 0:
        avg_per_category = total_complementary / target_categories
        balance_factor = min(1.0, avg_per_category / target_num_per_category)
    else:
        balance_factor = 0

    # Combine factors (more complementary businesses = higher score)
    final_score = (
        density_factor * 0.4  # 40% weight for overall density
        + coverage_factor * 0.3  # 30% weight for category coverage
        + balance_factor * 0.3  # 30% weight for category balance
    ) * 100

    # Generate explanation
    density_quality = (
        "high"
        if density_factor > 0.7
        else "moderate" if density_factor > 0.4 else "low"
    )
    coverage_quality = (
        "excellent"
        if coverage_factor > 0.8
        else "good" if coverage_factor > 0.6 else "limited"
    )
    balance_quality = (
        "well-balanced"
        if balance_factor > 0.7
        else "adequate" if balance_factor > 0.4 else "uneven"
    )

    top_categories = sorted(
        category_counts.items(), key=lambda x: x[1], reverse=True
    )[:3]
    top_cat_desc = ", ".join(
        [f"{cat}: {count}" for cat, count in top_categories]
    )

    explanation = (
        f"Score {round(final_score, 4)} based on {total_complementary} complementary businesses. "
        f"{density_quality} density, {coverage_quality} category coverage ({target_categories} categories), "
        f"{balance_quality} distribution. Top categories: {top_cat_desc}"
    )

    return {
        "score": round(final_score, 4),
        "total_complementary": total_complementary,
        "category_breakdown": category_counts,
        "complementary_density": round(complementary_density, 4),
        "density_factor": round(density_factor, 4),
        "coverage_factor": round(coverage_factor, 4),
        "balance_factor": round(balance_factor, 4),
        "explanation": explanation,
    }
