from typing import Dict, Any
from database import Database
from request_models import ReqIncome
from sql_object import SqlObject
from logging_wrapper import apply_decorator_to_module

from app_logger import get_logger

logger = get_logger(__name__)
logger.info("Database module loaded successfully")

async def calculate_income_score(req: ReqIncome) -> Dict[str, Any]:
    """Calculate income score based on location and target income level"""
    
    # Query income data from database
    results = await Database.fetch(SqlObject.fetch_income_data_query, req.lat, req.lng, req.radius)
    
    # Calculate income score with detailed breakdown
    score_data = calculate_score_from_income_results(results, req.target_income_level)
    
    return score_data


def calculate_score_from_income_results(results: list, target_income_level: str) -> Dict[str, Any]:
    """Calculate income score from database results - just return the pre-calculated score"""
    
    areas_analyzed = len(results)
    
    # Extract the appropriate score column based on target income level
    if target_income_level == "low":
        target_scores = [row["income_score_low"] for row in results if row["income_score_low"] is not None]
    elif target_income_level == "medium":
        target_scores = [row["income_score_medium"] for row in results if row["income_score_medium"] is not None]
    else:  # high
        target_scores = [row["income_score_high"] for row in results if row["income_score_high"] is not None]
    
    # Get the average score from the pre-calculated column
    final_score = sum(target_scores) / len(target_scores) if target_scores else 0
    
    # Calculate average income for context
    incomes = [row["income"] for row in results if row["income"] is not None]
    avg_income = sum(incomes) / len(incomes) if incomes else 0
    
    # Calculate all distribution scores for context
    low_scores = [row["income_score_low"] for row in results if row["income_score_low"] is not None]
    medium_scores = [row["income_score_medium"] for row in results if row["income_score_medium"] is not None]
    high_scores = [row["income_score_high"] for row in results if row["income_score_high"] is not None]
    
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

# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
