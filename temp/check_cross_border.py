import pandas as pd
import re

df = pd.read_csv('data-processing/raw-data/ACLED/ACLED_2025-10-29.csv', low_memory=False)

# Get list of all countries in the dataset
all_countries = set(df['country'].unique())

# Extract country from actor names (usually in parentheses at the end)
def extract_country(actor, valid_countries):
    if pd.isna(actor):
        return None
    match = re.search(r'\(([^)]+)\)$', str(actor))
    if match:
        extracted = match.group(1)
        # Only return if it's actually a country name
        if extracted in valid_countries:
            return extracted
    return None

# Check for events where actor's country differs from event country
df['actor1_country'] = df['actor1'].apply(lambda x: extract_country(x, all_countries))
df['actor2_country'] = df['actor2'].apply(lambda x: extract_country(x, all_countries))
df['assoc1_country'] = df['assoc_actor_1'].apply(lambda x: extract_country(x, all_countries))
df['assoc2_country'] = df['assoc_actor_2'].apply(lambda x: extract_country(x, all_countries))

# Find cross-border events (actor from different country than event location)
mask1 = (df['actor1_country'].notna()) & (df['actor1_country'] != df['country'])
mask2 = (df['actor2_country'].notna()) & (df['actor2_country'] != df['country'])
mask3 = (df['assoc1_country'].notna()) & (df['assoc1_country'] != df['country'])
mask4 = (df['assoc2_country'].notna()) & (df['assoc2_country'] != df['country'])
cross_border = df[mask1 | mask2 | mask3 | mask4]

print(f'Total events: {len(df):,}')
print(f'Events with cross-border actors: {len(cross_border):,} ({100*len(cross_border)/len(df):.2f}%)')
print()

# Show examples
if len(cross_border) > 0:
    print('Examples of cross-border events:')
    sample = cross_border[['country', 'actor1', 'actor1_country', 'actor2', 'actor2_country', 'assoc_actor_1', 'assoc1_country']].head(15)
    for idx, row in sample.iterrows():
        print(f"  Event in: {row['country']}")
        if row['actor1_country'] and row['actor1_country'] != row['country']:
            print(f"    Actor1: {row['actor1']} -> from {row['actor1_country']}")
        if row['actor2_country'] and row['actor2_country'] != row['country']:
            print(f"    Actor2: {row['actor2']} -> from {row['actor2_country']}")
        if row['assoc1_country'] and row['assoc1_country'] != row['country']:
            print(f"    Assoc Actor1: {row['assoc_actor_1']} -> from {row['assoc1_country']}")
        print()

# Also check: how many events have TWO different countries involved (actors from 2+ countries)
df['countries_involved'] = df.apply(lambda row: set(filter(None, [
    row['country'],
    row['actor1_country'],
    row['actor2_country'],
    row['assoc1_country'],
    row['assoc2_country']
])), axis=1)
df['num_countries'] = df['countries_involved'].apply(len)

print(f"\nEvents by number of countries involved:")
print(df['num_countries'].value_counts().sort_index())
