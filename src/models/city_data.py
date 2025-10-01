from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CityMetrics(BaseModel):
    """Normalized city metrics model for Pydantic v2."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda value: value.isoformat()},
        populate_by_name=True,
        validate_assignment=True,
    )

    # Basic information
    city_name: str = Field(..., min_length=1, max_length=100, description="City name")
    country: str = Field(..., min_length=1, max_length=100, description="Country")
    timestamp: datetime = Field(default_factory=_utcnow, description="Data collection timestamp")
    population: Optional[int] = Field(default=None, ge=0, description="Population size")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude")
    region: Optional[str] = Field(default=None, description="Region or state")
    elevation: Optional[float] = Field(default=None, description="Elevation above sea level (m)")
    timezone: Optional[str] = Field(default=None, description="Timezone identifier")

    # Quality of life and economy
    happiness_index: Optional[float] = Field(default=None, ge=0, le=100, description="Happiness index")
    health_index: Optional[float] = Field(default=None, ge=0, le=100, description="Healthcare index")
    cost_of_living_index: Optional[float] = Field(default=None, ge=0, le=100, description="Cost of living index")
    housing_price_index: Optional[float] = Field(default=None, ge=0, le=100, description="Housing price index")
    traffic_congestion_score: Optional[float] = Field(default=None, ge=0, le=100, description="Traffic congestion score")
    education_level_score: Optional[float] = Field(default=None, ge=0, le=100, description="Education score")
    cultural_events_per_capita: Optional[float] = Field(default=None, ge=0, le=100, description="Cultural events per capita")
    sports_facilities_per_capita: Optional[float] = Field(default=None, ge=0, le=100, description="Sports facilities per capita")
    economic_growth_rate: Optional[float] = Field(default=None, description="Economic growth rate (%)")
    average_salary: Optional[float] = Field(default=None, ge=0, description="Average salary (USD)")
    rent_price_index: Optional[float] = Field(default=None, ge=0, description="Rent price index")

    # Environment
    wind_speed_avg: Optional[float] = Field(default=None, ge=0, description="Average wind speed (m/s)")
    air_quality_index: Optional[int] = Field(default=None, ge=1, le=5, description="Air quality index (1-5)")
    temperature: Optional[float] = Field(default=None, description="Temperature (C)")
    humidity: Optional[float] = Field(default=None, ge=0, le=100, description="Humidity (%)")

    # Natural features
    distance_to_water: Optional[float] = Field(default=None, ge=0, description="Distance to nearest water body (km)")
    distance_to_mountains: Optional[float] = Field(default=None, ge=0, description="Distance to mountains (km)")
    distance_to_forest: Optional[float] = Field(default=None, ge=0, description="Distance to forest (km)")
    distance_to_park: Optional[float] = Field(default=None, ge=0, description="Distance to park (km)")
    forest_proximity_score: Optional[float] = Field(default=None, ge=0, le=100, description="Forest proximity score")
    green_space_ratio: Optional[float] = Field(default=None, ge=0, le=100, description="Green space ratio (%)")

    @classmethod
    def from_api_data(cls, data: dict) -> "CityMetrics":
        """Build the model instance from raw API data."""
        return cls.model_validate(data, strict=False)
