"""
Build a Master Country Mapping Table
Combines: UN M.49 + World Bank metadata (+ optional Gleditsch & Ward codes)
"""

import pandas as pd
import requests

# ------------------------------------------------------------
# 1. Get UN M.49 table (official list of countries and areas)
# ------------------------------------------------------------
un_url = "https://unstats.un.org/unsd/methodology/m49/overview/"
# UN provides an HTML table — we'll read it directly with pandas
un_tables = pd.read_html(un_url)
un_df = un_tables[0].copy()

# Standardize columns (replace spaces and dashes with underscores)
un_df.columns = [c.lower().strip().replace(" ", "_").replace("-", "_") for c in un_df.columns]

un_df.rename(
    columns={
        "country_or_area": "country_name_standard",
        "m49_code": "un_m49_code",
        "iso_alpha2_code": "iso2",
        "iso_alpha3_code": "iso3",
    },
    inplace=True,
)

un_df = un_df[
    ["country_name_standard", "iso2", "iso3", "un_m49_code", "region_name", "sub_region_name"]
]

# ------------------------------------------------------------
# 2. Get World Bank country metadata via API
# ------------------------------------------------------------
wb_url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
wb_data = requests.get(wb_url).json()[1]
wb_df = pd.DataFrame(wb_data)

wb_df = wb_df.rename(
    columns={
        "id": "world_bank_code",
        "name": "country_name_wb",
    }
)
wb_df = wb_df[
    ["country_name_wb", "iso2Code", "region", "incomeLevel", "world_bank_code"]
].rename(columns={"iso2Code": "iso2"})

# Extract readable values from dict objects
wb_df['region'] = wb_df['region'].apply(lambda x: x.get('value', '') if isinstance(x, dict) else '')
wb_df['incomeLevel'] = wb_df['incomeLevel'].apply(lambda x: x.get('value', '') if isinstance(x, dict) else '')

# ------------------------------------------------------------
# 3. Merge UN + World Bank metadata
# ------------------------------------------------------------
merged = pd.merge(un_df, wb_df, on="iso2", how="outer", validate="1:1")

# ------------------------------------------------------------
# 4. Optionally merge Gleditsch & Ward codes (if you have a CSV)
# ------------------------------------------------------------
# Example:
# gw_df = pd.read_csv("gleditsch_ward_codes.csv")
# merged = pd.merge(merged, gw_df[["iso3", "gwno"]], on="iso3", how="left")

# ------------------------------------------------------------
# 5. Clean and export
# ------------------------------------------------------------
merged.rename(
    columns={
        "country_name_standard": "Country_Name_Standard",
        "iso2": "ISO2",
        "iso3": "ISO3",
        "un_m49_code": "UN_M49_Code",
        "world_bank_code": "WorldBank_ID",
        "region_name": "UN_Region",
        "sub_region_name": "UN_Subregion",
        "region": "WB_Region",
        "incomeLevel": "WB_IncomeLevel",
    },
    inplace=True,
)

# Sort for clarity
merged.sort_values(by="Country_Name_Standard", inplace=True)

# Save to CSV in processed-data folder
output_path = "../processed-data/master_country_mapping.csv"
merged.to_csv(output_path, index=False, encoding="utf-8")

print(f"[SUCCESS] Master mapping table saved as '{output_path}'")
print(f"Total entries: {len(merged)}")
print(merged.head(10))
