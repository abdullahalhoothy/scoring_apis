import aiohttp
from typing import Dict, Any, List
from request_models import ReqCompetition
from config_factory import CONF
from logging_wrapper import apply_decorator_to_module

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Executing Competition Score logic")


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


async def calculate_competition_score(req: ReqCompetition) -> Dict[str, Any]:
    """Calculate competition score based on location and business categories"""

    # Login to get auth token
    auth_token = await login_to_external_api()

    # Fetch competition data from external API
    competition_data = await fetch_competition_data_from_external_api(
        req.lat,
        req.lng,
        req.radius,
        req.competition_business_categories,
        auth_token,
    )

    # Calculate competition score with detailed breakdown
    score_data = calculate_score_from_competition_data(
        competition_data, req.target_num_per_category
    )

    return score_data


async def fetch_competition_data_from_external_api(
    lat: float, lng: float, radius: int, categories: List[str], auth_token: str
) -> List[Dict]:
    """Fetch competition data from external API at 37.27.195.216"""

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
            businesses = data.get("data", {}).get("features", [])
            return businesses


def calculate_score_from_competition_data(
    competition_data: List[Dict], target_num_per_category: int
) -> Dict[str, Any]:
    """Calculate competition score from external API data with detailed breakdown"""

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
    # Lower score means higher competition (more competitors)
    if total_competitors == 0:
        return {
            "score": 1.0,
            "total_competitors": 0,
            "category_breakdown": {},
            "competition_density": 0.0,
            "competition_factor": 1.0,
            "category_factor": 1.0,
            "explanation": "Perfect score: No competitors found in the area",
        }

    # Competition density factor
    competition_density = total_competitors / 1000  # Normalize by area
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

    explanation = f"Score {round(final_score, 4)} indicates {competition_level} competition ({total_competitors} competitors). Competition is {category_distribution} across categories. Top categories: {top_cat_desc}"

    return {
        "score": round(final_score, 4),
        "total_competitors": total_competitors,
        "category_breakdown": category_counts,
        "competition_density": round(competition_density, 4),
        "competition_factor": round(competition_factor, 4),
        "category_factor": round(category_factor, 4),
        "explanation": explanation,
    }


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
