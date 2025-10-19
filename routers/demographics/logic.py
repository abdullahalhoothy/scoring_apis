import math
from typing import Dict, Any
from database import Database
from request_models import ReqDemographics
from sql_object import SqlObject
from logging_wrapper import apply_decorator_to_module

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Database module loaded successfully")


async def calculate_demographics_score(req: ReqDemographics) -> Dict[str, Any]:
    """Calculate demographics score based on location and target age"""

    # Query population data from database
    results = await Database.fetch(
        SqlObject.fetch_population_data_query, req.lat, req.lng, req.radius
    )

    # Calculate demographics score with detailed breakdown
    score_data = calculate_score_from_results(
        results, req.target_age, req.sex_preference
    )

    return score_data


def calculate_score_from_results(
    results: list, target_age: int, sex_preference: str = None
) -> Dict[str, Any]:
    """Calculate demographics score from database results with detailed breakdown"""

    # Calculate population metrics based on sex preference
    if sex_preference == "male":
        target_population = sum(
            (row["Male_Population"] or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row["Median_Age_Male"] or 0) * (row["Male_Population"] or 0)
                for row in results
            )
            / target_population
        )
        sex_desc = "male population"
    elif sex_preference == "female":
        target_population = sum(
            (row["Female_Population"] or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row["Median_Age_Female"] or 0)
                * (row["Female_Population"] or 0)
                for row in results
            )
            / target_population
        )
        sex_desc = "female population"
    else:
        # No sex preference - use total population
        target_population = sum(
            (row["Population_Count"] or 0) for row in results
        )
        weighted_median_age = (
            sum(
                (row["Median_Age_Total"] or 0) * (row["Population_Count"] or 0)
                for row in results
            )
            / target_population
        )
        sex_desc = "total population"

    avg_density = sum(
        (row["Population_Density_KM2"] or 0) for row in results
    ) / len(results)

    # Age proximity factor (how close the median age is to target age)
    age_diff = abs(weighted_median_age - target_age)
    age_proximity_factor = max(0, 1 - (age_diff / 30))

    # Population density factor
    density_factor = min(1.0, avg_density / 1000)

    # Population size factor (using target population based on sex preference)
    population_factor = min(1.0, math.log10(target_population + 1) / 6)

    # Combine factors
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

    explanation = f"Score {round(final_score, 4)} based on {sex_desc}: {age_quality} age match (median {round(weighted_median_age, 1)} vs target {target_age}), {density_quality} density ({round(avg_density, 1)}/km²), {size_quality} population size ({target_population:,} people)"

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


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
