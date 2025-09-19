from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CountryMetrics(BaseModel):
    """Normalized socio-economic metrics aggregated at country level."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda value: value.isoformat()},
        populate_by_name=True,
        validate_assignment=True,
    )

    country_name: str = Field(..., min_length=1, max_length=120, description="Official country name")
    iso2: Optional[str] = Field(default=None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 code")
    iso3: Optional[str] = Field(default=None, min_length=3, max_length=3, description="ISO 3166-1 alpha-3 code")
    year: int = Field(..., ge=1900, le=2100, description="Observation year")

    employee_income_index: Optional[float] = Field(
        default=None,
        description="OECD employee compensation index (base depends on source)",
    )
    consumer_price_index: Optional[float] = Field(
        default=None,
        ge=0,
        description="Consumer price index (base depends on source)",
    )
    rent_expenditure_percent_gdp: Optional[float] = Field(
        default=None,
        ge=0,
        description="Government rent expenditure as percent of GDP",
    )
    house_price_to_income_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        description="House price-to-income ratio",
    )
    real_gdp_growth_rate: Optional[float] = Field(
        default=None,
        description="Real GDP annual growth rate in percent",
    )
    digital_economy_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Digital economy and technology composite score",
    )
    higher_education_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Higher education and training score",
    )
    life_satisfaction_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
        description="Life satisfaction score (0-10)",
    )
    cultural_resources_index: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Cultural resources availability index",
    )
    sports_expenditure_percent_gdp: Optional[float] = Field(
        default=None,
        ge=0,
        description="Government expenditure on sporting services as percent of GDP",
    )
    road_traffic_mortality_rate: Optional[float] = Field(
        default=None,
        ge=0,
        description="Road traffic mortality per 100,000 population",
    )
    forest_area_percent: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Forest area as percentage of total land area",
    )
    life_expectancy_years: Optional[float] = Field(
        default=None,
        ge=0,
        description="Life expectancy at birth in years",
    )

    @classmethod
    def from_record(cls, data: dict) -> "CountryMetrics":
        """Instantiate model from a generic record."""
        return cls.model_validate(data, strict=False)
