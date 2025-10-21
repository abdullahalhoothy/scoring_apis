"""
Income Scoring Algorithm

Calculates location scores based on income levels and distribution.
Includes complete database integration for fetching income data.
"""

import asyncpg
from typing import Dict, Any, List


FETCH_INCOME_DATA_QUERY = """
    SELECT 
        income,
        geometry,
        low_income_score,
        medium_income_score,
        high_income_score,
        ST_Distance(geometry::geography, ST_MakePoint($2, $1)::geography) as distance
    FROM schema_marketplace.area_income_all_features_v12
    WHERE ST_DWithin(
        geometry::geography,
        ST_MakePoint($2, $1)::geography,
        $3
    )
    ORDER BY distance
    LIMIT 1000;
"""


async def fetch_income_data_from_db(
    database_url: str,
    lat: float,
    lng: float,
    radius: int
) -> List[Dict[str, Any]]:
    """Fetch income data from PostgreSQL database"""
    
    conn = await asyncpg.connect(database_url)
    try:
        rows = await conn.fetch(FETCH_INCOME_DATA_QUERY, lat, lng, radius)
        # Convert Record objects to dictionaries
        results = [dict(row) for row in rows]
        return results
    finally:
        await conn.close()


async def calculate_income_score(
    database_url: str,
    lat: float,
    lng: float,
    radius: int,
    target_income_level: str
) -> Dict[str, Any]:
    """
    Complete income scoring with database integration.
    
    Args:
        database_url: PostgreSQL database connection URL
        lat: Latitude of the location
        lng: Longitude of the location
        radius: Search radius in meters
        target_income_level: Target income category ("low", "medium", or "high")
    
    Returns:
        Dictionary containing income score and detailed breakdown
    """
    
    # Fetch income data from database
    results = await fetch_income_data_from_db(database_url, lat, lng, radius)
    
    # Calculate score from the data
    score_data = calculate_score_from_income_results(results, target_income_level)
    
    return score_data


def calculate_score_from_income_results(
    results: List[Dict[str, Any]], target_income_level: str
) -> Dict[str, Any]:
    """
    Calculate income score from database results - returns the pre-calculated score
    
    Args:
        results: List of income data records from database
        target_income_level: Target income category ("low", "medium", or "high")
    
    Returns:
        Dictionary containing score and detailed breakdown
    """
    
    areas_analyzed = len(results)
    
    # Extract the appropriate score column based on target income level
    if target_income_level == "low":
        target_scores = [
            row["low_income_score"] 
            for row in results 
            if row.get("low_income_score") is not None
        ]
    elif target_income_level == "medium":
        target_scores = [
            row["medium_income_score"] 
            for row in results 
            if row.get("medium_income_score") is not None
        ]
    else:  # high
        target_scores = [
            row["high_income_score"] 
            for row in results 
            if row.get("high_income_score") is not None
        ]
    
    # Get the average score from the pre-calculated column
    final_score = sum(target_scores) / len(target_scores) if target_scores else 0
    
    # Calculate average income for context
    incomes = [row["income"] for row in results if row.get("income") is not None]
    avg_income = sum(incomes) / len(incomes) if incomes else 0
    
    # Calculate all distribution scores for context
    low_scores = [
        row["low_income_score"] 
        for row in results 
        if row.get("low_income_score") is not None
    ]
    medium_scores = [
        row["medium_income_score"] 
        for row in results 
        if row.get("medium_income_score") is not None
    ]
    high_scores = [
        row["high_income_score"] 
        for row in results 
        if row.get("high_income_score") is not None
    ]
    
    income_distribution = {
        "low_score": round(sum(low_scores) / len(low_scores), 2) if low_scores else 0.0,
        "medium_score": round(sum(medium_scores) / len(medium_scores), 2) if medium_scores else 0.0,
        "high_score": round(sum(high_scores) / len(high_scores), 2) if high_scores else 0.0
    }
    
    return {
        "score": round(final_score, 2),
        "target_income_level": target_income_level,
        "areas_analyzed": areas_analyzed,
        "avg_income": round(avg_income, 2),
        "income_distribution": income_distribution
    }
