# Economic Structure Dataset Plan

## Objective
Create a consolidated country-year economic structure dataset showing the percentage breakdown of each country's economy by sector for each year.

## Data Source
**Base Dataset**: World Bank GDP sectoral breakdown (`Download-GDPcurrent-NCU-countries.xlsx`)
- **Coverage**: 220 countries, 1970-2023 (54 years)
- **Supplementary**: UN Tourism data for tourism-specific metrics (2008-2023)

## Sector Classification

### Primary Sector (Extractive/Agricultural)
**Components**:
- Agriculture, hunting, forestry, fishing (ISIC A-B)
- Mining (calculated as: Mining, Manufacturing, Utilities - Manufacturing)

**Calculation**:
```
Primary_% = (Agriculture + Mining) / Total_Value_Added × 100

Where:
  Mining = (Mining, Manufacturing, Utilities [ISIC C-E]) - (Manufacturing [ISIC D])
```

### Secondary Sector (Industrial/Manufacturing)
**Components**:
- Manufacturing (ISIC D)
- Construction (ISIC F)

**Calculation**:
```
Secondary_% = (Manufacturing + Construction) / Total_Value_Added × 100
```

### Tertiary Sector (Services)
**Components**:
- Wholesale, retail trade, restaurants and hotels (ISIC G-H)
- Transport, storage and communication (ISIC I)
- Other Activities (ISIC J-P)

**Calculation**:
```
Tertiary_% = (Wholesale_Retail + Transport + Other_Activities) / Total_Value_Added × 100
```

### Tourism (Special Indicator - Subset of Tertiary)
**Source**: UN Tourism SDG 8.9.1 dataset
**Calculation**: Direct value from dataset (already calculated as % of total GDP)
**Coverage**: 2008-2023 only (125 countries)

## Country Code Mapping Table

### Step 1: Create Master Country Mapping
A one-time lookup table to enable joins across all datasets.

**Structure**:
| Column | Source | Purpose |
|--------|--------|---------|
| `Country_Name_Standard` | Standardized name | Primary join key |
| `ISO_Numeric_Code` | ACLED | For conflict data joins |
| `GleditschWard_Code` | UCDP/Religious Cleavages | For conflict data joins |
| `UN_M49_Code` | UN Tourism | For tourism data joins |
| `WorldBank_CountryID` | World Bank | For economic data joins |
| `WorldBank_Country_Name` | World Bank | Alternate join key |

**Method**: Manual curation using country name fuzzy matching + official lookup tables from UN/World Bank

## Output Dataset Structure

### Final Schema
```
Country | Year | Primary_% | Secondary_% | Tertiary_% | Tourism_% | GDP_USD | Notes
```

**Columns**:
- `Country` (str): Standardized country name
- `Year` (int): Year of observation (1970-2023)
- `Primary_%` (float): Primary sector as % of Total Value Added
- `Secondary_%` (float): Secondary sector as % of Total Value Added
- `Tertiary_%` (float): Tertiary sector as % of Total Value Added
- `Tourism_%` (float): Tourism direct GDP as % of total GDP (NULL before 2008)
- `GDP_USD` (float): Total GDP in current US dollars (from World Bank Dev Indicators)
- `Notes` (str): Data quality flags (e.g., "estimated", "incomplete year")

### Example Output
```
Country      | Year | Primary_% | Secondary_% | Tertiary_% | Tourism_% | GDP_USD
-------------|------|-----------|-------------|------------|-----------|------------
Afghanistan  | 2010 | 32.4      | 24.5        | 43.1       | NULL      | 15.9B
Afghanistan  | 2015 | 28.5      | 22.3        | 49.2       | 1.2       | 19.3B
Syria        | 2010 | 21.8      | 31.2        | 47.0       | 12.5      | 60.2B
Syria        | 2015 | NULL      | NULL        | NULL       | NULL      | NULL (conflict)
```

## Implementation Steps

1. **Load World Bank GDP sectoral data** (Excel, skip first 2 rows, header at row 3)
2. **Reshape data** from wide format (years as columns) to long format (year as rows)
3. **Calculate sectoral components**:
   - Extract Mining = (Mining+Manufacturing+Utilities) - Manufacturing
   - Sum components for each sector
   - Calculate percentages relative to Total Value Added
4. **Load UN Tourism data** and merge on country-year (2008-2023 subset)
5. **Load World Bank Development Indicators** for GDP_USD and merge on country-year
6. **Create country mapping table** (manual/semi-automated)
7. **Export consolidated dataset** as CSV for easy joining with conflict data

## Benefits

- **Long time series**: 54 years of data (1970-2023)
- **Broad coverage**: 220 countries
- **Conflict-ready**: Easy country-year joins with ACLED, UCDP
- **Economic context**: See how conflicts affect different economic structures
- **Tourism vulnerability**: Identify tourism-dependent economies affected by violence
- **Longitudinal analysis**: Track economic transformation during/after conflicts

## Use Cases for Conflict Analysis

1. **Tourism collapse during conflict**: Compare Tourism_% before/during/after conflict events
2. **Sectoral impacts**: Which sectors are most disrupted by violence?
3. **Economic structure & conflict type**: Do agricultural vs. industrial economies have different conflict patterns?
4. **Recovery patterns**: How do sectors recover post-conflict?
5. **Resource conflicts**: Correlate Primary_% (extraction) with conflict intensity

## Data Quality Notes

- **Missing data**: Some countries/years may have incomplete sectoral breakdowns
- **Currency conversions**: World Bank GDP uses national currency; need USD conversion for cross-country comparison
- **Tourism data gaps**: Only available 2008-2023; use NULL for earlier years
- **Conflict periods**: Data collection may fail during active conflicts (e.g., Syria 2014-2018)
- **Validation**: Ensure Primary_% + Secondary_% + Tertiary_% ≈ 100% (allow small rounding errors)

## Next Steps

1. **Create country mapping table** (priority task)
2. **Write Python/Jupyter notebook** to implement the calculations
3. **Validate outputs** on sample countries (check percentages sum to ~100%)
4. **Export final CSV** to `data-processing/processed-data/` folder
5. **Document methodology** in processing notebook
