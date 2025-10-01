# City Geo Warehouse

An ETL playground that builds a unified warehouse of socio-economic metrics. The current focus is on **country-level** indicators compiled from public bulk datasets (OECD, IMF, UNCTAD, World Bank, WEF). The legacy city pipeline remains in the codebase for future expansion.

## Directory Layout

`
.
+-- data/
¦   +-- raw/         # original CSV dumps (wide format)
¦   +-- processed/   # normalized datasets (e.g. country_metrics.csv)
+-- docker/
¦   +-- Dockerfile
¦   +-- init.sql
+-- notebooks/
¦   +-- city_data_etl.ipynb
+-- scripts/
¦   +-- process_country_metrics.py
¦   +-- load_country_metrics.py
¦   +-- ...
+-- src/
¦   +-- models/
¦   ¦   +-- country_data.py
¦   ¦   +-- country_etl.py
¦   ¦   +-- city_data.py (legacy)
¦   ¦   +-- ...
¦   +-- utils/
¦       +-- validators.py
+-- Makefile
+-- docker-compose.yml
+-- requirements.txt
+-- README.md
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
2. Provide credentials in .env:
   `env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=city_metrics
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://:@localhost:/
   `
   API keys are optional at the moment (the active pipeline relies on offline datasets).
3. Start PostgreSQL:
   `ash
   make up
   `

## Country Data Workflow

1. Drop raw source files in data/raw/ (see data/raw/README.md for provenance and definitions).
2. Normalize them:
   `ash
   .venv/Scripts/python.exe scripts/process_country_metrics.py
   `
3. Load the processed table into PostgreSQL:
   `ash
   .venv/Scripts/python.exe scripts/load_country_metrics.py
   `
   or run everything at once:
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

The loader writes to country_data.country_metrics with an upsert on (country_code, year).

## Legacy City Stack (optional)

The project still ships the city collectors and ETL (GeoDB, OpenWeatherMap, OpenStreetMap). They can be exercised with:
`python
from src.models.city_etl import CityDataETL

etl = CityDataETL(database_url=os.environ["DATABASE_URL"])
`
Those components are not wired into the default workflow until richer city data is available.

## Docker Helpers

`
make up           # start PostgreSQL
make down         # stop containers
make clean        # stop containers and remove data volume
make init         # full database reset (destroys data)
make logs         # tail PostgreSQL logs
make country-etl  # process + load country metrics
`

## License

MIT License.
