import os
import pandas as pd
from pathlib import Path

data_files = [f for f in os.listdir('.') if f.endswith('.csv')]

for file_name in data_files:
    print(file_name)
    data = pd.read_csv(file_name)
    data['DateRepConf'] = pd.to_datetime(data['DateRepConf'])

    # regions
    confirmed = data.groupby('RegionRes').size().to_frame('confirmed')
    deaths = data[data['RemovalType'] == 'DIED'].groupby(
        'RegionRes').size().to_frame('deaths')
    recovered = data[data['RemovalType'] == 'RECOVERED'].groupby(
        'RegionRes').size().to_frame('recovered')
    combined = pd.concat([confirmed, deaths, recovered], axis=1)
    combined = combined.fillna(0).astype(int).rename_axis(
        'region').reset_index()
    combined.to_csv(f'./regions/{file_name}', index=False)

    # provinces
    if 'ProvRes' in data:
        confirmed = data.groupby(['RegionRes',
                                  'ProvRes']).size().to_frame('confirmed')
        deaths = data[data['RemovalType'] == 'DIED'].groupby(
            ['RegionRes', 'ProvRes']).size().to_frame('deaths')
        recovered = data[data['RemovalType'] == 'RECOVERED'].groupby(
            ['RegionRes', 'ProvRes']).size().to_frame('recovered')
        combined = pd.concat([confirmed, deaths, recovered], axis=1)
        combined = combined.fillna(0).astype(int)
        combined = combined.rename_axis(['region', 'province']).reset_index()
        combined.to_csv(f'./provinces/{file_name}', index=False)

    print(f'{file_name[:10]} data processed!')

# clean files
for p in Path('.').glob("*.csv"):
    p.unlink()