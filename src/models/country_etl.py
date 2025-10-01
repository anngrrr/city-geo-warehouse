from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, String, Table, UniqueConstraint, create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.models.country_data import CountryMetrics
from src.utils.validators import log_data_quality_metrics, validate_data_ranges, validate_required_fields

logger = logging.getLogger(__name__)


class CountryDataETL:
    """ETL pipeline that loads preprocessed country metrics into PostgreSQL."""

    IDENTIFIER_COLUMNS = ["country_code", "country_name", "year"]
    METRIC_COLUMNS = [
        "employee_income_index",
        "consumer_price_index",
        "rent_expenditure_percent_gdp",
        "house_price_to_income_ratio",
        "real_gdp_growth_rate",
        "digital_economy_score",
        "higher_education_score",
        "life_satisfaction_score",
        "cultural_resources_index",
        "sports_expenditure_percent_gdp",
        "road_traffic_mortality_rate",
        "forest_area_percent",
        "life_expectancy_years",
    ]

    def __init__(self, database_url: str, source_path: str | Path = "data/processed/country_metrics.csv") -> None:
        self.engine: Engine = create_engine(database_url, future=True)
        self.source_path = Path(source_path)
        self.metadata = MetaData(schema="country_data")
        self.country_metrics = Table(
            "country_metrics",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("country_code", String(10), nullable=False),
            Column("country_name", String(255), nullable=False),
            Column("iso2", String(2)),
            Column("iso3", String(3)),
            Column("year", Integer, nullable=False),
            Column("employee_income_index", Float),
            Column("consumer_price_index", Float),
            Column("rent_expenditure_percent_gdp", Float),
            Column("house_price_to_income_ratio", Float),
            Column("real_gdp_growth_rate", Float),
            Column("digital_economy_score", Float),
            Column("higher_education_score", Float),
            Column("life_satisfaction_score", Float),
            Column("cultural_resources_index", Float),
            Column("sports_expenditure_percent_gdp", Float),
            Column("road_traffic_mortality_rate", Float),
            Column("forest_area_percent", Float),
            Column("life_expectancy_years", Float),
            Column("created_at", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")),
            UniqueConstraint("country_code", "year", name="uq_country_year"),
        )

    def _ensure_schema_exists(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS country_data"))

    def extract(self) -> pd.DataFrame:
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_path}")
        return pd.read_csv(self.source_path)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        validate_required_fields(df, self.IDENTIFIER_COLUMNS)
        metric_columns = [col for col in df.columns if col not in self.IDENTIFIER_COLUMNS]
        df = df.dropna(subset=metric_columns, how="all")

        if df.empty:
            logger.warning("No country metrics available after dropping empty rows")
            return pd.DataFrame(columns=[field for field in CountryMetrics.model_fields])

        records: List[dict] = []
        for record in df.to_dict(orient="records"):
            payload = {**record}
            payload.setdefault("iso2", None)
            payload["iso3"] = payload.get("iso3") or payload["country_code"]
            for column in self.METRIC_COLUMNS:
                if pd.isna(payload.get(column)):
                    payload[column] = None
            model = CountryMetrics.from_record(payload)
            data = model.model_dump()
            data["country_code"] = payload["country_code"]
            records.append(data)

        transformed = pd.DataFrame(records)
        ordered_columns = ['country_code', 'country_name', 'iso2', 'iso3', 'year'] + self.METRIC_COLUMNS
        transformed = transformed.reindex(columns=ordered_columns)
        validate_data_ranges(transformed)
        log_data_quality_metrics(transformed)
        return transformed

    def load(self, df: pd.DataFrame) -> None:
        if df.empty:
            logger.info("Nothing to load: dataframe is empty")
            return

        self._ensure_schema_exists()
        self.metadata.create_all(self.engine)

        records = df.to_dict(orient="records")
        stmt = insert(self.country_metrics).values(records)
        update_columns = [
            column.name
            for column in self.country_metrics.columns
            if column.name not in {"id", "country_code", "year", "created_at"}
        ]
        stmt = stmt.on_conflict_do_update(
            index_elements=["country_code", "year"],
            set_={column: getattr(stmt.excluded, column) for column in update_columns},
        )

        try:
            with self.engine.begin() as connection:
                connection.execute(stmt)
            logger.info("Loaded %s rows into country_data.country_metrics", len(records))
        except SQLAlchemyError as exc:
            logger.error("Error loading country metrics: %s", exc)
            raise

    def run(self) -> pd.DataFrame:
        logger.info("Starting country metrics ETL")
        extracted = self.extract()
        transformed = self.transform(extracted)
        self.load(transformed)
        logger.info("Country metrics ETL finished (rows=%s)", len(transformed))
        return transformed


__all__ = ["CountryDataETL"]
