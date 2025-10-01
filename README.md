# City Geo Warehouse

City Geo Warehouse prepares analytics-ready datasets for a future web service where users will be able to filter the best cities to live in by selected criteria. The current focus is on collecting and cleaning country-level socio-economic indicators, and the project structure is ready to attach city-level sources with geometry from OpenStreetMap and other geospatial feeds.

## What the Project Does
- collects open CSV datasets from OECD, IMF, UNCTAD, World Bank, and WEF
- normalizes indicators with mixed frequencies and units into a single table with explicit country and year labels
- loads the processed data into PostgreSQL while keeping reruns free from duplicates
- ships an overview notebook that lets you inspect the resulting dataset in minutes

## ETL Pipeline

### Data preparation
Raw files go to `data/raw/`, every source is described in `data/raw/README.md`.

### Normalization (`scripts/process_country_metrics.py`)
- reads tables where years are spread across columns
- converts yearly columns into rows so every country and year occupies a dedicated record
- aggregates monthly and quarterly series into annual values starting from 2015
- rescales indicators from a 1-7 scoring scheme to 0-100 and clips extreme outliers
- drops rows with no available metrics
- writes the final dataset to `data/processed/country_metrics.csv`

### Validation and loading (`scripts/load_country_metrics.py`)
- validates records with the `CountryMetrics` model (Pydantic) and rules from `src/utils/validators.py`
- performs an upsert on `(country_code, year)` into the `country_data.country_metrics` table
- creates required schemas on startup using `docker/init.sql`

### Exploring the result
The notebook `notebooks/country_metrics_overview.ipynb` reads the processed CSV, highlights year coverage, compares real GDP growth against the digital economy score, and exports the latest available snapshot.

## Core Metrics
```bash
employee_income_index                             # employee income index per household in local currency;
consumer_price_index                              # annual CPI with 2015 = 100;
rent_expenditure_percent_gdp                      # share of government rent expenses relative to GDP;
house_price_to_income_ratio                       # housing price to income ratio averaged across quarters;
real_gdp_growth_rate                              # real GDP growth rate in percent;
digital_economy_score                             # share of businesses using the internet;
higher_education_score                            # higher education score rescaled from 1-7 to 0-100;
life_satisfaction_score                           # life satisfaction index from 0 to 10;
cultural_resources_index                          # cultural resources score rescaled from 1-7 to 0-100;
sports_expenditure_percent_gdp                    # government spending on sports as a percentage of GDP;
road_traffic_mortality_rate                       # road traffic mortality per 100000 inhabitants;
forest_area_percent                               # share of forest land within total territory;
life_expectancy_years                             # life expectancy at birth in years.
```

## Repository Layout
- `data/raw/` raw source files
- `data/processed/` normalized datasets
- `docker/` Dockerfile and initialization SQL
- `scripts/` ETL steps
- `src/models/` models and loaders
- `src/utils/validators.py` validation helpers
- `notebooks/` processed data overview
- `Makefile`, `docker-compose.yml`, `pyproject.toml`, `.env.example`, `README.md`

## Run the Project
```bash
cp .env.example .env          # create the environment file from the template
uv sync                       # build the virtual environment and install dependencies
make up                       # start the PostgreSQL container
make country-etl              # normalize the data and load it into the database
```

## Roadmap
- Add city-level metrics such as distance to waterfronts, park access, green area share, and transport accessibility from OpenStreetMap, then join them with the country indicators.
- Build a dedicated city dataset and a companion notebook.
- Expand the pipeline with dbt for transformations, Airflow or Prefect for orchestration, Great Expectations for data quality checks, Google Cloud integration, Delta Lake style storage, feature store patterns, automated tests, and CI/CD.

## License
MIT License.
