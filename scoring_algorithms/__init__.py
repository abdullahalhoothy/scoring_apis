"""
Scoring Algorithms Package

A reusable package containing all scoring calculation logic for location-based business analysis.
This package can be installed on multiple servers to ensure consistent scoring across systems.

All modules include complete integration (API calls, database queries) - no external dependencies needed.

Version: 1.0.0
"""

from .income import calculate_income_score
from .demographics import calculate_demographics_score
from .traffic import calculate_traffic_score, format_traffic_results
from .competition import calculate_competition_score
from .complementary import calculate_complementary_score

__version__ = "1.0.0"

__all__ = [
    "calculate_income_score",
    "calculate_demographics_score",
    "calculate_traffic_score",
    "format_traffic_results",
    "calculate_competition_score",
    "calculate_complementary_score",
]
