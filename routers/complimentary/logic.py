import aiohttp
from typing import Dict, Any, List
from request_models import ReqComplementary
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Executing Complementary Score logic")


async def login_to_external_api() -> str:
    """Login to external API and get auth token"""

    login_payload = {
        "message": "string",
        "request_info": {"additionalProp1": {}},
        "request_body": {
            "email": "u_je_u2008@live.com",
            "password": "12351235",
        },
    }

    login_url = f"{CONF.external_api_base_url}/fastapi/login"

    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data["data"]["idToken"]


async def calculate_complementary_score(
    req: ReqComplementary,
) -> Dict[str, Any]:
    """Calculate complementary business score based on location and business categories"""

    # Login to get auth token
    auth_token = await login_to_external_api()

    # Fetch complementary business data from external API
    complementary_data = await fetch_complementary_data_from_external_api(
        req.lat,
        req.lng,
        req.radius,
        req.complementary_business_categories,
        auth_token,
    )

    # Calculate complementary score with detailed breakdown
    score_data = calculate_score_from_complementary_data(
        complementary_data, req.target_num_per_category
    )

    return score_data


async def fetch_complementary_data_from_external_api(
    lat: float, lng: float, radius: int, categories: List[str], auth_token: str
) -> List[Dict]:
    """Fetch complementary business data from external API at 37.27.195.216"""

    # Prepare request payload with simplified structure
    request_body = {
        "message": "string",
        "request_info": {"additionalProp1": {}},
        "request_body": {
            "lat": lat,
            "lng": lng,
            "user_id": "JnaGDCKoSoWtj6NWEVW8MDMBCiA2",
            "boolean_query": " OR ".join(categories),
            "action": "sample",
            "search_type": "category_search",
            "radius":radius
        },
    }

    # Make API call to external service with auth header
    url = f"{CONF.external_api_base_url}/fastapi/fetch_dataset"
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=request_body, headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()

            # Extract business data from response
            businesses = data.get("data", {}).get("features",[])
            return businesses


def calculate_score_from_complementary_data(
    complementary_data: List[Dict], target_num_per_category: int
) -> Dict[str, Any]:
    """Calculate complementary score from external API data with detailed breakdown"""

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
    # Higher score means more complementary businesses available
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

    # Complementary density factor
    complementary_density = total_complementary / 1000  # Normalize by area
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

    explanation = f"Score {round(final_score, 4)} based on {total_complementary} complementary businesses. {density_quality} density, {coverage_quality} category coverage ({target_categories} categories), {balance_quality} distribution. Top categories: {top_cat_desc}"

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


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
