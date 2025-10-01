# Data Directory

## Structure
- raw/ - source tables exactly as downloaded (wide format, untouched units)
- processed/ - normalized datasets ready for ingestion (currently country_metrics.csv)

## Processed Dataset: country_metrics.csv
Produced by scripts/process_country_metrics.py from the files in data/raw. Rows cover every available country/year from 2015 onward. Missing values remain NaN; no forward filling is applied.

| Column | Source | Unit / Notes |
| --- | --- | --- |
| country_code | original REF_AREA code | string as provided by the source |
| country_name | original REF_AREA_LABEL | country display name |
| year | derived from column headers | integer year >= 2015 |
| employee_income_index | OECD_IDD_EAR_METH2012 | domestic currency per equivalized household, all ages |
| consumer_price_index | FAO_CP (general CPI, 2015=100) | annual mean of the monthly CPI (base 2015=100) |
| rent_expenditure_percent_gdp | IMF_GFSE_GEOPR_G14 | general government rent expenditure, % of GDP |
| house_price_to_income_ratio | IMF_GHW | yearly mean of the quarterly house price-to-income ratio |
| real_gdp_growth_rate | BS_SGI_10 | percent (real GDP annual growth) |
| digital_economy_score | UNCTAD_DE (businesses using the Internet) | percent of businesses |
| higher_education_score | WEF_GCIHH_GCI_B_05 | pillar score rescaled from 1-7 to 0-100 |
| life_satisfaction_score | BS_SGI_67 | score 0-10 |
| cultural_resources_index | WEF_TTDI_TTDI_D_13 | pillar score rescaled from 1-7 to 0-100 |
| sports_expenditure_percent_gdp | IMF_COFOG_GERS_GF0801 | general government sports services, % of GDP |
| road_traffic_mortality_rate | WB_WDI_SH_STA_TRAF_P5 | deaths per 100,000 population |
| forest_area_percent | WB_ESG_AG_LND_FRST_ZS | percent of land area |
| life_expectancy_years | WEF_GCIHH_LIFEEXPECT (unit: Years) | life expectancy at birth, years |

## Workflow
1. Drop new raw downloads into data/raw/.
2. Run python scripts/process_country_metrics.py from the project root; the script rewrites data/processed/country_metrics.csv and ensures the directory exists.
3. Downstream ETL should read from data/processed/.
