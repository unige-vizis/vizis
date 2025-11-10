import pandas as pd
import numpy as np
import json
from pathlib import Path

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# Define paths
raw_data_path = Path('../raw-data')
processed_data_path = Path('../processed-data')
viz_datasets_path = Path('../viz-datasets')
viz_datasets_path.mkdir(exist_ok=True)

# Load data
print("Loading data...")
df_acled = pd.read_csv(raw_data_path / 'ACLED' / 'ACLED_2025-10-29.csv', encoding='utf-8-sig')
df_econ = pd.read_csv(processed_data_path / 'economics-countries-master.csv')

print(f"ACLED: {len(df_acled):,} events")
print(f"Economics: {len(df_econ):,} country-years")

# Get the current year from the data
current_year = df_acled['year'].max()
print(f"Latest year in data: {current_year}")

# Define last 10 years
last_10_years_start = current_year - 9

# Filter economics data to last 10 years
print("\nFiltering to last 10 years...")
df_econ_recent = df_econ[df_econ['Year'] >= last_10_years_start].copy()

# Calculate GDP per capita
df_econ_recent['GDP_per_capita'] = df_econ_recent['GDP_USD'] / df_econ_recent['Population']

# Categorize countries by sector dominance
# Fill NaN sector values with 0 for calculation
df_econ_recent['Primary_%'] = df_econ_recent['Primary_%'].fillna(0)
df_econ_recent['Secondary_%'] = df_econ_recent['Secondary_%'].fillna(0)
df_econ_recent['Tertiary_%'] = df_econ_recent['Tertiary_%'].fillna(0)

df_econ_recent['Primary_Secondary_Sum'] = df_econ_recent['Primary_%'] + df_econ_recent['Secondary_%']
df_econ_recent['Category'] = df_econ_recent.apply(
    lambda row: 'Primary+Secondary Dominated' if row['Primary_Secondary_Sum'] > 50 else 'Tertiary Dominated',
    axis=1
)

# Use economics-master data directly
df_combined = df_econ_recent

print(f"\nCombined data: {len(df_combined):,} country-years")
print(f"\nCountry categories:")
print(df_combined.groupby('Category').size())
print(f"\nRecords with GDP per capita: {df_combined['GDP_per_capita'].notna().sum():,}")
print(f"Records with inflation data: {df_combined['Inflation_%'].notna().sum():,}")
print(f"Records with debt data: {df_combined['Debt_%'].notna().sum():,}")
print(f"\nYears covered: {df_combined['Year'].min()} - {df_combined['Year'].max()}")

# ============================================================
# VIZ 2: Pyramid Chart - GDP per Capita by Country Category
# ============================================================

print("\n" + "="*60)
print("GENERATING VIZ 2: Pyramid Chart - GDP per Capita")
print("="*60)

# Filter to most recent year for each country (for viz 2)
df_latest = df_combined.sort_values('Year').groupby('Country').last().reset_index()

# Remove rows without GDP per capita
df_viz2 = df_latest[df_latest['GDP_per_capita'].notna()].copy()

# Create bins for GDP per capita (for pyramid chart) - 2k below 10k, 10k above
bins = [0, 2000, 4000, 6000, 8000, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, np.inf]
labels = ['0-2k', '2k-4k', '4k-6k', '6k-8k', '8k-10k', '10k-20k', '20k-30k', '30k-40k', '40k-50k', '50k-60k', '60k-70k', '70k-80k', '80k+']
# Mark which bins are in the "low" group (below 10k) vs "high" group (10k+)
bin_groups = ['low', 'low', 'low', 'low', 'low', 'high', 'high', 'high', 'high', 'high', 'high', 'high', 'high']
df_viz2['GDP_bracket'] = pd.cut(df_viz2['GDP_per_capita'], bins=bins, labels=labels)

# Count countries in each bracket by category and get country names
pyramid_data = df_viz2.groupby(['Category', 'GDP_bracket'], observed=True).agg(
    count=('Country', 'size'),
    countries=('Country', lambda x: sorted(x.tolist()))
).reset_index()

# Convert countries list to regular list (from pandas object)
pyramid_data['countries'] = pyramid_data['countries'].apply(list)

# Get country names for each category
countries_by_category = df_viz2.groupby('Category')['Country'].apply(sorted).to_dict()

# Prepare metadata for viz 2
viz2_metadata = {
    'title': 'GDP per Capita Distribution by Economic Sector Dominance',
    'description': 'Pyramid chart comparing GDP per capita distribution between countries dominated by Primary+Secondary sectors vs Tertiary sector. Data represents the most recent year available for each country.',
    'source': 'World Bank Development Indicators',
    'date_range': f'{last_10_years_start}-{current_year}',
    'notes': 'Countries categorized by whether Primary% + Secondary% > 50% (Primary+Secondary) or Tertiary% >= 50% (Tertiary). Bins below 10k are 2k intervals, bins above 10k are 10k intervals.',
    'bins': labels,
    'bin_groups': bin_groups,
    'total_countries': len(df_viz2)
}

# Create output structure for viz 2
viz2_output = {
    'metadata': viz2_metadata,
    'data': pyramid_data.to_dict('records'),
    'countries_by_category': countries_by_category
}

