from pydantic import BaseModel, Field
from typing import Dict


class ResDemographics(BaseModel):
    """Response model for demographics scoring API"""
    score: float = Field(..., description="Calculated demographics score")
    target_population: int = Field(..., description="Total target population found")
    weighted_median_age: float = Field(..., description="Weighted median age of the population")
    avg_density: float = Field(..., description="Average population density per KM2")
    age_proximity_factor: float = Field(..., description="How close median age is to target age (0-1)")
    density_factor: float = Field(..., description="Population density factor (0-1)")
    population_factor: float = Field(..., description="Population size factor (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of the score")


class ResCompetition(BaseModel):
    """Response model for competition scoring API"""
    score: float = Field(..., description="Calculated competition score")
    total_competitors: int = Field(..., description="Total number of competing businesses found")
    category_breakdown: Dict[str, int] = Field(..., description="Number of competitors per category")
    competition_density: float = Field(..., description="Competition density per 1000 area units")
    competition_factor: float = Field(..., description="Overall competition intensity factor (0-1)")
    category_factor: float = Field(..., description="Category distribution factor (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of the score")


class ResComplementary(BaseModel):
    """Response model for complementary business scoring API"""
    score: float = Field(..., description="Calculated complementary score")
    total_complementary: int = Field(..., description="Total number of complementary businesses found")
    category_breakdown: Dict[str, int] = Field(..., description="Number of businesses per category")
    complementary_density: float = Field(..., description="Complementary business density per 1000 area units")
    density_factor: float = Field(..., description="Overall density factor (0-1)")
    coverage_factor: float = Field(..., description="Category coverage factor (0-1)")
    balance_factor: float = Field(..., description="Category balance factor (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of the score")


class ResIncome(BaseModel):
    """Response model for income scoring API"""
    score: float = Field(..., description="Calculated income score (0-100 based on percentile)")
    target_income_level: str = Field(..., description="Target income level used for calculation")
    areas_analyzed: int = Field(..., description="Number of areas analyzed within radius")
    avg_income: float = Field(..., description="Average income in the analyzed area")
    income_distribution: Dict[str, float] = Field(..., description="Income distribution breakdown (low/medium/high scores)")