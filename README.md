# City Geo Warehouse

An ETL playground for socio-economic metrics. The current focus is on **country-level** indicators compiled from public datasets (OECD, IMF, UNCTAD, World Bank, WEF). Legacy city code is archived; running it by accident now raises a clear error.

## Directory Layout

`
.
+-- data/
¦   +-- raw/         # original CSV dumps
¦   +-- processed/   # normalized datasets (e.g. country_metrics.csv)
+-- docker/
¦   +-- Dockerfile
¦   +-- init.sql
+-- notebooks/
¦   +-- country_metrics_overview.ipynb
+-- scripts/
¦   +-- process_country_metrics.py
¦   +-- load_country_metrics.py
+-- src/
¦   +-- models/
¦   ¦   +-- country_data.py
¦   ¦   +-- country_etl.py
¦   ¦   +-- city_etl.py (legacy stub)
¦   ¦   +-- city_data.py
¦   +-- utils/validators.py
+-- Makefile
`

## Setup

1. Create a virtual environment and install dependencies:
   `ash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   `
2. Provide credentials in .env (see .env.example):
   `env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=city_metrics
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://:@localhost:/
   `
   API keys are optional; the active workflow uses offline data.
3. Start PostgreSQL:
   `ash
   make up
   `

## Country Data Workflow

1. Drop new raw CSV files into data/raw/ (see data/raw/README.md for provenance).
2. Normalize them:
   `ash
   .venv/Scripts/python.exe scripts/process_country_metrics.py
   `
3. Load the processed table into PostgreSQL, or run both steps at once:
   `ash
   make country-etl
   `

### Programmatic usage

`python
from dotenv import load_dotenv
import os
from src.models.country_etl import CountryDataETL

load_dotenv()
etl = CountryDataETL(os.environ["DATABASE_URL"], "data/processed/country_metrics.csv")
result = etl.run()
print(result.head())
`

The loader upserts into country_data.country_metrics on (country_code, year).

### Notebook tour

Open 
otebooks/country_metrics_overview.ipynb to explore coverage and sample plots without spinning up Docker.

## Legacy city stack

src/models/city_etl.py remains for reference but now raises a runtime error because the collectors were removed. Re-enable it only after restoring fresh city data sources.

## Docker helpers

`
make up           # start PostgreSQL
make down         # stop containers
make clean        # stop containers and remove data volume
make init         # rebuild database (destroys data)
make logs         # tail PostgreSQL logs
make country-etl  # process + load country metrics
`

## License

MIT License.
