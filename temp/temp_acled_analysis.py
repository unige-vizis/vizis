import pandas as pd
from collections import Counter

# Load the ACLED data
df = pd.read_csv('data-processing/raw-data/ACLED/ACLED_2025-10-29.csv')

# Columns to analyze
columns = [
    'disorder_type', 'event_type', 'actor1', 'assoc_actor_1',
    'inter1', 'actor2', 'assoc_actor_2', 'inter2', 'region'
]

def analyze_column(df, col_name, max_values=20):
    """Analyze a column and return info about unique values."""
    if col_name not in df.columns:
        return None, None, None, False

    col_data = df[col_name].dropna()

    # Check if values contain lists (semicolon or comma separated)
    sample_values = col_data.head(100).astype(str)
    has_list_values = any(';' in str(v) for v in sample_values)

    if has_list_values:
        # Explode the list values
        all_values = []
        for val in col_data:
            if pd.notna(val):
                parts = [p.strip() for p in str(val).split(';') if p.strip()]
                all_values.extend(parts)
        value_counts = Counter(all_values)
    else:
        value_counts = Counter(col_data.astype(str))

    total_unique = len(value_counts)
    most_common = value_counts.most_common(max_values)

    return total_unique, most_common, len(col_data), has_list_values

# Generate markdown
md_lines = ["# ACLED Data Analysis\n"]
md_lines.append(f"**Total rows in dataset:** {len(df):,}\n")
md_lines.append(f"**Columns in dataset:** {len(df.columns)}\n")
md_lines.append("---\n")

for col in columns:
    total_unique, most_common, non_null_count, is_list = analyze_column(df, col)

    if total_unique is None:
        md_lines.append(f"## {col}\n")
        md_lines.append("**Column not found in dataset**\n\n")
        continue

    md_lines.append(f"## {col}\n")
    md_lines.append(f"- **Field type:** {'List (semicolon-separated)' if is_list else 'Simple value'}\n")
    md_lines.append(f"- **Non-null values:** {non_null_count:,}\n")
    md_lines.append(f"- **Total unique values:** {total_unique:,}\n")

    if total_unique > 20:
        md_lines.append(f"- **Showing:** Top 20 most frequent\n")

    md_lines.append("\n| Value | Count |\n|-------|-------|\n")

    for value, count in most_common:
        # Escape pipe characters in values for markdown table
        safe_value = str(value).replace('|', '\\|')
        # Truncate very long values
        if len(safe_value) > 80:
            safe_value = safe_value[:77] + "..."
        md_lines.append(f"| {safe_value} | {count:,} |\n")

    md_lines.append("\n---\n")

# Write to markdown file
with open('ACLED_analysis.md', 'w', encoding='utf-8') as f:
    f.writelines(md_lines)

print("Analysis complete! Output saved to ACLED_analysis.md")
