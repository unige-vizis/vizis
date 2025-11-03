# Raw Data Overview

This document provides a comprehensive overview of all datasets in the raw-data folder, organized by source organization.

## Summary Statistics

**Total Datasets**: 13 files (11 CSV/Excel files + 1 PDF metadata)
**Organizations**: 7 data sources
**Total Rows**: ~2.42 million records
**Coverage**: Global conflict, protests, violence, religious demographics, ethnic composition, economic indicators, tourism metrics (1945-2024)
**Primary Dataset**: ACLED (2.37M events)

---

## PRIMARY DATASET

## 1. ACLED (Armed Conflict Location & Event Data Project)

### ACLED_2025-10-29.csv
**The World's Most Comprehensive Political Violence and Protest Event Dataset**

**Size**: 2,372,683 rows × 35 columns (1.32 GB)
**Source**: Armed Conflict Location & Event Data Project
**Coverage**: January 1997 - October 2024 (27+ years)
**Geographic Scope**: Global (all regions, 37+ countries in sample)
**Update Frequency**: Weekly real-time updates available

**Purpose**: ACLED collects real-time data on political violence and protest events worldwide. This is the most granular conflict dataset available, capturing individual events with precise geographic and temporal information, actor details, and source documentation.

**Event Types Covered**:
- Battles (armed clashes between organized groups)
- Explosions/Remote violence (IEDs, air strikes, etc.)
- Violence against civilians (one-sided attacks)
- Protests (demonstrations and rallies)
- Riots (violent public disturbances)
- Strategic developments (non-violent but politically significant)

### Complete Column Reference

| Column | Type | Description | Example | Null% |
|--------|------|-------------|---------|-------|
| `event_id_cnty` | str | Event ID with country code | ALG40 | 0% |
| `event_date` | date | Date of event (YYYY-MM-DD) | 1997-01-29 | 0% |
| `year` | int | Year of event | 1997 | 0% |
| `time_precision` | int | Temporal precision (1-3) | 1 (day-level) | 0% |
| `disorder_type` | str | High-level category | Political violence | 0% |
| `event_type` | str | Primary event classification | Violence against civilians | 0% |
| `sub_event_type` | str | Detailed event subtype | Attack | 0% |
| `actor1` | str | Primary actor/perpetrator | GIA: Armed Islamic Group | 0% |
| `assoc_actor_1` | str | Actor 1 associates | Students (Nigeria) | 82% |
| `inter1` | str | Actor 1 type category | Rebel group | 0% |
| `actor2` | str | Secondary actor/target | Civilians (Algeria) | 21% |
| `assoc_actor_2` | str | Actor 2 associates | Students (Nigeria) | 91% |
| `inter2` | str | Actor 2 type category | Civilians | 21% |
| `interaction` | str | Interaction between actor types | Rebel group-Civilians | 0% |
| `civilian_targeting` | str | Civilian targeting indicator | Civilian targeting | 70% |
| `iso` | int | ISO numeric country code | 12 (Algeria) | 0% |
| `region` | str | World region | Northern Africa | 0% |
| `country` | str | Country name | Algeria | 0% |
| `admin1` | str | First-level admin division | Alger | 0% |
| `admin2` | str | Second-level admin division | Sidi Moussa | 4% |
| `admin3` | str | Third-level admin division | Lower Banta | 39% |
| `location` | str | Specific location name | Algiers - Sidi Moussa | 0% |
| `latitude` | float | Latitude coordinate | 36.6064 | 0% |
| `longitude` | float | Longitude coordinate | 3.0878 | 0% |
| `geo_precision` | int | Geographic precision (1-3) | 1 (precise) | 0% |
| `source` | str | Information source | Algeria Watch | 0% |
| `source_scale` | str | Source type category | Other | 0% |
| `notes` | str | Detailed event description | 8 civilians, among them one baby... | 0% |
| `fatalities` | int | Number of fatalities | 8 | 0% |
| `tags` | str | Additional event tags | crowd size=no report | 99.6% |
| `timestamp` | int | Unix timestamp of data entry | 1618524706 | 0% |
| `population_1km` | float | Population within 1km radius | [future feature] | 100% |
| `population_2km` | float | Population within 2km radius | [future feature] | 100% |
| `population_5km` | float | Population within 5km radius | [future feature] | 100% |
| `population_best` | float | Best population estimate | [future feature] | 100% |

### Key Code Values