# Save viz 2 JSON
output_file_viz2 = viz_datasets_path / 'viz2-2_pyramid_gdp_per_capita.json'
with open(output_file_viz2, 'w', encoding='utf-8') as f:
    json.dump(viz2_output, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved VIZ 2: {output_file_viz2.name} ({output_file_viz2.stat().st_size / 1024:.1f} KB)")
print(f"  Total countries: {len(df_viz2):,}")
print(f"\nCountries per category:")
print(df_viz2.groupby('Category').size())

# ============================================================
# VIZ 3: Ridge Chart - Annual Inflation over Last 10 Years
# ============================================================

print("\n" + "="*60)
print("GENERATING VIZ 3: Ridge Chart - Annual Inflation")
print("="*60)

# Filter to records with inflation data
df_viz3 = df_combined[df_combined['Inflation_%'].notna()].copy()

# Group by year and category, get all inflation values
ridge_data = []
for year in sorted(df_viz3['Year'].unique()):
    year_data = df_viz3[df_viz3['Year'] == year]

    for category in ['Primary+Secondary Dominated', 'Tertiary Dominated']:
        category_data = year_data[year_data['Category'] == category]
        values = category_data['Inflation_%'].tolist()

        if values:  # Only include if there's data
            ridge_data.append({
                'year': int(year),
                'category': category,
                'values': values,
                'count': len(values),
                'mean': float(np.mean(values)),
                'median': float(np.median(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            })

# Prepare metadata for viz 3
viz3_metadata = {
    'title': 'Annual Inflation Distribution by Economic Sector (2015-2024)',
    'description': 'Ridge plot showing the distribution of annual inflation rates across two economic sector categories over the last 10 years. Each year has two ridges representing Primary+Secondary dominated countries and Tertiary dominated countries.',
    'source': 'World Bank Development Indicators',
    'date_range': f'{last_10_years_start}-{current_year}',
    'notes': 'Annual inflation percentage from World Bank data',
    'categories': ['Primary+Secondary Dominated', 'Tertiary Dominated'],
    'years': sorted(df_viz3['Year'].unique().tolist())
}

# Create output structure for viz 3
viz3_output = {
    'metadata': viz3_metadata,
    'data': ridge_data
}

# Save viz 3 JSON
output_file_viz3 = viz_datasets_path / 'viz2-3_ridge_inflation.json'
with open(output_file_viz3, 'w', encoding='utf-8') as f:
    json.dump(viz3_output, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved VIZ 3: {output_file_viz3.name} ({output_file_viz3.stat().st_size / 1024:.1f} KB)")
print(f"  Total ridge lines: {len(ridge_data)}")
print(f"  Years: {len(viz3_metadata['years'])}")
print(f"\nData points per year-category:")
for item in ridge_data[:5]:  # Show first 5 as example
    print(f"  {item['year']} - {item['category']}: {item['count']} countries")

# ============================================================
# VIZ 3b: Violin Plot - National Debt per Capita by Category
# ============================================================

print("\n" + "="*60)
print("GENERATING VIZ 3b: Violin Plot - National Debt per Capita")
print("="*60)

# Calculate National Debt per capita using Debt_% from economics-master
df_combined['Debt_per_capita'] = (df_combined['GDP_USD'] * df_combined['Debt_%'] / 100) / df_combined['Population']

# Filter to records with debt per capita data
df_violin_debt = df_combined[df_combined['Debt_per_capita'].notna()].copy()

# Group by category and country, take the last reported debt per capita
violin_debt_data = []
for category in ['Primary+Secondary Dominated', 'Tertiary Dominated']:
    category_data = df_violin_debt[df_violin_debt['Category'] == category]

    # Get the last reported debt per capita for each country (most recent year)
    country_latest = category_data.sort_values('Year').groupby('Country').last().reset_index()

    # Create list of data points with country info
    data_points = []
    for _, row in country_latest.iterrows():
        data_points.append({
            'country': row['Country'],
            'year': int(row['Year']),
            'value': float(row['Debt_per_capita'])
        })

    values = country_latest['Debt_per_capita'].tolist()

    if values:
        violin_debt_data.append({
            'category': category,
            'data_points': data_points,
            'values': values,  # Keep for backward compatibility
            'count': len(values),
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        })

# Prepare metadata
violin_debt_metadata = {
    'title': 'National Debt per Capita Distribution by Economic Sector',
    'description': 'Violin plot comparing the distribution of national debt per capita between countries dominated by Primary+Secondary sectors vs Tertiary sector.',
    'source': 'World Bank Development Indicators',
    'date_range': f'{last_10_years_start}-{current_year}',
    'notes': 'Debt per capita calculated as (GDP × Central Government Debt%) / Population. Each country shows its most recent reported value within the 10 year period.',
    'categories': ['Primary+Secondary Dominated', 'Tertiary Dominated']
}

# Create output structure
violin_debt_output = {
    'metadata': violin_debt_metadata,
    'data': violin_debt_data
}

# Save JSON
output_file_violin_debt = viz_datasets_path / 'viz2-3b_violin_debt_per_capita.json'
with open(output_file_violin_debt, 'w', encoding='utf-8') as f:
    json.dump(violin_debt_output, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved VIZ 3b: {output_file_violin_debt.name} ({output_file_violin_debt.stat().st_size / 1024:.1f} KB)")
print(f"  Categories: {len(violin_debt_data)}")
for item in violin_debt_data:
    print(f"  {item['category']}: {item['count']} countries")

print("\n" + "="*60)
print("COMPLETE!")
print("="*60)
