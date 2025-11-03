import pandas as pd
import numpy as np
import json
from pathlib import Path

print("=== Week 1 Visualizations: Economic Sectors & Conflict Analysis ===\n")

# Setup
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

raw_data_path = Path('../raw-data')
processed_data_path = Path('../processed-data')

# Load Data
print("Loading data...")
df_acled = pd.read_csv(raw_data_path / 'ACLED' / 'ACLED_2025-10-29.csv', encoding='utf-8-sig')
df_econ = pd.read_csv(processed_data_path / 'economics-countries-master.csv')

print(f"ACLED: {len(df_acled):,} events")
print(f"Economics: {len(df_econ):,} country-years")

# Get the current year from the data
current_year = df_acled['year'].max()
print(f"Latest year in data: {current_year}\n")

# Process & Join
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

# Get latest economics data per country (includes Population now)
df_econ_latest = df_econ.sort_values('Year').groupby('Country').last().reset_index()

# Join conflict + economics
df_merged = conflict_summary.merge(
    df_econ_latest,
    left_on='country',
    right_on='Country',
    how='left'
)

print(f"Merged: {len(df_merged):,} rows")
print(f"Records with population data: {df_merged['Population'].notna().sum():,}\n")

# Viz 1: Bar Chart - Top Countries by Primary Sector %
print("=== Creating Viz 1: Bar Chart ===")

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

# Check USA tourism data
usa_row = viz1_data[viz1_data['country'] == 'United States']
if len(usa_row) > 0:
    print(f"USA Tourism %: {usa_row['Tourism_%'].iloc[0]}")

viz_data = viz1_data[['country', 'event_count', 'total_fatalities',
                      'events_per_100k', 'fatalities_per_100k',
                      'Primary_%', 'Secondary_%', 'Tertiary_%', 'Tourism_%',
                      'Population']].copy()

# Clean values
viz_data['event_count'] = viz_data['event_count'].astype(int)
viz_data['total_fatalities'] = viz_data['total_fatalities'].astype(int)
viz_data['events_per_100k'] = viz_data['events_per_100k'].round(2)
viz_data['fatalities_per_100k'] = viz_data['fatalities_per_100k'].round(2)
viz_data['Primary_%'] = viz_data['Primary_%'].round(2)
viz_data['Secondary_%'] = viz_data['Secondary_%'].round(2)
viz_data['Tertiary_%'] = viz_data['Tertiary_%'].round(2)
viz_data['Tourism_%'] = viz_data['Tourism_%'].fillna(0).round(2)
viz_data['Population'] = viz_data['Population'].astype('Int64')

metadata = {
    'title': 'Top Conflict Countries by Economic Sector (2015-2024)',
    'description': 'Top 20 countries sorted by number of conflict events',
    'source': 'ACLED + World Bank',
    'date_range': '2015-2024',
    'notes': 'Per capita rates calculated per 100,000 population'
}

viz_datasets_path = Path('../viz-datasets')
viz_datasets_path.mkdir(exist_ok=True)

output = {
    'metadata': metadata,
    'data': viz_data.to_dict('records')
}

output_file = viz_datasets_path / 'viz1_bar_chart_sectors_conflicts.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)\n")

# Viz 2: 100% Stacked Bar Chart - Economic Sector Composition
print("=== Creating Viz 2: 100% Stacked Bar Chart ===")

highlighted_countries = ['Ukraine', 'India', 'Mexico', 'United States', 'Afghanistan', 'Somalia', 'Italy']

stacked_data = viz1_data[viz1_data['country'].isin(highlighted_countries)].copy()

# Sort by the order in highlighted_countries list
stacked_data['sort_order'] = stacked_data['country'].apply(lambda x: highlighted_countries.index(x) if x in highlighted_countries else 999)
stacked_data = stacked_data.sort_values('sort_order').drop(columns=['sort_order'])

stacked_records = []
for _, row in stacked_data.iterrows():
    country_name = row['country']
    tourism_pct = float(row['Tourism_%'])
    tertiary_pct = float(row['Tertiary_%'])

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
        'percentage': tertiary_pct - tourism_pct
    })
    stacked_records.append({
        'country': country_name,
        'sector': 'Tourism',
        'percentage': tourism_pct
    })

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

output_file = viz_datasets_path / 'viz2_stacked_bar_sectors.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stacked_output, f, indent=2, ensure_ascii=False)

print(f'Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)\n')

# Viz 3: Grouped Bar Chart - Event types by Countries
print("=== Creating Viz 3: Grouped Bar Chart ===")

events_by_country = df_acled_recent.groupby(['country', 'event_type'])['event_id_cnty'].count().reset_index()

pivot_df = events_by_country.pivot(index='country', columns='event_type', values='event_id_cnty').fillna(0)

pivot_df = pivot_df[pivot_df.index.isin(highlighted_countries)]

pivot_df['Protests & Riots'] = pivot_df['Protests'] + pivot_df['Riots']

viz3_columns = ['Battles', 'Explosions/Remote violence', 'Protests & Riots', 'Violence against civilians']
pivot_df = pivot_df[viz3_columns]

pivot_df['sort_order'] = pivot_df.index.map(lambda x: highlighted_countries.index(x) if x in highlighted_countries else 999)
pivot_df = pivot_df.sort_values('sort_order').drop(columns=['sort_order'])

pivot_df = pivot_df.reset_index()

