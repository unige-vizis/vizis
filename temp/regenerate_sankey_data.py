"""
Regenerate Sankey visualization data with 6 actors per category.
"""
import pandas as pd
import json
from datetime import datetime
import os

# Set paths
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_path = os.path.join(base_path, 'data-processing', 'raw-data', 'ACLED', 'ACLED_2025-10-29.csv')
output_path = os.path.join(base_path, 'data-processing', 'viz-datasets', 'viz10_actor_sankey.json')

print("Loading ACLED dataset...")
df = pd.read_csv(raw_data_path)
print(f"Dataset shape: {df.shape}")

# Count events per actor within each actor type
actor_stats = df.groupby(['inter1', 'actor1']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum',
    'country': 'nunique'
}).rename(columns={
    'event_id_cnty': 'total_events',
    'country': 'countries_active'
}).reset_index()

print(f"Total unique actors: {len(actor_stats)}")

# Get top 10 actors per actor type
top_actors_by_type = {}

for actor_type in actor_stats['inter1'].unique():
    if pd.isna(actor_type):
        continue

    type_actors = actor_stats[actor_stats['inter1'] == actor_type].nlargest(10, 'total_events')
    top_actors_by_type[actor_type] = type_actors['actor1'].tolist()

    print(f"\n{actor_type} - Top 10 Actors:")
    for i, (_, row) in enumerate(type_actors.iterrows(), 1):
        print(f"{i}. {row['actor1'][:60]:<60} | {row['total_events']:>6} events | {row['fatalities']:>7} fatalities")

total_selected_actors = sum(len(actors) for actors in top_actors_by_type.values())
print(f"\nTotal selected actors: {total_selected_actors}")

# Create list of all selected actors
all_selected_actors = []
for actor_list in top_actors_by_type.values():
    all_selected_actors.extend(actor_list)

# Filter dataset to only selected actors
df_filtered = df[df['actor1'].isin(all_selected_actors)].copy()
print(f"\nFiltered dataset: {len(df_filtered):,} events ({len(df_filtered)/len(df)*100:.1f}% of original)")

# Clean data
df_filtered['fatalities'] = df_filtered['fatalities'].fillna(0)
essential_columns = ['actor1', 'inter1', 'country', 'event_type']
df_clean = df_filtered.dropna(subset=essential_columns)
df_clean['year'] = df_clean['year'].astype(int)

print(f"After cleaning: {len(df_clean):,} events")

# Create flows
print("\nAggregating flows...")
flows = df_clean.groupby(['actor1', 'inter1', 'country', 'event_type']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum',
    'year': lambda x: sorted(x.unique()),
    'sub_event_type': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
}).rename(columns={
    'event_id_cnty': 'events'
}).reset_index()

print(f"Total flows created: {len(flows)}")

# Create year-by-year breakdown
year_breakdown = df_clean.groupby(['actor1', 'inter1', 'country', 'event_type', 'year']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).rename(columns={'event_id_cnty': 'events'}).reset_index()

# Build year breakdown lookup
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
        'year_breakdown': year_breakdown_dict
    }
    flows_list.append(flow_dict)

# Create final dataset
final_dataset = {
    'metadata': {
        'created_date': datetime.now().isoformat(),
        'source': 'ACLED_2025-10-29.csv',
        'total_actors': len(all_selected_actors),
        'total_flows': len(flows_list),
        'year_range': [int(df_clean['year'].min()), int(df_clean['year'].max())],
        'fatality_stats': fatality_stats,
        'event_stats': event_stats
    },
    'actor_types': top_actors_by_type,
    'flows': flows_list
}

# Export to JSON
print(f"\nExporting to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, indent=2, ensure_ascii=False)

file_size = os.path.getsize(output_path) / 1024**2
print(f"File exported successfully! Size: {file_size:.2f} MB")

# Also copy to public folder
public_path = os.path.join(base_path, 'public', 'src', 'assets', 'data', 'viz10_actor_sankey.json')
with open(public_path, 'w', encoding='utf-8') as f:
    json.dump(final_dataset, f, indent=2, ensure_ascii=False)
print(f"Copied to {public_path}")

print("\n=== DONE ===")
print(f"Total actors: {total_selected_actors} (6 per category x {len(top_actors_by_type)} categories)")
