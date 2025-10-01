import logging
from typing import Iterable, List

import pandas as pd
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.models.city_data import CityMetrics
try:
    from src.models.city_data_collector import CityDataCollector
except ImportError:  # legacy pipeline not available
    CityDataCollector = None
from src.utils.validators import log_data_quality_metrics, validate_data_ranges, validate_required_fields

logger = logging.getLogger(__name__)


class CityDataETL:
    """ETL pipeline for collecting and loading city metrics."""

    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(database_url, future=True)
        if CityDataCollector is None:
            raise RuntimeError('CityDataCollector is not available. The city pipeline is deprecated.')
        self.collector = CityDataCollector()
        self.metadata = MetaData()
        self._ensure_schema_exists()

        self.city_metrics = Table(
            "city_metrics",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("city_name", String(255), nullable=False),
            Column("country", String(255), nullable=False),
            Column("timestamp", DateTime(timezone=True), nullable=False),
            Column("population", Integer),
            Column("latitude", Float),
            Column("longitude", Float),
            Column("region", String(255)),
            Column("elevation", Float),
            Column("timezone", String(100)),
            Column("happiness_index", Float),
            Column("health_index", Float),
            Column("cost_of_living_index", Float),
            Column("housing_price_index", Float),
            Column("traffic_congestion_score", Float),
            Column("education_level_score", Float),
            Column("cultural_events_per_capita", Float),
            Column("sports_facilities_per_capita", Float),
            Column("economic_growth_rate", Float),
            Column("average_salary", Float),
            Column("rent_price_index", Float),
            Column("wind_speed_avg", Float),
            Column("air_quality_index", Float),
            Column("temperature", Float),
            Column("humidity", Float),
            Column("distance_to_water", Float),
            Column("distance_to_mountains", Float),
            Column("distance_to_forest", Float),
            Column("distance_to_park", Float),
            Column("forest_proximity_score", Float),
            Column("green_space_ratio", Float),
            UniqueConstraint("city_name", "country", "timestamp", name="uq_city_country_timestamp"),
            CheckConstraint("air_quality_index >= 0", name="ck_air_quality_index_positive"),
            CheckConstraint("humidity BETWEEN 0 AND 100", name="ck_humidity_range"),
            CheckConstraint("traffic_congestion_score BETWEEN 0 AND 100", name="ck_traffic_range"),
            CheckConstraint("forest_proximity_score BETWEEN 0 AND 100", name="ck_forest_score_range"),
            CheckConstraint("green_space_ratio BETWEEN 0 AND 100", name="ck_green_space_range"),
            schema="city_data",
        )

    def _ensure_schema_exists(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS city_data"))

    def extract(self, cities: Iterable[dict[str, str]]) -> List[CityMetrics]:
        city_data: List[CityMetrics] = []
        for city in cities:
            try:
                logger.info("Collecting data for %s, %s", city["name"], city["country"])
                raw = self.collector.collect_all_city_data(city["name"], city["country"])
                if not raw:
                    logger.warning("No data found for %s, %s", city["name"], city["country"])
                    continue
                city_data.append(CityMetrics.from_api_data(raw))
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to extract data for %s: %s", city.get("name"), exc)
        return city_data

    def transform(self, city_data: Iterable[CityMetrics]) -> pd.DataFrame:
        records = [item.model_dump(mode="python") for item in city_data]
        df = pd.DataFrame(records)
        if df.empty:
            logger.warning("DataFrame after transform is empty")
            return df

        validate_required_fields(df, ["city_name", "country", "timestamp"])
        validate_data_ranges(df)
        log_data_quality_metrics(df)
        return df

    def load(self, df: pd.DataFrame) -> None:
        if df.empty:
            logger.info("Nothing to load: DataFrame is empty")
            return

        records = df.to_dict(orient="records")
        stmt = insert(self.city_metrics).values(records)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["city_name", "country", "timestamp"],
            set_={
                column.name: getattr(stmt.excluded, column.name)
                for column in self.city_metrics.columns
                if column.name not in {"id", "city_name", "country", "timestamp"}
            },
        )

        try:
            with self.engine.begin() as connection:
                connection.execute(upsert_stmt)
            logger.info("Inserted/updated records: %s", len(records))
        except SQLAlchemyError as exc:
            logger.error("Database load failed: %s", exc)
            raise

    def run_etl(self, cities: Iterable[dict[str, str]]) -> pd.DataFrame:
        logger.info("Starting ETL pipeline")
        extracted = self.extract(cities)
        transformed = self.transform(extracted)
        self.load(transformed)
        logger.info("ETL pipeline finished")
        return transformed
