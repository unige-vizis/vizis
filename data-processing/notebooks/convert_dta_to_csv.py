"""
Quick script to convert .dta (Stata) files to CSV format
"""
import pandas as pd
from pathlib import Path

# Read the .dta file
dta_file = Path('../raw-data/Religious Cleavages Dataset.dta')
output_folder = Path('../raw-data/Religious_Cleavages')
output_folder.mkdir(exist_ok=True)

print(f"Reading {dta_file.name}...")
df = pd.read_stata(dta_file)

print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Save as CSV
output_file = output_folder / 'Religious_Cleavages_Dataset.csv'
df.to_csv(output_file, index=False)

print(f"\nConverted successfully!")
print(f"Saved to: {output_file}")
print(f"Rows: {len(df)}")