**Disorder Types**:
- `Political violence` - Armed conflict and attacks
- `Demonstrations` - Protests and rallies
- `Strategic developments` - Context events (agreements, arrests, etc.)

**Event Types** (6 categories):
1. `Battles` - Armed clashes between organized groups
2. `Explosions/Remote violence` - Bombings, shelling, air strikes
3. `Violence against civilians` - One-sided attacks on non-combatants
4. `Protests` - Public demonstrations
5. `Riots` - Violent crowd actions
6. `Strategic developments` - Non-violent tactical moves

**Sub-Event Types** (22 detailed classifications):
- Attack, Abduction/forced disappearance, Sexual violence
- Armed clash, Government regains territory, Non-state actor overtakes territory
- Air/drone strike, Suicide bomb, Shelling/artillery/missile attack, Grenade, Remote explosive/landmine/IED
- Peaceful protest, Protest with intervention, Excessive force against protesters
- Violent demonstration, Mob violence
- Agreement, Arrests, Change to group/activity, Disrupted weapons use, Looting/property destruction, Non-violent transfer of territory, Other

**Actor Type (inter1/inter2)**:
- `State forces` - Military, police
- `Rebel group` - Armed opposition
- `Political militia` - Party-aligned armed groups
- `Identity militia` - Ethnic/religious militias
- `Rioters` - Unorganized violent protesters
- `Protesters` - Demonstration participants
- `Civilians` - Non-combatants
- `External/Other forces` - Foreign military, private security

**Precision Codes**:
- Time Precision: 1 (day), 2 (week), 3 (month)
- Geographic Precision: 1 (precise location), 2 (approximate within 25km), 3 (admin-level estimate)

**Data Quality Notes**:
- **Missing values**: Population fields not yet populated (future feature)
- **Associated actors**: Often empty (82-91% null) - only used for coalition events
- **Tags field**: Rarely used (99.6% null) - reserved for special coding
- **Fatalities**: Reports confirmed deaths; actual tolls may be higher
- **Geographic precision**: Always check `geo_precision` for mapping accuracy
- **Temporal coverage**: Varies by country (some start after 1997)

---

## SUPPLEMENTARY DATASETS

## 2. UCDP (Uppsala Conflict Data Program)

The most established academic conflict dataset, providing aggregated annual summaries and actor registries. Four complementary datasets:

### 2.1 Actor_v25_1.csv
**Armed Conflict Actors**

**Size**: 1,878 rows × 35 columns
**Version**: 25.1 (2025)
**Coverage**: All armed conflict actors globally (1946-2024)

