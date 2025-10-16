from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class ReqDemographics(BaseModel):
    """Request model for demographics scoring API"""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate") 
    radius: int = Field(..., description="Search radius in meters")
    target_age: int = Field(..., description="Target age for demographics analysis")
    sex_preference: Optional[Literal["male", "female"]] = Field(None, description="Optional sex preference filter")


class ReqCompetition(BaseModel):
    """Request model for competition scoring API"""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    radius: int = Field(..., description="Search radius in meters")
    competition_business_categories: List[str] = Field(..., description="List of business categories to analyze for competition")
    target_num_per_category: int = Field(..., description="Target number of businesses per category")


class ReqComplementary(BaseModel):
    """Request model for complementary business scoring API"""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    radius: int = Field(..., description="Search radius in meters")
    complementary_business_categories: List[str] = Field(..., description="List of complementary business categories")
    target_num_per_category: int = Field(..., description="Target number per category")


class ReqIncome(BaseModel):
    """Request model for income scoring API"""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    radius: int = Field(..., description="Search radius in meters")
    target_income_level: Literal["low", "medium", "high"] = Field(..., description="Target income level (low, medium, high)")