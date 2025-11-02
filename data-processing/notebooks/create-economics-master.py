"""
Economics Countries Master Dataset Generator

Purpose: Create a consolidated country-year economic structure dataset
         for merging with conflict data.

Output: economics-countries-master.csv
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ECONOMICS COUNTRIES MASTER DATASET GENERATOR")
print("=" * 80)

# ============================================================================
# STEP 1: Load World Bank GDP Sectoral Data
# ============================================================================
print("\n[1/8] Loading World Bank GDP sectoral data...")

df_gdp_sectoral = pd.read_excel(
    '../raw-data/World_Bank/Download-GDPcurrent-NCU-countries.xlsx',
    sheet_name=0,
    header=2
)

print(f"  > Loaded {len(df_gdp_sectoral):,} rows")
print(f"  > Found {len(df_gdp_sectoral['IndicatorName'].unique())} indicators")
print(f"  > Covering {df_gdp_sectoral['Country'].nunique()} countries")

# ============================================================================
# STEP 2: Reshape from Wide to Long Format
# ============================================================================
print("\n[2/8] Reshaping data from wide to long format...")

# Get year columns (all numeric columns from 1970 onwards)
year_columns = [col for col in df_gdp_sectoral.columns if isinstance(col, (int, float)) and col >= 1970]

print(f"  > Year range: {min(year_columns)} to {max(year_columns)}")

# Reshape to long format
df_long = df_gdp_sectoral.melt(
    id_vars=['CountryID', 'Country', 'Currency', 'IndicatorName'],
    value_vars=year_columns,
    var_name='Year',
    value_name='Value'
)

# Convert Year to integer
df_long['Year'] = df_long['Year'].astype(int)

print(f"  > Reshaped to {len(df_long):,} rows")

# ============================================================================
# STEP 3: Pivot Indicators to Columns
# ============================================================================
print("\n[3/8] Pivoting indicators to columns...")

df_pivot = df_long.pivot_table(
    index=['CountryID', 'Country', 'Currency', 'Year'],
    columns='IndicatorName',
    values='Value',
    aggfunc='first'
).reset_index()

print(f"  > Created {len(df_pivot):,} country-year records")
print(f"  > {df_pivot['Country'].nunique()} countries x {df_pivot['Year'].nunique()} years")

# ============================================================================
# STEP 4: Calculate Sector Percentages
# ============================================================================
print("\n[4/8] Calculating sector percentages...")

# Clean column names
df_pivot.columns = df_pivot.columns.str.strip()

# Map long indicator names to short names
col_map = {
    'Agriculture, hunting, forestry, fishing (ISIC A-B)': 'Agriculture',
    'Mining, Manufacturing, Utilities (ISIC C-E)': 'Mining_Manuf_Util',
    'Manufacturing (ISIC D)': 'Manufacturing',
    'Construction (ISIC F)': 'Construction',
    'Wholesale, retail trade, restaurants and hotels (ISIC G-H)': 'Trade_Retail',
    'Transport, storage and communication (ISIC I)': 'Transport',
    'Other Activities (ISIC J-P)': 'Other_Activities',
    'Total Value Added': 'Total_Value_Added',
    'Gross Domestic Product (GDP)': 'GDP'
}

df_pivot = df_pivot.rename(columns=col_map)

# Calculate Mining (Mining+Manuf+Util - Manufacturing)
df_pivot['Mining'] = df_pivot['Mining_Manuf_Util'] - df_pivot['Manufacturing']

# Calculate sector components
df_pivot['Primary_Value'] = df_pivot['Agriculture'] + df_pivot['Mining']
df_pivot['Secondary_Value'] = df_pivot['Manufacturing'] + df_pivot['Construction']
df_pivot['Tertiary_Value'] = df_pivot['Trade_Retail'] + df_pivot['Transport'] + df_pivot['Other_Activities']

# Calculate percentages (relative to Total Value Added)
df_pivot['Primary_%'] = (df_pivot['Primary_Value'] / df_pivot['Total_Value_Added']) * 100
df_pivot['Secondary_%'] = (df_pivot['Secondary_Value'] / df_pivot['Total_Value_Added']) * 100
df_pivot['Tertiary_%'] = (df_pivot['Tertiary_Value'] / df_pivot['Total_Value_Added']) * 100

print("  > Calculated Primary % (Agriculture + Mining)")
print("  > Calculated Secondary % (Manufacturing + Construction)")
print("  > Calculated Tertiary % (Services)")

# ============================================================================
# STEP 5: Load and Merge UN Tourism Data
# ============================================================================
print("\n[5/8] Loading UN Tourism data...")

df_tourism = pd.read_excel(
    '../raw-data/UN_Tourism/UN_Tourism_8_9_1_TDGDP_04_2025.xlsx',
    sheet_name='SDG 8.9.1',
    header=0
)

print(f"  > Loaded {len(df_tourism):,} tourism records")
print(f"  > {df_tourism['GeoAreaName'].nunique()} countries, {df_tourism['TimePeriod'].min()}-{df_tourism['TimePeriod'].max()}")

# Select relevant columns and rename
df_tourism_clean = df_tourism[['GeoAreaName', 'TimePeriod', 'Value']].copy()
df_tourism_clean.columns = ['Country', 'Year', 'Tourism_%']

# Merge tourism data
print("\n[6/8] Merging tourism data...")
df_master = df_pivot.merge(
    df_tourism_clean,
    on=['Country', 'Year'],
    how='left'
)

tourism_coverage = df_master['Tourism_%'].notna().sum()
print(f"  > Merged: {tourism_coverage:,} records now have tourism data")

# ============================================================================
# STEP 7: Add GDP in USD
# ============================================================================
print("\n[7/8] Loading and merging GDP in USD...")

df_dev_ind = pd.read_csv('../raw-data/World_Bank/world_bank_development_indicators.csv')

# Extract year from date column
df_dev_ind['Year'] = pd.to_datetime(df_dev_ind['date']).dt.year

# Select GDP in USD column
df_gdp_usd = df_dev_ind[['country', 'Year', 'GDP_current_US']].copy()
df_gdp_usd.columns = ['Country', 'Year', 'GDP_USD']

# Merge GDP USD
df_master = df_master.merge(
    df_gdp_usd,
    on=['Country', 'Year'],
    how='left'
)

gdp_coverage = df_master['GDP_USD'].notna().sum()
print(f"  > Merged: {gdp_coverage:,} records now have GDP in USD")

# ============================================================================
# STEP 8: Create Final Master Dataset with Explicit NULLs
# ============================================================================
print("\n[8/8] Creating final dataset with explicit NULL values...")

# Select final columns in desired order
df_final = df_master[[
    'Country',
    'Year',
    'Primary_%',
    'Secondary_%',
    'Tertiary_%',
    'Tourism_%',
    'GDP_USD'
]].copy()

# Round percentages to 2 decimal places
df_final['Primary_%'] = df_final['Primary_%'].round(2)
df_final['Secondary_%'] = df_final['Secondary_%'].round(2)
df_final['Tertiary_%'] = df_final['Tertiary_%'].round(2)
df_final['Tourism_%'] = df_final['Tourism_%'].round(2)

# Ensure all numeric columns use proper float64 with NaN for missing
numeric_cols = ['Primary_%', 'Secondary_%', 'Tertiary_%', 'Tourism_%', 'GDP_USD']
for col in numeric_cols:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

# Sort by Country and Year
df_final = df_final.sort_values(['Country', 'Year']).reset_index(drop=True)

print(f"  > Final dataset: {len(df_final):,} rows x {len(df_final.columns)} columns")
print(f"  > Countries: {df_final['Country'].nunique()}")
print(f"  > Year range: {df_final['Year'].min()} - {df_final['Year'].max()}")

# ============================================================================
# VALIDATION
# ============================================================================
print("\n[VALIDATION] Data quality checks...")

# Check sector percentages sum to ~100%
df_final['Total_%'] = df_final['Primary_%'] + df_final['Secondary_%'] + df_final['Tertiary_%']
valid_rows = df_final[(df_final['Total_%'] >= 99) & (df_final['Total_%'] <= 101)].shape[0]
total_rows_with_sectors = df_final['Total_%'].notna().sum()

print(f"  > Sector validation: {valid_rows:,}/{total_rows_with_sectors:,} rows with sectors sum to 100% (+/-1%)")

# Drop temporary column
df_final = df_final.drop(columns=['Total_%'])

# Missing data report
print(f"\n  > Missing data summary:")
for col in df_final.columns:
    null_count = df_final[col].isna().sum()
    null_pct = (null_count / len(df_final)) * 100
    print(f"     {col}: {null_count:,} ({null_pct:.1f}%)")

# ============================================================================
# EXPORT
# ============================================================================
output_path = '../processed-data/economics-countries-master.csv'
df_final.to_csv(output_path, index=False, na_rep='')  # na_rep='' writes empty string for NULL

print("\n" + "=" * 80)
print("OK EXPORT COMPLETED")
print("=" * 80)
print(f"\nFile: {output_path}")
print(f"Size: {len(df_final):,} records")
print(f"Countries: {df_final['Country'].nunique()}")
print(f"Years: {df_final['Year'].min()}-{df_final['Year'].max()}")
print(f"\nColumns:")
print(f"  - Country (text - standardized World Bank name)")
print(f"  - Year (1970-2023)")
print(f"  - Primary_% (Agriculture + Mining)")
print(f"  - Secondary_% (Manufacturing + Construction)")
print(f"  - Tertiary_% (Services)")
print(f"  - Tourism_% (2008-2023, 125 countries)")
print(f"  - GDP_USD (current US dollars)")
print(f"\nNOTE: Missing values are represented as empty cells in CSV (NULL)")
print("\nOK Ready to merge with conflict data!")
print("=" * 80)
