import pandas as pd
import json
from pathlib import Path

# Read the viz1 JSON to get the same countries in the same order
with open('viz-datasets/viz1_bar_chart_sectors_conflicts.json', 'r', encoding='utf-8') as f:
    viz1 = json.load(f)

viz1_data = pd.DataFrame(viz1['data'])

# Create stacked bar chart data
stacked_records = []
for _, row in viz1_data.iterrows():
    country_name = row['country']

    # Add each sector as a separate record
    stacked_records.append({
        'country': country_name,
        'sector': 'Primary',
        'percentage': float(row['Primary_%'])
    })
    stacked_records.append({
        'country': country_name,
        'sector': 'Secondary',
        'percentage': float(row['Secondary_%'])
    })
    stacked_records.append({
        'country': country_name,
        'sector': 'Tertiary',
        'percentage': float(row['Tertiary_%'])
    })
    # Only add Tourism if it's greater than 0
    if row['Tourism_%'] > 0:
        stacked_records.append({
            'country': country_name,
            'sector': 'Tourism',
            'percentage': float(row['Tourism_%'])
        })

# Create the output structure
stacked_output = {
    'metadata': {
        'title': '100% Stacked Bar: Economic Sector Composition by Country',
        'description': 'Distribution of economic sectors (Primary, Secondary, Tertiary, Tourism) for top 20 conflict countries',
        'source': 'World Bank + ACLED',
        'date_range': '2015-2024',
        'note': 'Countries ordered by total conflict events (same as Viz 1)'
    },
    'countries': viz1_data['country'].tolist(),
    'data': stacked_records
}

# Save to JSON
output_file = Path('viz-datasets/viz5_stacked_bar_sectors.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stacked_output, f, indent=2, ensure_ascii=False)

print(f'Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)')
print(f'Countries: {len(viz1_data)}')
print(f'Data records: {len(stacked_records)}')
print('\nFirst country sample:')
print([r for r in stacked_records if r['country'] == viz1_data.iloc[0]['country']])
