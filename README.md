# City Data ETL Project

This project demonstrates a data engineering ETL (Extract, Transform, Load) process for collecting and analyzing city metrics across various dimensions including cultural, economic, environmental, and social factors.

## Project Structure

```
├── src/
│   ├── etl/
│   │   ├── extractors/
│   │   ├── transformers/
│   │   └── loaders/
│   ├── models/
│   ├── config/
│   └── utils/
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── requirements.txt
└── README.md
```

## Features

- Data collection from multiple sources (APIs)
- Data transformation and cleaning using pandas
- PostgreSQL database integration
- Complex SQL analysis with window functions
- Data visualization
- Pydantic models for data validation

## Requirements

- Python 3.8+
- PostgreSQL
- Python packages listed in requirements.txt

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
- Create a database named 'city_metrics'
- Update the .env file with your database credentials

4. Create the database schema:
- Run the Jupyter notebook in notebooks/city_data_etl.ipynb

## Data Sources

The project collects data from various sources including:
- Cost of living data
- Weather data
- Economic indicators
- Environmental metrics
- Social and cultural indicators

## Analysis Features

- City ranking by various metrics
- Cost of living comparisons
- Quality of life analysis
- Environmental impact assessment
- Cultural and social indicators analysis

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License.