for col in viz3_columns:
    pivot_df[col] = pivot_df[col].astype(int)

output_data = {
    "metadata": {
        "title": "Event Types by Country (2015-2024)",
        "description": "Distribution of ACLED event types across the 7 highlighted countries",
        "source": "ACLED",
        "date_range": "2015-2024",
        "note": "Protests & Riots combined. Strategic developments excluded. Same 7 countries as viz2."
    },
    "data": pivot_df.to_dict('records')
}

with open('../viz-datasets/viz3_event_types.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"Saved: viz3_event_types.json\n")

# Viz 4: Heatmap - Event Types × Years
print("=== Creating Viz 4: Heatmap ===")

heatmap_data = df_acled_recent.groupby(['year', 'event_type']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).reset_index()

heatmap_data.columns = ['year', 'event_type', 'event_count', 'total_fatalities']

heatmap_data['year'] = heatmap_data['year'].astype(int)
heatmap_data['event_count'] = heatmap_data['event_count'].astype(int)
heatmap_data['total_fatalities'] = heatmap_data['total_fatalities'].astype(int)

metadata = {
    'title': 'Heatmap: Event Types by Year (2015-2024)',
    'description': 'Temporal distribution of ACLED event types showing both event counts and fatalities',
    'source': 'ACLED',
    'date_range': f"{heatmap_data['year'].min()}-{heatmap_data['year'].max()}",
    'note': 'Color intensity based on event_count, fatalities included for additional context'
}

output = {
    'metadata': metadata,
    'data': heatmap_data.to_dict('records')
}

output_file = viz_datasets_path / 'viz4_heatmap_event_types_years.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)\n")

# Viz 5: Waffle Chart - Economic Sectors by Event Type
print("=== Creating Viz 5: Waffle Chart ===")

df_events_econ = df_acled_recent.merge(
    df_econ_latest[['Country', 'Primary_%', 'Secondary_%', 'Tertiary_%']],
    left_on='country',
    right_on='Country',
    how='left'
)

df_events_econ = df_events_econ[
    df_events_econ['Primary_%'].notna() &
    df_events_econ['Secondary_%'].notna() &
    df_events_econ['Tertiary_%'].notna()
].copy()

df_events_econ = df_events_econ[df_events_econ['event_type'] != 'Strategic developments'].copy()

country_event_counts = df_events_econ.groupby(['event_type', 'country']).agg({
    'event_id_cnty': 'count',
    'Primary_%': 'first',
    'Secondary_%': 'first',
    'Tertiary_%': 'first'
}).reset_index()

country_event_counts.columns = ['event_type', 'country', 'event_count', 'Primary_%', 'Secondary_%', 'Tertiary_%']

waffle_data = []

for event_type in country_event_counts['event_type'].unique():
    event_df = country_event_counts[country_event_counts['event_type'] == event_type].copy()

    total_events = event_df['event_count'].sum()

    event_df['weight'] = event_df['event_count'] / total_events

    primary_weighted = (event_df['Primary_%'] * event_df['weight']).sum()
    secondary_weighted = (event_df['Secondary_%'] * event_df['weight']).sum()
    tertiary_weighted = (event_df['Tertiary_%'] * event_df['weight']).sum()

    total_pct = primary_weighted + secondary_weighted + tertiary_weighted
    primary_weighted = (primary_weighted / total_pct) * 100
    secondary_weighted = (secondary_weighted / total_pct) * 100
    tertiary_weighted = (tertiary_weighted / total_pct) * 100

    waffle_data.append({
        'event_type': event_type,
        'event_count': int(total_events),
        'primary_pct': round(primary_weighted, 2),
        'secondary_pct': round(secondary_weighted, 2),
        'tertiary_pct': round(tertiary_weighted, 2)
    })

waffle_df = pd.DataFrame(waffle_data)

waffle_df = waffle_df.sort_values('primary_pct', ascending=False).reset_index(drop=True)

waffle_df['total_pct'] = waffle_df['primary_pct'] + waffle_df['secondary_pct'] + waffle_df['tertiary_pct']

waffle_records = []

for _, row in waffle_df.iterrows():
    event_name = row['event_type']

    event_record = {
        'event_type': event_name,
        'event_count': int(row['event_count']),
        'sectors': [
            {
                'sector': 'Primary',
                'percentage': float(row['primary_pct'])
            },
            {
                'sector': 'Secondary',
                'percentage': float(row['secondary_pct'])
            },
            {
                'sector': 'Tertiary',
                'percentage': float(row['tertiary_pct'])
            }
        ],
        'total_percentage': float(row['total_pct'])
    }

    waffle_records.append(event_record)

metadata = {
    'title': 'Waffle Chart: Economic Sector Composition by Event Type',
    'description': 'Weighted average economic sector distribution for countries experiencing each type of conflict event',
    'source': 'ACLED + World Bank',
    'date_range': f'{last_10_years_start}-{current_year}',
    'note': 'Percentages are WEIGHTED by event frequency per country. Countries with more events of a type have proportionally more influence on the average. Tourism sector removed. NaN values excluded. Strategic developments excluded. Sorted by Primary sector percentage.'
}

waffle_output = {
    'metadata': metadata,
    'data': waffle_records
}

output_file = viz_datasets_path / 'viz5_waffle_sectors_by_event_type.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(waffle_output, f, indent=2, ensure_ascii=False)

print(f'Saved: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)\n')

print("\n=== All visualizations created successfully! ===")