**Purpose**: Central registry of all armed groups, governments, and organizations involved in conflicts. Use this to standardize actor names when cross-referencing with ACLED.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ActorId` | int | Unique actor identifier | 2 |
| `NameData` | str | Standardized actor name | Government of Hyderabad |
| `NameOrig` | str | Original name in data | Government of Hyderabad |
| `Org` | int | Organization type code | 4 (Government) |
| `ConflictId` | str | Associated conflict IDs | 11884, 226 |
| `Location` | str | Geographic location | Hyderabad, India |
| `Region` | str | Region code | 3 (Asia) |

**Key Features**:
- Tracks name changes, mergers, and splits over time
- Links actors across conflict types
- Coalition and alliance structures

### 2.2 BattleDeaths_v25_1.csv
**Battle-Related Deaths**

**Size**: 1,995 rows × 25 columns
**Version**: 25.1 (2025)
**Coverage**: Annual battle deaths by conflict (1989-2024)

**Purpose**: Annual aggregate fatality estimates for state-based conflicts. Use for year-level trend analysis; ACLED provides event-level detail.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `conflict_id` | int | Unique conflict identifier | 11447 |
| `year` | int | Year of observation | 1991 |
| `bd_best` | int | Best estimate of deaths | 100 |
| `bd_low` | int | Low estimate | 100 |
| `bd_high` | int | High estimate | 100 |
| `type_of_conflict` | int | Conflict type (1-4) | 3 (Internal) |

**Conflict Types**:
- 1 = Extrasystemic, 2 = Interstate, 3 = Internal, 4 = Internationalized internal

### 2.3 GEDEvent_v25_0_9.csv
**Georeferenced Event Dataset**

**Size**: 2,553 rows × 49 columns
**Version**: 25.0.9 (2025)
**Coverage**: Individual violent events (1989-2025, sample shown)

**Purpose**: Similar to ACLED but focused only on organized violence (no protests/riots). More conservative inclusion criteria (only violent events with ≥25 annual deaths at conflict level).

**Violence Types**:
- 1 = State-based conflict, 2 = Non-state conflict, 3 = One-sided violence

### 2.4 UcdpPrioConflict_v25_1.csv
**Armed Conflict Dataset**

**Size**: 2,752 rows × 28 columns
**Version**: 25.1 (2025)
**Coverage**: Armed conflicts with ≥25 battle deaths per year (1946-2024)

**Purpose**: Annual summary of all state-based armed conflicts. Use for identifying major conflicts; ACLED captures lower-intensity events.

**Intensity Levels**:
- 1 = Minor conflict (25-999 deaths/year), 2 = War (≥1000 deaths/year)

---

## 3. Religious Cleavages

### Religious_Cleavages_Dataset.csv
**Religious Cleavages in Armed Conflict**

**Size**: 1,610 rows × 13 columns
**Source**: Religious Cleavages Dataset
**Coverage**: Armed conflicts with religious dimensions (1946-present)
**Format**: Originally Stata (.dta), converted to CSV

**Purpose**: Documents religious characteristics of conflict actors and the role of religion in armed conflicts. Use to add religious context to ACLED/UCDP events.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `idv4` | int | Conflict ID (UCDP v4) | 1 |
| `sidea` | str | Government/Side A name | Bolivia |
| `sideb` | str | Rebel group/Side B name | ELN |
| `year` | int | Year of observation | 1967 |
| `govrel` | str | Government's religion | catholic |
| `rebrel` | str | Rebel group's religion | none |
| `cleavage` | float | Religious cleavage present (1=yes) | 1.0 |
| `reldiscr` | float | Religious discrimination index | 7.0 |
| `relfrac` | float | Religious fractionalization (0-1) | 0.2479 |

---

## 4. Epac (Ethnic Power Relations)

### ED-2021.csv
**Ethnic Dimensions Dataset**

**Size**: 871 rows × 20 columns
**Source**: Ethnic Power Relations (EPR) Core Dataset
**Coverage**: Ethnic group compositions by country

**Purpose**: Captures the ethnic, religious, linguistic, and phenotypic composition of politically relevant ethnic groups worldwide. Use to add demographic context to country-level analysis.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `gwid` | int | Gleditsch-Ward country ID | 2 (USA) |
| `religion1/2/3` | str | Religion codes | ARC4, ATH, ARC1 |
| `rel1/2/3_size` | float | Proportion of group (0-1) | 0.56, 0.2, 0.17 |
| `language1/2/3` | str | Language codes | eng, cre, oji |
| `phenotype1/2/3` | str | Phenotype codes | eur, ssa |

---

## 5. WRP (World Religion Project)

Global religious demographics from 1945-2010 at three levels of aggregation. Use for historical religious context (note: ends 2010).

### 5.1 WRP_global.csv
**Size**: 14 rows × 77 columns | **Coverage**: Worldwide totals every 5 years (1945-2010)

### 5.2 WRP_national.csv
**Size**: 1,995 rows × 84 columns | **Coverage**: Country-level data every 5 years (1945-2010)

### 5.3 WRP_regional.csv
**Size**: 182 rows × 84 columns | **Coverage**: Regional aggregates every 5 years (1945-2010)

**Purpose**: Religious population totals and percentages over time.

**Major Column Groups**: Christian (6 denominations), Jewish (4), Muslim (8), Buddhist (3), Hindu, Sikh, Shinto, Baha'i, Taoist, Jain, Confucian, Syncretic, Animist, Non-religious, Other

---

## 6. World Bank

Economic indicators and GDP data from the World Bank's comprehensive global development database. Two complementary datasets covering macroeconomic performance and sectoral breakdowns.

### 6.1 world_bank_development_indicators.csv
**Comprehensive Development Indicators**

**Size**: 17,272 rows × 50 columns (5.2 MB)
**Source**: World Bank Development Indicators
**Coverage**: Annual data by country (1960-2024+)
**Geographic Scope**: Global (all countries)

**Purpose**: Comprehensive collection of 50 key development indicators covering economic performance, governance, environment, infrastructure, and social metrics. Use for understanding the broader development context behind conflicts.

**Indicator Categories** (50 total indicators):

**Economic Indicators**:
- `GDP_current_US` - GDP in current US dollars
- `inflation_annual%` - Annual inflation rate
- `real_interest_rate` - Real interest rate
- `risk_premium_on_lending` - Risk premium on lending
- `central_goverment_debt%` - Central government debt as % of GDP
- `tax_revenue%` - Tax revenue as % of GDP
- `expense%` - Government expense as % of GDP

**Governance Indicators** (World Bank Governance Indicators):
- `control_of_corruption_estimate` & `control_of_corruption_std` - Corruption control scores
- `goverment_effectiveness_estimate` & `goverment_effectiveness_std` - Government effectiveness
- `political_stability_estimate` & `political_stability_std` - Political stability scores
- `rule_of_law_estimate` & `rule_of_law_std` - Rule of law metrics
- `regulatory_quality_estimate` & `regulatory_quality_std` - Regulatory quality
- `voice_and_accountability_estimate` & `voice_and_accountability_std` - Democratic accountability

**Social & Human Development**:
- `human_capital_index` - Human capital index score
- `government_expenditure_on_education%` - Education spending as % of GDP
- `government_health_expenditure%` - Health spending as % of GDP
- `multidimensional_poverty_headcount_ratio%` - Multidimensional poverty rate
- `gini_index` - Income inequality measure
- `life_expectancy_at_birth` - Average life expectancy
- `birth_rate` & `death_rate` - Demographic rates
- `population` & `rural_population` - Population metrics
- `population_density` - People per sq km

**Environment & Resources**:
- `agricultural_land%` & `forest_land%` - Land use percentages
- `land_area` - Total land area
- `avg_precipitation` - Average precipitation levels
- `CO2_emisions` - CO2 emissions
- `other_greenhouse_emisions` - Other greenhouse gas emissions
- `renewvable_energy_consumption%` - Renewable energy share
- `electric_power_consumption` - Electricity consumption
- `access_to_electricity%` - Population with electricity access

**Infrastructure & Business**:
- `individuals_using_internet%` - Internet penetration rate
- `logistic_performance_index` - Logistics performance
- `doing_business` - Ease of doing business score
- `time_to_get_operation_license` - Days to get business permits
- `statistical_performance_indicators` - Statistical capacity

**Trade & Research**:
- `trade_in_services%` - Trade in services as % of GDP
- `research_and_development_expenditure%` - R&D spending as % of GDP

**Security**:
- `military_expenditure%` - Military spending as % of GDP
- `intentional_homicides` - Intentional homicide rate

**Data Quality**:
- Many indicators have sparse data for certain countries/years
- Governance indicators updated annually with some lag
- Check for missing values when analyzing specific countries

### 6.2 Download-GDPcurrent-NCU-countries.xlsx
**GDP Components and Sectoral Breakdown**

**Size**: 3,714 rows × 58 columns (2.2 MB)
**Source**: World Bank National Accounts Data
**Coverage**: Annual GDP data by country (1970-2023)
**Geographic Scope**: 220 countries
**Format**: Excel (.xlsx) with 2 sheets (main data + footnotes)

**Purpose**: Detailed GDP breakdown by expenditure components and economic sectors in national currencies. Use for understanding economic structure and how conflicts affect different sectors.

**GDP Expenditure Components** (9 indicators):
- `Final consumption expenditure` - Total consumption
- `Household consumption expenditure` - Private consumption
- `General government final consumption expenditure` - Government consumption
- `Gross capital formation` - Total investment
- `Gross fixed capital formation` - Fixed capital investment
- `Changes in inventories` - Inventory changes
- `Exports of goods and services` - Total exports
- `Imports of goods and services` - Total imports
- `Gross Domestic Product (GDP)` - Total GDP

**GDP by Economic Sector** (8 indicators):
- `Agriculture, hunting, forestry, fishing (ISIC A-B)`
- `Mining, Manufacturing, Utilities (ISIC C-E)`
- `Manufacturing (ISIC D)`
- `Construction (ISIC F)`
- `Wholesale, retail trade, restaurants and hotels (ISIC G-H)`
- `Transport, storage and communication (ISIC I)`
- `Other Activities (ISIC J-P)`
- `Total Value Added`

**Key Features**:
- All values in national currency (see `Currency` column)
- 54 years of annual data (1970-2023)
- Includes footnotes sheet with data source notes
- Header row starts at row 3 (row 1-2 are metadata)

**Data Structure**:
| Column | Type | Description |
|--------|------|-------------|
| `CountryID` | int | Numeric country identifier |
| `Country` | str | Country name |
| `Currency` | str | National currency name |
| `IndicatorName` | str | GDP component or sector name |
| `1970` to `2023` | float | Annual values in national currency |

---

## 7. UN Tourism

### 7.1 UN_Tourism_8_9_1_TDGDP_04_2025.xlsx
**Tourism Direct GDP Contribution (SDG Indicator 8.9.1)**

**Size**: 1,243 rows × 12 columns (78 KB)
**Source**: UN Tourism (formerly UNWTO) - Sustainable Development Goal 8.9.1
**Coverage**: Annual data by country (2008-2023)
**Geographic Scope**: 125 countries
**Format**: Excel (.xlsx) with 2 sheets (Overview + data)
**Update**: April 2025 release

**Purpose**: Tracks tourism's direct contribution to GDP as a percentage of total GDP. Essential for understanding economic dependence on tourism and how conflicts affect tourism-dependent economies.

**SDG Context**: Part of UN Sustainable Development Goal 8.9 - "By 2030, devise and implement policies to promote sustainable tourism that creates jobs and promotes local culture and products."

**Complete Column Reference**:
| Column | Type | Description |
|--------|------|-------------|
| `INDEX` | int | Row index (mostly null) |
| `SDG_Indicator` | str | SDG code (8.9.1) |
| `SeriesCode` | str | UN series identifier |
| `SeriesDescription` | str | "Tourism direct GDP as a proportion of total GDP (%)" |
| `GeoAreaCode` | int | UN M49 country code |
| `GeoAreaName` | str | Country name |
| `TimePeriod` | int | Year of observation |
| `Value` | float | Tourism GDP as % of total GDP |
| `Source` | str | Data source organization |
| `FootNote` | str | Methodological notes |
| `Nature` | str | Data type (Country data/Estimate) |
| `Units` | str | PERCENT |

**Key Metrics**:
- Measures **direct** tourism contribution only (not indirect/induced effects)
- Includes accommodation, food services, transport, recreation, travel services
- Based on Tourism Satellite Account (TSA) methodology
- Values typically range from <1% (low tourism) to 20%+ (tourism-dependent economies)

**Coverage Notes**:
- 125 countries reporting
- 16 years of data (2008-2023)
- Some countries have gaps in annual reporting
- Data may be estimated for certain years (check `Nature` column)

**Included Files**:
- Main data: Sheet "SDG 8.9.1"
- Metadata PDF: `UN_Tourism_8_9_1_TDGDP_metadata_04_2025.pdf` (251 KB) - Contains methodology, definitions, and data quality notes

---

## Data Linkage Keys

Cross-dataset joins are possible using these common identifiers:

| Dataset 1 | Dataset 2 | Common Key(s) | Notes |
|-----------|-----------|---------------|-------|
| ACLED | UCDP GED | `country`, `year`, `event_date`, `latitude`, `longitude` | Fuzzy match on location/date |
| ACLED | Religious Cleavages | `country`, `year`, `actor1/2` | Match on country-year, actors |
| ACLED | World Bank | `country`, `year` | Country-year join |
| ACLED | UN Tourism | `country`, `year` (as `TimePeriod`) | Country-year join |
| UCDP Actor | UCDP Conflict | `ActorId` ↔ `side_a_id`, `side_b_id` | Direct join |
| UCDP Conflict | UCDP BattleDeaths | `conflict_id`, `dyad_id` | Direct join |
| UCDP Conflict | World Bank | `country`, `year` | Country-year join |
| Religious Cleavages | UCDP Conflict | `idv4` ↔ `conflict_id` (v4) | Direct join |
| Epac | WRP | `gwid` ↔ `state` | May need code conversion |
| Any dataset | WRP | `country` ↔ `name`, `year` | Country-year join |
| Any dataset | World Bank Dev Indicators | `country`, `date` (year) | Country-year join |
| Any dataset | World Bank GDP | `country`, year columns | Country-year join |
| Any dataset | UN Tourism | `country` ↔ `GeoAreaName`, `year` ↔ `TimePeriod` | Country-year join |
| World Bank Dev Indicators | World Bank GDP | `country`, `year` | Both use country names |
| World Bank | UN Tourism | `country`, `year` | Economic context for tourism |

**Geographic Codes**:
- ACLED uses ISO numeric country codes (`iso` column)
- UCDP/Religious Cleavages use Gleditsch-Ward codes (`gwno*`, `gwnoa`)
- Epac/WRP use Gleditsch-Ward codes (`gwid`, `state`)
- World Bank uses country names (`country` column) and numeric IDs (`CountryID`)
- UN Tourism uses UN M49 codes (`GeoAreaCode`) and country names (`GeoAreaName`)
- A lookup table may be needed for cross-system joins between different coding schemes

---
