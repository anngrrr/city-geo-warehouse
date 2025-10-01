from typing import List

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_required_fields(df: pd.DataFrame, required_fields: List[str]) -> None:
    """Validate that all required fields are present in the dataframe."""
    missing = [field for field in required_fields if field not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def validate_data_ranges(df: pd.DataFrame) -> None:
    """Validate data ranges for different types of fields."""
    bounded_columns = {
        "happiness_index": (0, 100),
        "health_index": (0, 100),
        "traffic_congestion_score": (0, 100),
        "education_level_score": (0, 100),
        "cultural_events_per_capita": (0, 100),
        "sports_facilities_per_capita": (0, 100),
        "forest_proximity_score": (0, 100),
        "green_space_ratio": (0, 100),
        "humidity": (0, 100),
        "cost_of_living_index": (0, 100),
        "housing_price_index": (0, 100),
        "air_quality_index": (0, 500),
        "digital_economy_score": (0, 100),
        "higher_education_score": (0, 100),
        "life_satisfaction_score": (0, 10),
        "cultural_resources_index": (0, 100),
        "forest_area_percent": (0, 100),
    }

    for column, (lower, upper) in bounded_columns.items():
        if column in df.columns and df[column].notna().any():
            invalid = df[df[column].notna() & ~df[column].between(lower, upper)]
            if not invalid.empty:
                raise ValueError(
                    f"Values in {column} must be between {lower} and {upper}. "
                    f"Found invalid values in rows: {invalid.index.tolist()}"
                )

    positive_columns = {
        "population",
        "distance_to_water",
        "distance_to_mountains",
        "distance_to_forest",
        "distance_to_park",
        "wind_speed_avg",
        "average_salary",
        "rent_price_index",
        "employee_income_index",
        "consumer_price_index",
        "rent_expenditure_percent_gdp",
        "house_price_to_income_ratio",
        "sports_expenditure_percent_gdp",
        "road_traffic_mortality_rate",
        "life_expectancy_years",
    }

    for column in positive_columns:
        if column in df.columns and df[column].notna().any():
            invalid = df[df[column].notna() & (df[column] < 0)]
            if not invalid.empty:
                raise ValueError(
                    f"Values in {column} must be non-negative. "
                    f"Found invalid values in rows: {invalid.index.tolist()}"
                )

    if "latitude" in df.columns:
        invalid = df[df["latitude"].notna() & ~df["latitude"].between(-90, 90)]
        if not invalid.empty:
            raise ValueError(
                f"Latitude must be between -90 and 90. Found invalid values in rows: {invalid.index.tolist()}"
            )

    if "longitude" in df.columns:
        invalid = df[df["longitude"].notna() & ~df["longitude"].between(-180, 180)]
        if not invalid.empty:
            raise ValueError(
                f"Longitude must be between -180 and 180. Found invalid values in rows: {invalid.index.tolist()}"
            )


def log_data_quality_metrics(df: pd.DataFrame) -> None:
    """Log data quality metrics for monitoring."""
    total_records = len(df)
    if total_records == 0:
        logger.info("No records to analyse for data quality")
        return

    logger.info("Total records processed: %s", total_records)

    for column in df.columns:
        completeness = (df[column].notna().sum() / total_records) * 100
        logger.info("Column %s completeness: %.2f%%", column, completeness)

    stats_columns = [
        "happiness_index",
        "health_index",
        "traffic_congestion_score",
        "education_level_score",
        "forest_proximity_score",
        "green_space_ratio",
        "digital_economy_score",
        "higher_education_score",
        "life_satisfaction_score",
        "cultural_resources_index",
        "forest_area_percent",
    ]

    for column in stats_columns:
        if column in df.columns and df[column].notna().any():
            logger.info(
                "%s stats: min=%.2f, max=%.2f, mean=%.2f",
                column,
                df[column].min(),
                df[column].max(),
                df[column].mean(),
            )
