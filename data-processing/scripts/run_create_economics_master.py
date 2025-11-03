import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("Libraries loaded successfully")

# Load World Bank GDP sectoral data
df_gdp_sectoral = pd.read_excel(
    '../raw-data/World_Bank/Download-GDPcurrent-NCU-countries.xlsx',
    sheet_name=0,
    header=2
)

print(f"Loaded {len(df_gdp_sectoral):,} rows")

# Get year columns (all numeric columns from 1970 onwards)
year_columns = [col for col in df_gdp_sectoral.columns if isinstance(col, (int, float)) and col >= 1970]

print(f"Year range: {min(year_columns)} to {max(year_columns)}")
print(f"Total years: {len(year_columns)}")

# Reshape to long format
df_long = df_gdp_sectoral.melt(
    id_vars=['CountryID', 'Country', 'Currency', 'IndicatorName'],
    value_vars=year_columns,
    var_name='Year',
    value_name='Value'
)

# Convert Year to integer
df_long['Year'] = df_long['Year'].astype(int)

print(f"\nReshaped to {len(df_long):,} rows")

# Pivot so each indicator is a column
df_pivot = df_long.pivot_table(
    index=['CountryID', 'Country', 'Currency', 'Year'],
    columns='IndicatorName',
    values='Value',
    aggfunc='first'
).reset_index()

print(f"Pivoted to {len(df_pivot):,} rows (country-years)")

# Shorter column names for easier reference
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

print("\n=== Loading UN Tourism Data ===")

# Load UN Tourism data
df_tourism = pd.read_excel(
    '../raw-data/UN_Tourism/UN_Tourism_8_9_1_TDGDP_04_2025.xlsx',
    sheet_name='SDG 8.9.1',
    header=0
)

print(f"Loaded {len(df_tourism):,} tourism records")

# Select relevant columns and rename
df_tourism_clean = df_tourism[['GeoAreaName', 'TimePeriod', 'Value']].copy()
df_tourism_clean.columns = ['Country', 'Year', 'Tourism_%']

# *** FIX: Standardize tourism country names to match main dataset ***
tourism_country_name_map = {
    'United States of America': 'United States',
    # Add other mappings if needed
}

df_tourism_clean['Country'] = df_tourism_clean['Country'].replace(tourism_country_name_map)

print(f"Applied country name mapping for tourism data")

# Merge tourism data with main dataset
df_master = df_pivot.merge(
    df_tourism_clean,
    on=['Country', 'Year'],
    how='left'
)

print(f"After merging tourism: {len(df_master):,} rows")
print(f"Records with tourism data: {df_master['Tourism_%'].notna().sum():,}")

# Check USA specifically
usa_tourism = df_master[df_master['Country'] == 'United States']['Tourism_%'].notna().sum()
print(f"USA records with tourism data: {usa_tourism}")

print("\n=== Loading GDP USD Data ===")

# Load World Bank Development Indicators
df_dev_ind = pd.read_csv('../raw-data/World_Bank/world_bank_development_indicators.csv')

print(f"Loaded {len(df_dev_ind):,} development indicator records")

# Extract year from date column
df_dev_ind['Year'] = pd.to_datetime(df_dev_ind['date']).dt.year

# Select GDP in USD and population columns
df_gdp_usd = df_dev_ind[['country', 'Year', 'GDP_current_US', 'population']].copy()
df_gdp_usd.columns = ['Country', 'Year', 'GDP_USD', 'Population']

# Standardize country names to match ACLED naming conventions
country_name_map = {
    'Yemen, Rep.': 'Yemen',
    'Egypt, Arab Rep.': 'Egypt',
    'Congo, Dem. Rep.': 'Democratic Republic of Congo',
    'Congo, Rep.': 'Republic of Congo',
    'Bahamas, The': 'Bahamas',
    'Gambia, The': 'Gambia',
    'Korea, Rep.': 'South Korea',
    'Korea, Dem. People\'s Rep.': 'North Korea',
    'Kyrgyz Republic': 'Kyrgyzstan',
    'Lao PDR': 'Laos',
    'Russian Federation': 'Russia',
    'Syrian Arab Republic': 'Syria',
    'Turkiye': 'Turkey',
    'Venezuela, RB': 'Venezuela',
    'West Bank and Gaza': 'Palestine',
    'Slovak Republic': 'Slovakia'
}

df_gdp_usd['Country'] = df_gdp_usd['Country'].replace(country_name_map)

# Merge GDP USD and Population with master dataset
df_master = df_master.merge(
    df_gdp_usd,
    on=['Country', 'Year'],
    how='left'
)

print(f"After merging GDP USD and Population: {len(df_master):,} rows")

print("\n=== Creating Final Dataset ===")

# Select final columns
df_final = df_master[[
    'Country',
    'Year',
    'Primary_%',
    'Secondary_%',
    'Tertiary_%',
    'Tourism_%',
    'GDP_USD',
    'Population'
]].copy()

# Round percentages to 2 decimal places
df_final['Primary_%'] = df_final['Primary_%'].round(2)
df_final['Secondary_%'] = df_final['Secondary_%'].round(2)
df_final['Tertiary_%'] = df_final['Tertiary_%'].round(2)
df_final['Tourism_%'] = df_final['Tourism_%'].round(2)

# Sort by Country and Year
df_final = df_final.sort_values(['Country', 'Year']).reset_index(drop=True)

print(f"Final dataset: {len(df_final):,} rows × {len(df_final.columns)} columns")

# Validation - check USA tourism data
usa_data = df_final[(df_final['Country'] == 'United States') & (df_final['Year'] >= 2015)]
print("\n=== USA Tourism Data (2015+) ===")
print(usa_data[['Year', 'Tourism_%']])

# Export to CSV
output_path = '../processed-data/economics-countries-master.csv'
df_final.to_csv(output_path, index=False)

print(f"\n✓ Exported to: {output_path}")
print(f"\n✓ Economics Countries Master dataset created successfully!")
print(f"  - Total records: {len(df_final):,}")
print(f"  - Countries: {df_final['Country'].nunique()}")
print(f"  - Years: {df_final['Year'].min()} - {df_final['Year'].max()}")
