import pandas as pd
from pathlib import Path

FILES = [
    'OECD_IDD_EAR_METH2012_WIDEF.csv',
    'FAO_CP_WIDEF.csv',
    'IMF_GFSE_GEOPR_G14_WIDEF.csv',
    'IMF_GHW_WIDEF.csv',
    'BS_SGI_10_WIDEF.csv',
    'UNCTAD_DE_WIDEF.csv',
    'WEF_GCIHH_GCI_B_05_WIDEF.csv',
    'BS_SGI_67_WIDEF.csv',
    'WEF_TTDI_TTDI_D_13_WIDEF.csv',
    'IMF_COFOG_GERS_GF0801_WIDEF.csv',
    'WB_WDI_SH_STA_TRAF_P5_WIDEF.csv',
    'WB_ESG_AG_LND_FRST_ZS_WIDEF.csv',
    'WEF_GCIHH_LIFEEXPECT_WIDEF.csv',
]

ROOT = Path('data')

for name in FILES:
    path = ROOT / name
    df = pd.read_csv(path, nrows=3)
    cols = list(df.columns)
    tail_cols = cols[:6] + cols[-4:]
    print(f"=== {name} ===")
    print('columns sample:', tail_cols)
    print(df.iloc[:2, :6])
    print()
