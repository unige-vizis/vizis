# Processed Data

This folder contains cleaned, consolidated datasets ready for analysis and visualization.

## economics-countries-master.csv

**Master economic structure dataset by country-year, ready for merging with conflict data.**

### Dataset Overview

- **Records**: 10,936 country-year observations
- **Countries**: 220
- **Time Coverage**: 1970-2023 (54 years)
- **File Size**: ~500 KB
- **Format**: CSV with headers, NULL values as empty cells

### Column Definitions

| Column | Type | Description | Coverage |
|--------|------|-------------|----------|
| `Country` | text | Country name (World Bank standardized) | 100% |
| `Year` | integer | Year of observation (1970-2023) | 100% |
| `Primary_%` | float | Primary sector as % of Total Value Added | 98.4% |
| `Secondary_%` | float | Secondary sector as % of Total Value Added | 99.6% |
| `Tertiary_%` | float | Tertiary sector as % of Total Value Added | 99.6% |
| `Tourism_%` | float | Tourism direct GDP as % of total GDP | 10.3% |
| `GDP_USD` | float | GDP in current US dollars | 74.6% |

### Sector Definitions

**Primary Sector** (Extractive/Agricultural):
- Agriculture, hunting, forestry, fishing
- Mining and quarrying
- Formula: `(Agriculture + Mining) / Total Value Added × 100`

**Secondary Sector** (Industrial/Manufacturing):
- Manufacturing
- Construction
- Formula: `(Manufacturing + Construction) / Total Value Added × 100`

**Tertiary Sector** (Services):
- Wholesale and retail trade, restaurants, hotels
- Transport, storage, communication
- Other service activities (finance, real estate, government, etc.)
- Formula: `(Trade + Transport + Other Services) / Total Value Added × 100`

**Tourism** (Special indicator - subset of tertiary):
- Direct tourism contribution to GDP (%)
- Based on Tourism Satellite Account methodology
- Coverage: 2008-2023 only, 125 countries
- Source: UN Tourism SDG 8.9.1

### Data Sources

1. **World Bank GDP Sectoral Breakdown**: Sectoral composition (1970-2023)
2. **UN Tourism SDG 8.9.1**: Tourism direct GDP % (2008-2023)
3. **World Bank Development Indicators**: GDP in USD (1960-2024)

### Data Quality Notes

- **Sector percentages**: 97.65% of records have valid sectors that sum to 100% (±1%)
- **Missing data**:
  - Primary_%: 1.6% missing (some countries lack sectoral breakdowns)
  - Secondary_%: 0.4% missing
  - Tertiary_%: 0.4% missing
  - Tourism_%: 89.7% missing (only available 2008-2023 for 125 countries)
  - GDP_USD: 25.4% missing (some country-years lack USD conversion)

- **Conflict-affected countries**: Some countries have data gaps during active conflict periods
  - Example: Syria shows economic shifts during 2011+ conflict (services collapsed, agriculture increased)

### Usage Examples

#### Merge with Conflict Data (ACLED)

```python
import pandas as pd

# Load datasets
df_economics = pd.read_csv('processed-data/economics-countries-master.csv')
df_conflict = pd.read_csv('raw-data/ACLED/ACLED_2025-10-29.csv')

# Aggregate conflict events by country-year
conflict_by_country_year = df_conflict.groupby(['country', 'year']).agg({
    'event_id_cnty': 'count',
    'fatalities': 'sum'
}).reset_index()
conflict_by_country_year.columns = ['Country', 'Year', 'Events', 'Fatalities']

# Merge with economics
df_merged = df_economics.merge(
    conflict_by_country_year,
    on=['Country', 'Year'],
    how='left'
)

# Fill NaN in conflict columns with 0 (no events)
df_merged[['Events', 'Fatalities']] = df_merged[['Events', 'Fatalities']].fillna(0)

# Example analysis: Tourism impact during conflict
tourism_conflict = df_merged[df_merged['Tourism_%'].notna()]
print(tourism_conflict[['Country', 'Year', 'Tourism_%', 'Events', 'Fatalities']].head(20))
```

#### Analyze Economic Structure Changes Over Time

```python
# Example: Afghanistan's economic transformation
afghanistan = df_economics[df_economics['Country'] == 'Afghanistan']

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(afghanistan['Year'], afghanistan['Primary_%'], label='Primary (Agr+Mining)')
plt.plot(afghanistan['Year'], afghanistan['Secondary_%'], label='Secondary (Manuf+Const)')
plt.plot(afghanistan['Year'], afghanistan['Tertiary_%'], label='Tertiary (Services)')
plt.xlabel('Year')
plt.ylabel('% of Total Value Added')
plt.title('Afghanistan: Economic Structure Over Time (1970-2023)')
plt.legend()
plt.grid(alpha=0.3)
plt.show()
```

#### Identify Tourism-Dependent Economies

```python
# Countries most dependent on tourism (2019, pre-COVID)
tourism_2019 = df_economics[
    (df_economics['Year'] == 2019) &
    (df_economics['Tourism_%'].notna())
].nlargest(20, 'Tourism_%')

print(tourism_2019[['Country', 'Tourism_%', 'GDP_USD']])
```

### Key Insights from the Data

1. **Syria (conflict example)**:
   - Pre-conflict (2010): 42% Primary, 8% Secondary, 50% Tertiary
   - During conflict (2017): 53% Primary, 4% Secondary, 43% Tertiary
   - **Economic regression**: Services collapsed, economy shifted back to agriculture

2. **Afghanistan**:
   - Recent years show increasing Primary sector (40%+) due to conflict and instability
   - Secondary sector remains weak (~10%)

3. **Tourism vulnerability**:
   - Some countries (e.g., Guyana 33%, Panama 11%) are highly tourism-dependent
   - Conflict directly impacts tourism-dependent economies

4. **Developed economies** (e.g., United States):
   - Highly service-based: ~80% Tertiary, ~15% Secondary, ~4% Primary
   - Stable structure over time

### Processing Scripts

- **Main Generator**: `notebooks/create-economics-master.py`
- **Notebook**: `notebooks/create-economics-master.ipynb`
- **Plan Document**: `temp/economic-structure-dataset-plan.md`

### Version History

- **2025-11-02**: Dataset created
  - 220 countries, 1970-2023 (54 years)
  - Primary/Secondary/Tertiary sector percentages calculated
  - Tourism % and GDP in USD integrated
  - Explicit NULL values for all missing data

---

**Ready for conflict analysis!** Use `Country` + `Year` as join keys.
