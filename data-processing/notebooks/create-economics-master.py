import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

print("="*80)
print("ECONOMICS COUNTRIES MASTER DATASET GENERATOR")
print("="*80)

# [1/8] Load World Bank GDP sectoral data
print("\n[1/8] Loading World Bank GDP sectoral data...")
df_gdp_sectoral_raw = pd.read_excel('../raw-data/World_Bank/Download-GDPcurrent-NCU-countries.xlsx', header=1)
new_columns = df_gdp_sectoral_raw.iloc[0].tolist()
df_gdp_sectoral = df_gdp_sectoral_raw.copy()
df_gdp_sectoral.columns = new_columns
df_gdp_sectoral = df_gdp_sectoral.drop(0).reset_index(drop=True)

if "Country" not in df_gdp_sectoral.columns or "IndicatorName" not in df_gdp_sectoral.columns:
    raise KeyError("Expected columns 'Country' or 'IndicatorName' not found.")

print(f"Loaded {len(df_gdp_sectoral):,} rows covering {df_gdp_sectoral['Country'].nunique()} countries")

# [2/8] Reshape from wide to long format
print("\n[2/8] Reshaping data...")
year_columns = sorted([col for col in df_gdp_sectoral.columns
                       if isinstance(col, (int, float)) and float(col) >= 1970 and float(col).is_integer()],
                      key=lambda x: float(x))

df_long = df_gdp_sectoral.melt(
    id_vars=['CountryID', 'Country', 'Currency', 'IndicatorName'],
    value_vars=year_columns,
    var_name='Year',
    value_name='Value'
)
df_long['Year'] = df_long['Year'].astype(float).astype(int)
print(f"Reshaped to {len(df_long):,} rows")

# [3/8] Pivot indicators to columns
print("\n[3/8] Pivoting indicators...")
df_pivot = df_long.pivot_table(
    index=['CountryID', 'Country', 'Currency', 'Year'],
    columns='IndicatorName',
    values='Value',
    aggfunc='first'
).reset_index()

print(f"Created {len(df_pivot):,} country-year records")

# [4/8] Calculate sector percentages
print("\n[4/8] Calculating sector percentages...")
df_pivot.columns = df_pivot.columns.str.strip()

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

df_pivot['Mining'] = df_pivot['Mining_Manuf_Util'] - df_pivot['Manufacturing']
df_pivot['Primary_Value'] = df_pivot['Agriculture'] + df_pivot['Mining']
df_pivot['Secondary_Value'] = df_pivot['Manufacturing'] + df_pivot['Construction']
df_pivot['Tertiary_Value'] = df_pivot['Trade_Retail'] + df_pivot['Transport'] + df_pivot['Other_Activities']

df_pivot['Primary_%'] = (df_pivot['Primary_Value'] / df_pivot['Total_Value_Added']) * 100
df_pivot['Secondary_%'] = (df_pivot['Secondary_Value'] / df_pivot['Total_Value_Added']) * 100
df_pivot['Tertiary_%'] = (df_pivot['Tertiary_Value'] / df_pivot['Total_Value_Added']) * 100

# [5/8] Load UN Tourism data
print("\n[5/8] Loading UN Tourism data...")
df_tourism = pd.read_excel(
    '../raw-data/UN_Tourism/UN_Tourism_8_9_1_TDGDP_04_2025.xlsx',
    sheet_name='SDG 8.9.1'
)

df_tourism_clean = df_tourism[['GeoAreaName', 'TimePeriod', 'Value']].copy()
df_tourism_clean.columns = ['Country', 'Year', 'Tourism_%']
df_tourism_clean['Country'] = df_tourism_clean['Country'].replace({
    'United States of America': 'United States'
})

print(f"Loaded {len(df_tourism_clean):,} tourism records")

# [6/8] Merge tourism data
print("\n[6/8] Merging tourism data...")
df_master = df_pivot.merge(df_tourism_clean, on=['Country', 'Year'], how='left')
print(f"Merged: {df_master['Tourism_%'].notna().sum():,} records have tourism data")

# [7/8] Load and merge GDP USD, Population, Inflation, and Debt
print("\n[7/8] Loading GDP, population, inflation, and debt data...")
df_dev_ind = pd.read_csv('../raw-data/World_Bank/world_bank_development_indicators.csv')
df_dev_ind['Year'] = pd.to_datetime(df_dev_ind['date']).dt.year

df_gdp_usd = df_dev_ind[['country', 'Year', 'GDP_current_US', 'population', 'inflation_annual%', 'central_goverment_debt%']].copy()
df_gdp_usd.columns = ['Country', 'Year', 'GDP_USD', 'Population', 'Inflation_%', 'Debt_%']

