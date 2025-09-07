from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CityMetrics(BaseModel):
    city_name: str
    country: str
    timestamp: datetime
    
    # Education and Culture
    english_proficiency_score: Optional[float]
    lgbt_acceptance_score: Optional[float]
    cultural_events_per_capita: Optional[float]
    education_level_score: Optional[float]
    
    # Quality of Life
    happiness_index: Optional[float]
    sports_facilities_per_capita: Optional[float]
    health_index: Optional[float]
    noise_pollution_level: Optional[float]
    air_quality_index: Optional[float]
    water_quality_score: Optional[float]
    
    # Economic Indicators
    economic_growth_rate: Optional[float]
    cost_of_living_index: Optional[float]
    average_salary: Optional[float]
    housing_price_index: Optional[float]
    rent_price_index: Optional[float]
    
    # Environmental Factors
    wind_speed_avg: Optional[float]
    sunny_days_per_year: Optional[float]
    distance_to_water: Optional[float]
    distance_to_mountains: Optional[float]
    forest_proximity_score: Optional[float]
    green_space_ratio: Optional[float]
    traffic_congestion_score: Optional[float]

    class Config:
        from_attributes = True
