import pandas as pd
import numpy as np
import json
from pathlib import Path

# Set paths
raw_data_path = Path('../raw-data')
processed_data_path = Path('../processed-data')
viz_datasets_path = Path('../viz-datasets')

# Load data
df_acled = pd.read_csv(raw_data_path / 'ACLED' / 'ACLED_2025-10-29.csv', encoding='utf-8-sig')
df_econ = pd.read_csv(processed_data_path / 'economics-countries-master.csv')

print(f"ACLED: {len(df_acled):,} events")
print(f"Economics: {len(df_econ):,} country-years")

# Get the current year from the data
current_year = df_acled['year'].max()
print(f"Latest year in data: {current_year}")

# Filter to last 10 years
last_10_years_start = current_year - 9
df_acled_recent = df_acled[df_acled['year'] >= last_10_years_start].copy()

print(f"Filtered to last 10 years: {last_10_years_start}-{current_year}")

# Aggregate events by country-year
conflict_summary = df_acled_recent.groupby(['country', 'year']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).reset_index()
conflict_summary.columns = ['country', 'year', 'event_count', 'total_fatalities']

# Get latest economics data per country
df_econ_latest = df_econ.sort_values('Year').groupby('Country').last().reset_index()

# Join conflict + economics
df_merged = conflict_summary.merge(
    df_econ_latest,
    left_on='country',
    right_on='Country',
    how='left'
)

# Aggregate by country
country_totals = df_merged.groupby('country').agg({
    'event_count': 'sum',
    'total_fatalities': 'sum',
    'Primary_%': 'first',
    'Secondary_%': 'first',
    'Tertiary_%': 'first',
    'Tourism_%': 'first',
    'Population': 'first'
}).reset_index()

# Filter for countries with economics data
country_totals = country_totals[country_totals['Primary_%'].notna()].copy()

# Calculate per capita metrics
country_totals['events_per_100k'] = (country_totals['event_count'] / country_totals['Population']) * 100000
country_totals['fatalities_per_100k'] = (country_totals['total_fatalities'] / country_totals['Population']) * 100000

# Top 20 by conflict
viz1_data = country_totals.nlargest(20, 'event_count').sort_values('event_count', ascending=False)

# Filter to only the 7 highlighted countries in specific order
highlighted_countries = ['Ukraine', 'India', 'Mexico', 'United States', 'Afghanistan', 'Somalia', 'Italy']

# Get data for these countries from viz1_data
stacked_data = viz1_data[viz1_data['country'].isin(highlighted_countries)].copy()

# Sort by the order in highlighted_countries list
stacked_data['sort_order'] = stacked_data['country'].apply(lambda x: highlighted_countries.index(x) if x in highlighted_countries else 999)
stacked_data = stacked_data.sort_values('sort_order').drop(columns=['sort_order'])

# Transform the data for stacked bar chart
# Tourism is shown separately, but subtracted from Tertiary to keep total at 100%
stacked_records = []
for _, row in stacked_data.iterrows():
    country_name = row['country']
    # Handle NaN tourism values - treat as 0
    tourism_pct = float(row['Tourism_%']) if pd.notna(row['Tourism_%']) else 0.0
    tertiary_pct = float(row['Tertiary_%']) if pd.notna(row['Tertiary_%']) else 0.0
    primary_pct = float(row['Primary_%']) if pd.notna(row['Primary_%']) else 0.0
    secondary_pct = float(row['Secondary_%']) if pd.notna(row['Secondary_%']) else 0.0

    # Add each sector as a separate record
    stacked_records.append({
        'country': country_name,
        'sector': 'Primary',
        'percentage': round(primary_pct, 2)
    })
    stacked_records.append({
        'country': country_name,
        'sector': 'Secondary',
        'percentage': round(secondary_pct, 2)
    })
    # Tertiary without Tourism (since Tourism is already part of Tertiary)
    stacked_records.append({
        'country': country_name,
        'sector': 'Tertiary',
        'percentage': round(tertiary_pct - tourism_pct, 2)
    })
    # Tourism shown separately
    stacked_records.append({
        'country': country_name,
        'sector': 'Tourism',
        'percentage': round(tourism_pct, 2)
    })

# Create the output structure
stacked_output = {
    'metadata': {
        'title': '100% Stacked Bar: Economic Sector Composition by Country',
        'description': 'Distribution of economic sectors (Primary, Secondary, Tertiary, Tourism) for highlighted conflict countries',
        'source': 'World Bank + ACLED',
        'date_range': '2015-2024',
        'note': 'Tourism is shown separately but is part of Tertiary sector. Bars total 100%. Only showing the 7 highlighted countries from Viz 1.'
    },
    'countries': stacked_data['country'].tolist(),
    'data': stacked_records
}

# Save to JSON in viz-datasets
output_file = viz_datasets_path / 'viz2_stacked_bar_sectors.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stacked_output, f, indent=2, ensure_ascii=False)

print(f'\n✓ Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)')
print(f'Countries: {len(stacked_data)}')
print(f'Data records: {len(stacked_records)}')
print('\nFirst country sample:')
print([r for r in stacked_records if r['country'] == stacked_data.iloc[0]['country']])

# Also copy to public assets
public_output_file = Path('../../public/src/assets/data/viz2_stacked_bar_sectors.json')
with open(public_output_file, 'w', encoding='utf-8') as f:
    json.dump(stacked_output, f, indent=2, ensure_ascii=False)

print(f'\n✓ Also saved to: {public_output_file}')
