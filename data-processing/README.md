# Data Processing Workflow

This folder contains all data processing scripts, notebooks, and datasets for the Vizis project. The workflow is designed to keep raw data and intermediate processing steps local (not committed to git), while only the final reduced datasets needed for the website are version controlled.

## Folder Structure

```
data-processing/
├── raw-data/           # Original CSV/Excel files (gitignored)
├── notebooks/          # Jupyter notebooks for data processing
├── intermediate/       # Intermediate processing results (gitignored)
├── output/             # Final outputs like PNG charts (gitignored)
└── viz-datasets/       # Reduced JSON datasets for D3.js (committed to git)
```

## Workflow Steps

### 1. Add Raw Data
Place your original CSV, Excel, or other data files into the `raw-data/` folder. These files will **not** be committed to git.

```
raw-data/
├── conflict_data_2024.csv
├── population_stats.xlsx
└── ...
```

### 2. Create Processing Notebooks
Create Jupyter notebooks in the `notebooks/` folder to process your data. Use pandas and NumPy for transformations.

**Naming Convention**: Use descriptive names like `01_clean_conflict_data.ipynb`, `02_aggregate_by_region.ipynb`, etc.

### 3. Save Intermediate Results
During processing, save intermediate results to the `intermediate/` folder. This helps with:
- Debugging
- Reusing partially processed data
- Avoiding redundant computations

These files are **gitignored** and won't be committed.

### 4. Generate Outputs

#### Option A: Static Visualizations
Create charts using Matplotlib/seaborn and save PNG/SVG files to the `output/` folder.

**To deploy**: Manually copy these images to `public/src/assets/` for inclusion in the website.

#### Option B: Interactive Visualizations
Generate reduced JSON datasets optimized for D3.js and save them to the `viz-datasets/` folder.

These files **will be committed to git** and should be:
- Small in size (< 1MB ideally)
- Only include necessary fields
- Pre-aggregated where possible

```python
# Example: Save reduced dataset
import json

reduced_data = df[['date', 'country', 'fatalities']].to_dict('records')

with open('../viz-datasets/conflict_summary.json', 'w') as f:
    json.dump(reduced_data, f, indent=2)
```

### 5. Deploy to Website
Reduced datasets in `viz-datasets/` are automatically tracked by git. To use them in the website:

1. Copy or reference the JSON file from your Vue components
2. Typical path in public folder: `public/src/assets/data/`
3. Import in components:
   ```js
   import data from '@/assets/data/conflict_summary.json'
   ```

## Git Tracking Rules

### ✅ Committed to Git
- `notebooks/*.ipynb` - Jupyter notebooks (code only, outputs cleared recommended)
- `viz-datasets/*.json` - Reduced datasets for D3.js
- `viz-datasets/*.geojson` - Geographic datasets
- `README.md` - This file

### ❌ Gitignored (Local Only)
- `raw-data/` - Original datasets
- `intermediate/` - Intermediate processing results
- `output/` - Static visualizations (PNG, SVG, PDF)
- All CSV, Excel, and binary data files except in `viz-datasets/`
- Python cache files and virtual environments

## Best Practices

### Data Processing
1. **Version your transformations**: Save intermediate steps as new files, don't overwrite
2. **Document your steps**: Use markdown cells in notebooks to explain each transformation
3. **Keep raw data pristine**: Never modify files in `raw-data/`, always read and transform to new files
4. **Clear notebook outputs**: Before committing notebooks, clear outputs to reduce file size

### Dataset Optimization
1. **Reduce data size**: Only include fields needed for visualization
2. **Pre-aggregate**: Calculate sums, averages, etc. in Python rather than client-side
3. **Limit rows**: Filter to relevant date ranges, top N items, etc.
4. **Use appropriate formats**:
   - JSON for general data
   - GeoJSON for geographic data
   - Consider CSV for very large tables (can be parsed client-side)

### Python Environment
1. **Use virtual environments**: Create a `venv/` or `.venv/` in this folder (gitignored)
2. **Document dependencies**: Create a `requirements.txt` for reproducibility
3. **Recommended packages**:
   ```
   pandas
   numpy
   matplotlib
   seaborn
   jupyter
   ```

## Example Workflow

```python
# In notebooks/01_process_conflict_data.ipynb

import pandas as pd
import json

# 1. Load raw data
df = pd.read_csv('../raw-data/conflict_data_2024.csv')

# 2. Save intermediate cleaned version
df_clean = df.dropna().drop_duplicates()
df_clean.to_csv('../intermediate/conflict_data_clean.csv', index=False)

# 3. Aggregate for visualization
summary = df_clean.groupby('country').agg({
    'fatalities': 'sum',
    'events': 'count'
}).reset_index()

# 4. Save reduced dataset for website
viz_data = summary.to_dict('records')
with open('../viz-datasets/conflict_by_country.json', 'w') as f:
    json.dump(viz_data, f, indent=2)

# 5. Optional: Create static visualization
import matplotlib.pyplot as plt
summary.plot(x='country', y='fatalities', kind='bar')
plt.savefig('../output/fatalities_by_country.png', dpi=300, bbox_inches='tight')
```

## API Integration

For small, frequently updated datasets, consider fetching directly from APIs in your Vue components:

```js
// Example: ACLED API
async function fetchLatestData() {
  const response = await fetch('https://api.acleddata.com/...')
  return await response.json()
}
```

This approach is best for:
- Real-time or frequently updated data
- Small payloads (< 100KB)
- Data that doesn't require heavy pre-processing
