"""
Analyze all datasets to understand their structure
"""
import pandas as pd
from pathlib import Path

raw_data = Path('../raw-data')

datasets = {
    'Epac': ['ED-2021.csv'],
    'Religious_Cleavages': ['Religious_Cleavages_Dataset.csv'],
    'UCDP': ['Actor_v25_1.csv', 'BattleDeaths_v25_1.csv', 'GEDEvent_v25_0_9.csv', 'UcdpPrioConflict_v25_1.csv'],
    'WRP': ['WRP_global.csv', 'WRP_national.csv', 'WRP_regional.csv']
}

for org, files in datasets.items():
    print(f"\n{'='*80}")
    print(f"ORGANIZATION: {org}")
    print('='*80)

    for file in files:
        filepath = raw_data / org / file
        print(f"\n[FILE] {file}")
        print('-' * 80)

        try:
            df = pd.read_csv(filepath, nrows=5)
            print(f"Shape: {len(pd.read_csv(filepath))} rows × {len(df.columns)} columns")
            print(f"\nColumns ({len(df.columns)}):")

            full_df = pd.read_csv(filepath)
            for i, col in enumerate(df.columns, 1):
                dtype = full_df[col].dtype
                non_null = full_df[col].notna().sum()
                sample_val = full_df[col].dropna().iloc[0] if len(full_df[col].dropna()) > 0 else "N/A"
                if isinstance(sample_val, str) and len(str(sample_val)) > 50:
                    sample_val = str(sample_val)[:47] + "..."
                print(f"  {i:2d}. {col:30s} ({dtype}) - Example: {sample_val}")

            print(f"\nFirst 2 rows preview:")
            print(full_df.head(2).to_string(index=False, max_colwidth=40))

        except Exception as e:
            print(f"Error reading file: {e}")

        print()