country_name_map = {
    'Yemen, Rep.': 'Yemen',
    'Egypt, Arab Rep.': 'Egypt',
    'Bahamas, The': 'Bahamas',
    'Gambia, The': 'Gambia',
    'Kyrgyz Republic': 'Kyrgyzstan',
    'Slovak Republic': 'Slovakia',
    'Bolivia': 'Bolivia (Plurinational State of)',
    'Hong Kong SAR, China': 'China, Hong Kong SAR',
    'Macao SAR, China': 'China, Macao SAR',
    'Congo, Rep.': 'Congo',
    'Congo, Dem. Rep.': 'D.R. of the Congo',
    'Curacao': 'Curaçao',
    'Cote d\'Ivoire': 'Côte d\'Ivoire',
    'Korea, Dem. People\'s Rep.': 'D.P.R. of Korea',
    'Iran, Islamic Rep.': 'Iran (Islamic Republic of)',
    'Lao PDR': 'Lao People\'s DR',
    'Micronesia, Fed. Sts.': 'Micronesia (FS of)',
    'Korea, Rep.': 'Republic of Korea',
    'Moldova': 'Republic of Moldova',
    'St. Kitts and Nevis': 'Saint Kitts and Nevis',
    'St. Lucia': 'Saint Lucia',
    'West Bank and Gaza': 'State of Palestine',
    'Turkiye': 'Türkiye',
    'Tanzania': 'U.R. of Tanzania: Mainland',
    'Venezuela, RB': 'Venezuela (Bolivarian Republic of)',
}
df_gdp_usd['Country'] = df_gdp_usd['Country'].replace(country_name_map)

df_master = df_master.merge(df_gdp_usd, on=['Country', 'Year'], how='left')
print(f"Merged: {df_master['GDP_USD'].notna().sum():,} records have GDP data")
print(f"Merged: {df_master['Inflation_%'].notna().sum():,} records have inflation data")
print(f"Merged: {df_master['Debt_%'].notna().sum():,} records have debt data")

# [8/8] Create final dataset
print("\n[8/8] Creating final dataset...")
df_final = df_master[[
    'Country', 'Year', 'Primary_%', 'Secondary_%', 'Tertiary_%',
    'Tourism_%', 'GDP_USD', 'Population', 'Inflation_%', 'Debt_%'
]].copy()

# Round percentages
for col in ['Primary_%', 'Secondary_%', 'Tertiary_%', 'Tourism_%', 'Inflation_%', 'Debt_%']:
    df_final[col] = df_final[col].round(2)

# Ensure numeric types
numeric_cols = ['Primary_%', 'Secondary_%', 'Tertiary_%', 'Tourism_%', 'GDP_USD', 'Population', 'Inflation_%', 'Debt_%']
for col in numeric_cols:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

df_final = df_final.sort_values(['Country', 'Year']).reset_index(drop=True)

print(f"Final dataset: {len(df_final):,} rows × {len(df_final.columns)} columns")
print(f"Countries: {df_final['Country'].nunique()}")
print(f"Year range: {df_final['Year'].min()}-{df_final['Year'].max()}")

# Data quality report
print("\n" + "="*80)
print("DATA QUALITY REPORT")
print("="*80)

print("\n1. Missing Data Summary:")
missing_df = pd.DataFrame({
    'Missing Count': df_final.isnull().sum(),
    'Missing %': (df_final.isnull().sum() / len(df_final) * 100).round(2)
})
print(missing_df)

print("\n2. Sector Percentage Validation:")
df_final['Total_%'] = df_final['Primary_%'] + df_final['Secondary_%'] + df_final['Tertiary_%']
valid_rows = df_final[(df_final['Total_%'] >= 99) & (df_final['Total_%'] <= 101)].shape[0]
total_rows_with_sectors = df_final['Total_%'].notna().sum()
print(f"Rows with sectors summing to 100% (±1%): {valid_rows:,}/{total_rows_with_sectors:,}")

print("\n3. GDP Coverage Analysis (Last 10 Years):")
current_year = df_final['Year'].max()
last_10_years = df_final[df_final['Year'] > current_year - 10]

countries_with_gdp = last_10_years[last_10_years['GDP_USD'].notna()]['Country'].unique()
countries_without_gdp = last_10_years[~last_10_years['Country'].isin(countries_with_gdp)]['Country'].unique()

print(f"Year range analyzed: {current_year - 9}-{current_year}")
print(f"Total unique countries in dataset: {df_final['Country'].nunique()}")
print(f"Countries WITH GDP data in last 10 years: {len(countries_with_gdp)}")
print(f"Countries WITHOUT any GDP data in last 10 years: {len(countries_without_gdp)}")

if len(countries_without_gdp) > 0:
    print(f"\nCountries missing GDP data:")
    for i, country in enumerate(sorted(countries_without_gdp), 1):
        print(f"  {i}. {country}")

print("\n4. Sample Countries (2015-2023):")
for country in ['United States', 'Germany', 'China']:
    sample = df_final[(df_final['Country'] == country) & (df_final['Year'] >= 2015)]
    if len(sample) > 0:
        print(f"\n{country}:")
        print(sample[['Year', 'Primary_%', 'Secondary_%', 'Tertiary_%']].to_string(index=False))

df_final = df_final.drop(columns=['Total_%'])

# Export
output_path = '../processed-data/economics-countries-master.csv'
df_final.to_csv(output_path, index=False, na_rep='')

print("\n" + "="*80)
print("EXPORT COMPLETED")
print("="*80)
print(f"\nFile: {output_path}")
print(f"Size: {len(df_final):,} records")
print(f"Countries: {df_final['Country'].nunique()}")
print(f"Years: {df_final['Year'].min()}-{df_final['Year'].max()}")
print("\nColumns: Country, Year, Primary_%, Secondary_%, Tertiary_%, Tourism_%, GDP_USD, Population, Inflation_%, Debt_%")
print("="*80)
