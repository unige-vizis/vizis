import pandas as pd
from collections import Counter, defaultdict

# Load the ACLED data
print("Loading data...")
df = pd.read_csv('data-processing/raw-data/ACLED/ACLED_2025-10-29.csv')
print(f"Loaded {len(df):,} rows")

# Get unique actor types
actor_types = df['inter1'].unique()

md_lines = ["# ACLED Actors by Type - Country Analysis\n\n"]

for actor_type in sorted(actor_types):
    md_lines.append(f"## {actor_type}\n\n")

    # Filter to this actor type
    type_df = df[df['inter1'] == actor_type]

    # Get top 15 most common actors of this type
    actor_counts = type_df['actor1'].value_counts().head(15)

    md_lines.append(f"**Total events:** {len(type_df):,}\n\n")
    md_lines.append("| Actor | Events | Countries | Top Countries |\n")
    md_lines.append("|-------|--------|-----------|---------------|\n")

    for actor, event_count in actor_counts.items():
        # Get countries this actor operates in
        actor_df = type_df[type_df['actor1'] == actor]
        countries = actor_df['country'].value_counts()
        num_countries = len(countries)

        # Top 5 countries
        top_countries = countries.head(5)
        if num_countries <= 5:
            country_str = ", ".join([f"{c} ({n:,})" for c, n in top_countries.items()])
        else:
            country_str = ", ".join([f"{c} ({n:,})" for c, n in top_countries.items()])
            country_str += f" +{num_countries - 5} more"

        # Escape pipes and truncate if needed
        actor_safe = actor.replace('|', '\\|')
        if len(actor_safe) > 50:
            actor_safe = actor_safe[:47] + "..."

        md_lines.append(f"| {actor_safe} | {event_count:,} | {num_countries} | {country_str} |\n")

    md_lines.append("\n---\n\n")

# Write output
with open('ACLED_actors_by_type.md', 'w', encoding='utf-8') as f:
    f.writelines(md_lines)

print("Done! Output saved to ACLED_actors_by_type.md")
