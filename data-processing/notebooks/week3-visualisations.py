"""
Week 3 Visualizations: Mexico vs India Conflict Timeline

Input: ACLED events data (2018-2024)
Output: JSON dataset for D3.js stream charts comparing conflict types in Mexico and India before/after COVID-19
"""

import pandas as pd
import json
from pathlib import Path

# Disable display warnings
pd.set_option('display.max_columns', None)

# Setup paths
raw_data_path = Path('../raw-data')
viz_datasets_path = Path('../viz-datasets')
viz_datasets_path.mkdir(exist_ok=True)

# Load ACLED data
df_acled = pd.read_csv(raw_data_path / 'ACLED' / 'ACLED_2025-10-29.csv', encoding='utf-8-sig')

# Parse event_date to datetime
df_acled['event_date'] = pd.to_datetime(df_acled['event_date'])

# Get current year from data
current_year = df_acled['year'].max()
start_year = current_year - 6  # Last 7 years (inclusive)

# Filter for Mexico and India only
countries_of_interest = ['Mexico', 'India']
df_filtered = df_acled[
    (df_acled['country'].isin(countries_of_interest)) &
    (df_acled['year'] >= start_year)
].copy()

# Create year-month column for monthly aggregation
df_filtered['year_month'] = df_filtered['event_date'].dt.to_period('M')

# Group by country, year_month, and event_type
stream_data = df_filtered.groupby(['country', 'year_month', 'event_type']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).reset_index()

stream_data.columns = ['country', 'year_month', 'event_type', 'event_count', 'fatalities']

# Convert year_month to string for JSON serialization
stream_data['year_month'] = stream_data['year_month'].astype(str)

# Convert to appropriate types
stream_data['event_count'] = stream_data['event_count'].astype(int)
stream_data['fatalities'] = stream_data['fatalities'].astype(int)

# Create a mapping for event types (combine Protests + Riots, and Explosions/Strategic into Other)
event_type_mapping = {
    'Protests': 'Protests & Riots',
    'Riots': 'Protests & Riots',
    'Battles': 'Battles',
    'Explosions/Remote violence': 'Other',
    'Violence against civilians': 'Violence against civilians',
    'Strategic developments': 'Other'
}

stream_data_clean = stream_data.copy()
stream_data_clean['event_category'] = stream_data_clean['event_type'].map(event_type_mapping)

# Re-aggregate with the combined categories
stream_data_combined = stream_data_clean.groupby(['country', 'year_month', 'event_category']).agg({
    'event_count': 'sum',
    'fatalities': 'sum'
}).reset_index()

# Create separate datasets for Mexico and India
mexico_data = stream_data_combined[stream_data_combined['country'] == 'Mexico'].copy()
india_data = stream_data_combined[stream_data_combined['country'] == 'India'].copy()

# Pivot to have year_month as rows and event categories as columns
mexico_pivot_count = mexico_data.pivot(index='year_month', columns='event_category', values='event_count').fillna(0)
india_pivot_count = india_data.pivot(index='year_month', columns='event_category', values='event_count').fillna(0)

mexico_pivot_fatal = mexico_data.pivot(index='year_month', columns='event_category', values='fatalities').fillna(0)
india_pivot_fatal = india_data.pivot(index='year_month', columns='event_category', values='fatalities').fillna(0)

# Reset index to make year_month a column
mexico_pivot_count = mexico_pivot_count.reset_index()
india_pivot_count = india_pivot_count.reset_index()
mexico_pivot_fatal = mexico_pivot_fatal.reset_index()
india_pivot_fatal = india_pivot_fatal.reset_index()

# Convert to int
for col in mexico_pivot_count.columns:
    if col != 'year_month':
        mexico_pivot_count[col] = mexico_pivot_count[col].astype(int)
        india_pivot_count[col] = india_pivot_count[col].astype(int)
        mexico_pivot_fatal[col] = mexico_pivot_fatal[col].astype(int)
        india_pivot_fatal[col] = india_pivot_fatal[col].astype(int)

def create_stream_records(pivot_count_df, pivot_fatal_df, country_name):
    """
    Convert pivot dataframes to stream chart format with tooltip data
    """
    records = []
    event_cols = [col for col in pivot_count_df.columns if col != 'year_month']

    for i, row_count in pivot_count_df.iterrows():
        row_fatal = pivot_fatal_df.iloc[i]
        year_month = str(row_count['year_month'])

        # Calculate totals
        total_events = sum(row_count[col] for col in event_cols)
        total_fatalities = sum(row_fatal[col] for col in event_cols)

        month_record = {
            'date': year_month,
        }

        # Add event counts for each category
        for event_type in event_cols:
            month_record[event_type] = int(row_count[event_type])

        # Add fatalities for each category
        for event_type in event_cols:
            month_record[f'{event_type}_fatalities'] = int(row_fatal[event_type])

        # Add aggregated data for tooltip context
        month_record['_total_events'] = int(total_events)
        month_record['_total_fatalities'] = int(total_fatalities)

        # Calculate percentages and rates for each event type
        for event_type in event_cols:
            event_count = int(row_count[event_type])
            event_fatalities = int(row_fatal[event_type])

            month_record[f'{event_type}_pct'] = round((event_count / total_events * 100) if total_events > 0 else 0, 1)
            month_record[f'{event_type}_fatality_rate'] = round((event_fatalities / event_count) if event_count > 0 else 0, 2)

        records.append(month_record)

    return records

# Create records for both countries
mexico_records = create_stream_records(mexico_pivot_count, mexico_pivot_fatal, 'Mexico')
india_records = create_stream_records(india_pivot_count, india_pivot_fatal, 'India')

# Get all event categories
all_event_categories = sorted(set(
    list(stream_data_combined['event_category'].unique())
))

# Create metadata
metadata = {
    'title': 'Violence in Mexico and India: Timeline Comparison (2018-2024)',
    'description': 'Stream charts comparing conflict types and intensity in Mexico and India before, during, and after COVID-19',
    'source': 'ACLED',
    'date_range': f'{start_year}-{current_year}',
    'countries': ['Mexico', 'India'],
    'event_categories': all_event_categories,
    'tooltip_fields': {
        'counts': 'Direct event category values (e.g., "Battles")',
        'fatalities': 'Event category with _fatalities suffix (e.g., "Battles_fatalities")',
        'percentages': 'Event category with _pct suffix (e.g., "Battles_pct")',
        'fatality_rate': 'Event category with _fatality_rate suffix (e.g., "Battles_fatality_rate")',
        'totals': '_total_events and _total_fatalities fields'
    },
    'notes': [
        'Data aggregated monthly (YYYY-MM format)',
        'Protests and Riots combined into single category',
        'Explosions/Remote violence and Strategic developments combined into Other category',
        'Pre-COVID period: 2018-2019',
        'COVID period: 2020-2021',
        'Post-COVID period: 2022-2024',
        'Tooltip data includes: fatalities, percentages, and fatality rates per event type'
    ]
}

# Create final output
output = {
    'metadata': metadata,
    'mexico': mexico_records,
    'india': india_records
}

# Save JSON
output_file = viz_datasets_path / 'viz6_stream_mexico_india_timeline.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated: {output_file.name} ({output_file.stat().st_size / 1024:.1f} KB)")
