"""
Demographics Scoring Algorithm

Calculates location scores based on population demographics, age distribution, and density.
Includes complete database integration for fetching population data.
"""

import asyncpg
import math
from typing import Dict, Any, List, Optional


FETCH_POPULATION_DATA_QUERY = """
    SELECT 
        "Main_ID",
        "Grid_ID", 
        "Level",
        "Population_Count",
        "Male_Population",
        "Female_Population", 
        "Population_Density_KM2",
        "Median_Age_Total",
        "Median_Age_Male",
        "Median_Age_Female",
        density,
        geometry,
        ST_Distance(geometry::geography, ST_MakePoint($2, $1)::geography) as distance
    FROM schema_marketplace.population_all_features_v12
    WHERE ST_DWithin(
        geometry::geography,
        ST_MakePoint($2, $1)::geography,
        $3
    )
    ORDER BY distance
    LIMIT 1000;
"""


async def fetch_population_data_from_db(
    database_url: str,
    lat: float,
    lng: float,
    radius: int
) -> List[Dict[str, Any]]:
    """Fetch population data from PostgreSQL database"""
    
    conn = await asyncpg.connect(database_url)
    try:
        rows = await conn.fetch(FETCH_POPULATION_DATA_QUERY, lat, lng, radius)
        # Convert Record objects to dictionaries
        results = [dict(row) for row in rows]
        return results
    finally:
        await conn.close()


async def calculate_demographics_score(
    database_url: str,
    lat: float,
    lng: float,
    radius: int,
    target_age: int,
    sex_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete demographics scoring with database integration.
    
    Args:
        database_url: PostgreSQL database connection URL
        lat: Latitude of the location
        lng: Longitude of the location
        radius: Search radius in meters
        target_age: Target age for the analysis
        sex_preference: Optional sex preference ("male", "female", or None for total)
    
    Returns:
        Dictionary containing demographics score and detailed breakdown
    """
    
    # Fetch population data from database
    results = await fetch_population_data_from_db(database_url, lat, lng, radius)
    
    # Calculate score from the data
    score_data = calculate_score_from_demographics_results(
        results, target_age, sex_preference
    )
    
    return score_data


def calculate_score_from_demographics_results(
    results: List[Dict[str, Any]], 
    target_age: int, 
    sex_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate demographics score from database results with detailed breakdown
    
    Args:
        results: List of population data records from database
        target_age: Target age for the analysis
        sex_preference: Optional sex preference ("male", "female", or None for total)
    
    Returns:
        Dictionary containing score and detailed demographic breakdown
    """
    
    # Calculate population metrics based on sex preference
    if sex_preference == "male":
        target_population = sum(
            (row.get("Male_Population") or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row.get("Median_Age_Male") or 0) * (row.get("Male_Population") or 0)
                for row in results
            )
            / target_population
            if target_population > 0
            else 0
        )
        sex_desc = "male population"
    elif sex_preference == "female":
        target_population = sum(
            (row.get("Female_Population") or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row.get("Median_Age_Female") or 0)
                * (row.get("Female_Population") or 0)
                for row in results
            )
            / target_population
            if target_population > 0
            else 0
        )
        sex_desc = "female population"
    else:
        # No sex preference - use total population
        target_population = sum(
            (row.get("Population_Count") or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row.get("Median_Age_Total") or 0) * (row.get("Population_Count") or 0)
                for row in results
            )
            / target_population
            if target_population > 0
            else 0
        )
        sex_desc = "total population"

    avg_density = (
        sum((row.get("Population_Density_KM2") or 0) for row in results) / len(results)
        if results
        else 0
    )

    # Age proximity factor (how close the median age is to target age)
    age_diff = abs(weighted_median_age - target_age)
    age_proximity_factor = max(0, 1 - (age_diff / 30))

    # Population density factor
    density_factor = min(1.0, avg_density / 1000)

    # Population size factor (using target population based on sex preference)
    population_factor = min(1.0, math.log10(target_population + 1) / 6)

    # Combine factors with weights
    final_score = (
        age_proximity_factor * 0.5  # 50% weight for age proximity
        + density_factor * 0.3  # 30% weight for population density
        + population_factor * 0.2  # 20% weight for population size
    ) * 100

    # Generate explanation
    age_quality = (
        "excellent"
        if age_proximity_factor > 0.8
        else (
            "good"
            if age_proximity_factor > 0.6
            else "moderate" if age_proximity_factor > 0.3 else "poor"
        )
    )
    density_quality = (
        "high"
        if density_factor > 0.7
        else "moderate" if density_factor > 0.4 else "low"
    )
    size_quality = (
        "large"
        if population_factor > 0.7
        else "medium" if population_factor > 0.4 else "small"
    )

    explanation = (
        f"Score {round(final_score, 4)} based on {sex_desc}: {age_quality} age match "
        f"(median {round(weighted_median_age, 1)} vs target {target_age}), "
        f"{density_quality} density ({round(avg_density, 1)}/km²), "
        f"{size_quality} population size ({target_population:,} people)"
    )

    return {
        "score": round(final_score, 4),
        "target_population": int(target_population),
        "weighted_median_age": round(weighted_median_age, 2),
        "avg_density": round(avg_density, 2),
        "age_proximity_factor": round(age_proximity_factor, 4),
        "density_factor": round(density_factor, 4),
        "population_factor": round(population_factor, 4),
        "explanation": explanation,
    }
