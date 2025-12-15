"""
Regenerate Sankey data with exact dates instead of just years
"""
import pandas as pd
import json
from datetime import datetime
import os

BASE_DIR = r'C:\Users\glaes\Desktop\github\vizis'

# Load ACLED data
print("Loading ACLED dataset...")
df = pd.read_csv(os.path.join(BASE_DIR, 'data-processing', 'raw-data', 'ACLED', 'ACLED_2025-10-29.csv'))
print(f"Dataset shape: {df.shape}")

# Get top actors by type (same as original)
actor_stats = df.groupby(['inter1', 'actor1']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum',
    'country': 'nunique'
}).rename(columns={
    'event_id_cnty': 'total_events',
    'country': 'countries_active'
}).reset_index()

# Get top 10 actors per actor type
top_actors_by_type = {}
for actor_type in actor_stats['inter1'].unique():
    if pd.isna(actor_type):
        continue
    type_actors = actor_stats[actor_stats['inter1'] == actor_type].nlargest(10, 'total_events')
    top_actors_by_type[actor_type] = type_actors['actor1'].tolist()

# Create list of all selected actors
all_selected_actors = []
for actor_list in top_actors_by_type.values():
    all_selected_actors.extend(actor_list)

print(f"Selected {len(all_selected_actors)} actors")

# Filter dataset
df_filtered = df[df['actor1'].isin(all_selected_actors)].copy()
df_filtered['fatalities'] = df_filtered['fatalities'].fillna(0)

# Clean data
essential_columns = ['actor1', 'inter1', 'country', 'event_type']
df_clean = df_filtered.dropna(subset=essential_columns)
df_clean['year'] = df_clean['year'].astype(int)

# Parse event_date to get actual dates
print("Parsing event dates...")
df_clean['event_date'] = pd.to_datetime(df_clean['event_date'])

# Create flows with dates
print("Aggregating flows with dates...")

flows = df_clean.groupby(['actor1', 'inter1', 'country', 'event_type']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum',
    'year': lambda x: sorted(x.unique()),
    'event_date': lambda x: sorted(x.dt.strftime('%Y-%m-%d').tolist()),  # Keep ALL dates (duplicates = multiple events)
    'sub_event_type': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
}).rename(columns={
    'event_id_cnty': 'events',
    'event_date': 'dates'
}).reset_index()

print(f"Total flows: {len(flows)}")

# Create year breakdown lookup
year_breakdown = df_clean.groupby(['actor1', 'inter1', 'country', 'event_type', 'year']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).rename(columns={'event_id_cnty': 'events'}).reset_index()

year_breakdown_lookup = {}
for _, row in year_breakdown.iterrows():
    key = (row['actor1'], row['inter1'], row['country'], row['event_type'])
    if key not in year_breakdown_lookup:
        year_breakdown_lookup[key] = {}
    year_breakdown_lookup[key][str(int(row['year']))] = {
        'events': int(row['events']),
        'fatalities': int(row['fatalities'])
    }

# Calculate statistics
fatality_stats = {
    'min': int(flows['fatalities'].min()),
    'max': int(flows['fatalities'].max()),
    'mean': float(flows['fatalities'].mean()),
    'median': float(flows['fatalities'].median()),
    'q25': float(flows['fatalities'].quantile(0.25)),
    'q75': float(flows['fatalities'].quantile(0.75))
}

event_stats = {
    'min': int(flows['events'].min()),
    'max': int(flows['events'].max()),
    'mean': float(flows['events'].mean()),
    'median': float(flows['events'].median())
}

# Get overall date range
all_dates = df_clean['event_date']
date_range = [all_dates.min().strftime('%Y-%m-%d'), all_dates.max().strftime('%Y-%m-%d')]

# Convert flows to final format
flows_list = []
for _, row in flows.iterrows():
    key = (row['actor1'], row['inter1'], row['country'], row['event_type'])
    year_breakdown_dict = year_breakdown_lookup.get(key, {})

    flow_dict = {
        'actor': row['actor1'],
        'actor_type': row['inter1'],
        'country': row['country'],
        'event_type': row['event_type'],
        'sub_event_type': row['sub_event_type'],
        'events': int(row['events']),
        'fatalities': int(row['fatalities']),
        'years': [int(y) for y in row['year']],
        'dates': row['dates'],  # NEW: exact dates
        'year_breakdown': year_breakdown_dict
    }
    flows_list.append(flow_dict)

print(f"Created {len(flows_list)} flow records")

# Sample to check dates
sample = flows_list[0]
print(f"\nSample flow dates: {sample['dates'][:5]}...")

# Create final dataset
final_dataset = {
    'metadata': {
        'created_date': datetime.now().isoformat(),
        'source': 'ACLED_2025-10-29.csv',
        'total_actors': len(all_selected_actors),
        'total_flows': len(flows_list),
        'year_range': [int(df_clean['year'].min()), int(df_clean['year'].max())],
        'date_range': date_range,  # NEW: actual date range
        'fatality_stats': fatality_stats,
        'event_stats': event_stats
    },
    'actor_types': top_actors_by_type,
    'flows': flows_list
}

# Export
output_file = os.path.join(BASE_DIR, 'data-processing', 'viz-datasets', 'viz10_actor_sankey.json')
print(f"\nExporting to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, indent=2, ensure_ascii=False)

import os
file_size = os.path.getsize(output_file) / 1024**2
print(f"File size: {file_size:.1f} MB")

# Also copy to public assets
import shutil
dest_file = os.path.join(BASE_DIR, 'public', 'src', 'assets', 'data', 'viz10_actor_sankey.json')
shutil.copy(output_file, dest_file)
print(f"Copied to {dest_file}")

print("\nDone! Data now includes exact dates.")
