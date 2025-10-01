import re
from pathlib import Path
from typing import Iterable

import pandas as pd

YEAR_MIN = 2015
DATA_DIR = Path('data/raw')
OUTPUT_PATH = Path('data/processed/country_metrics.csv')

CODE_COL = 'country_code'
NAME_COL = 'country_name'


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    code_col = 'REF_AREA' if 'REF_AREA' in df.columns else 'REF_AREA_ID'
    name_col = 'REF_AREA_LABEL' if 'REF_AREA_LABEL' in df.columns else 'REF_AREA_NAME'
    return df.rename(columns={code_col: CODE_COL, name_col: NAME_COL})


def _stack_years(df: pd.DataFrame, value_columns: Iterable[str], value_name: str) -> pd.DataFrame:
    stacked = (
        df.melt(id_vars=[CODE_COL, NAME_COL], value_vars=list(value_columns), var_name='year_raw', value_name=value_name)
        .dropna(subset=[value_name])
    )
    stacked['year'] = stacked['year_raw'].str.slice(0, 4).astype(int)
    stacked = stacked[stacked['year'] >= YEAR_MIN]
    if stacked.empty:
        return stacked
    return stacked.groupby([CODE_COL, NAME_COL, 'year'], as_index=False)[value_name].mean()


def _prepare_employee_income() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'OECD_IDD_EAR_METH2012_WIDEF.csv')
    df = df[df['AGE_NAME'] == 'All age ranges or no breakdown by age']
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'employee_income_index')


def _prepare_cpi() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'FAO_CP_WIDEF.csv')
    df = df[(df['INDICATOR_LABEL'] == 'Consumer Prices, General Indices (2015 = 100)') & (df['FREQ'] == 'M')]
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}-\d{2}', str(c))]
    base = df[[CODE_COL, NAME_COL] + value_cols].copy()
    stacked = (
        base.melt(id_vars=[CODE_COL, NAME_COL], value_vars=value_cols, var_name='year_month', value_name='cpi_monthly')
        .dropna(subset=['cpi_monthly'])
    )
    stacked['year'] = stacked['year_month'].str.slice(0, 4).astype(int)
    stacked = stacked[stacked['year'] >= YEAR_MIN]
    annual = stacked.groupby([CODE_COL, NAME_COL, 'year'], as_index=False)['cpi_monthly'].mean()
    return annual.rename(columns={'cpi_monthly': 'consumer_price_index'})


def _prepare_rent_expenditure() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'IMF_GFSE_GEOPR_G14_WIDEF.csv')
    df = df[(df['UNIT_MEASURE_LABEL'] == 'Percentage of GDP') & (df['SECTOR_LABEL'] == 'Sector: General government')]
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'rent_expenditure_percent_gdp')


def _prepare_house_price_income() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'IMF_GHW_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}-Q\d', str(c))]
    base = df[[CODE_COL, NAME_COL] + value_cols].copy()
    stacked = (
        base.melt(id_vars=[CODE_COL, NAME_COL], value_vars=value_cols, var_name='quarter', value_name='ratio')
        .dropna(subset=['ratio'])
    )
    stacked['year'] = stacked['quarter'].str.slice(0, 4).astype(int)
    stacked = stacked[stacked['year'] >= YEAR_MIN]
    annual = stacked.groupby([CODE_COL, NAME_COL, 'year'], as_index=False)['ratio'].mean()
    return annual.rename(columns={'ratio': 'house_price_to_income_ratio'})


def _prepare_real_gdp_growth() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'BS_SGI_10_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'real_gdp_growth_rate')


def _prepare_digital_economy() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'UNCTAD_DE_WIDEF.csv')
    df = df[df['INDICATOR_LABEL'] == 'Proportion of businesses using the Internet']
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'digital_economy_score')


def _prepare_higher_education() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'WEF_GCIHH_GCI_B_05_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    stacked = _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'higher_education_raw')
    stacked['higher_education_score'] = stacked['higher_education_raw'] / 7 * 100
    return stacked.drop(columns=['higher_education_raw'])


def _prepare_life_satisfaction() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'BS_SGI_67_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'life_satisfaction_score')


def _prepare_cultural_resources() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'WEF_TTDI_TTDI_D_13_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    stacked = _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'cultural_resources_raw')
    stacked['cultural_resources_index'] = stacked['cultural_resources_raw'] / 7 * 100
    return stacked.drop(columns=['cultural_resources_raw'])


def _prepare_sports_expenditure() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'IMF_COFOG_GERS_GF0801_WIDEF.csv')
    df = df[(df['UNIT_MEASURE_LABEL'] == 'Percentage of GDP') & (df['SECTOR_LABEL'] == 'Sector: General government')]
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'sports_expenditure_percent_gdp')


def _prepare_road_mortality() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'WB_WDI_SH_STA_TRAF_P5_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'road_traffic_mortality_rate')


def _prepare_forest_area() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'WB_ESG_AG_LND_FRST_ZS_WIDEF.csv')
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'forest_area_percent')


def _prepare_life_expectancy() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / 'WEF_GCIHH_LIFEEXPECT_WIDEF.csv')
    df = df[df['UNIT_MEASURE_LABEL'] == 'Years']
    df = _standardize(df)
    value_cols = [c for c in df.columns if re.fullmatch(r'\d{4}', str(c))]
    return _stack_years(df[[CODE_COL, NAME_COL] + value_cols], value_cols, 'life_expectancy_years')


def _forward_fill_per_country(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values([CODE_COL, NAME_COL, 'year']).reset_index(drop=True)


def _merge_metrics(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    from functools import reduce
    combined = reduce(lambda left, right: left.merge(right, on=[CODE_COL, NAME_COL, 'year'], how='outer'), dfs)
    return combined.sort_values([CODE_COL, 'year']).reset_index(drop=True)


def main() -> None:
    generators = [
        ('employee_income_index', _prepare_employee_income),
        ('consumer_price_index', _prepare_cpi),
        ('rent_expenditure_percent_gdp', _prepare_rent_expenditure),
        ('house_price_to_income_ratio', _prepare_house_price_income),
        ('real_gdp_growth_rate', _prepare_real_gdp_growth),
        ('digital_economy_score', _prepare_digital_economy),
        ('higher_education_score', _prepare_higher_education),
        ('life_satisfaction_score', _prepare_life_satisfaction),
        ('cultural_resources_index', _prepare_cultural_resources),
        ('sports_expenditure_percent_gdp', _prepare_sports_expenditure),
        ('road_traffic_mortality_rate', _prepare_road_mortality),
        ('forest_area_percent', _prepare_forest_area),
        ('life_expectancy_years', _prepare_life_expectancy),
    ]

    frames = []
    for column_name, factory in generators:
        df = factory()
        df = _forward_fill_per_country(df, column_name)
        frames.append(df)

    combined = _merge_metrics(frames)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f'Wrote {len(combined)} rows to {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
