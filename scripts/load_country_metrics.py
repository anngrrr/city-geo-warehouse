from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from src.models.country_etl import CountryDataETL

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    source_path = Path("data/processed/country_metrics.csv")
    etl = CountryDataETL(database_url=database_url, source_path=source_path)
    etl.run()


if __name__ == "__main__":
    main()
