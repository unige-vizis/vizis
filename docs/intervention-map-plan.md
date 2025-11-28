# Military Intervention Flow Map - Implementation Plan

## Overview

An interactive world map showing military intervention flows (arrows) from intervening countries to conflict zones, with a **year slider** to filter by year.

---

## Data Source Clarification

**UCDP "Battle Deaths"** = all deaths in organized armed conflict, including:
- Direct combat deaths (all sides)
- Collateral deaths during military operations
- Civilians caught in crossfire during battles

**What it does NOT include:**
- One-sided violence (massacres outside battle contexts)
- Non-state conflicts (rebel vs rebel without government)

**Intervention data = "Internationalized intrastate conflicts" (type 4)**
- Conflicts where foreign governments actively support one side militarily
- 390 records, 944,297 total deaths (2015-2024)

**Suggested label:** "Conflict Deaths" or "Deaths in Internationalized Conflicts"

---

## 1. Data Processing (Jupyter Notebook)

### Input Data
- **Source:** `data-processing/raw-data/UCDP/BattleDeaths_v25_1.csv`
- **Key Fields:**
  - `location_inc` - Country where conflict occurs
  - `side_a` - Primary party (usually government)
  - `side_a_2nd` - Secondary parties (intervening countries)
  - `year` - Year of conflict
  - `bd_best` - Conflict deaths (best estimate)

### Processing Steps

```python
# 1. Load UCDP Battle Deaths data
df = pd.read_csv('raw-data/UCDP/BattleDeaths_v25_1.csv')

# 2. Filter to 2015-2024
df = df[(df['year'] >= 2015) & (df['year'] <= 2024)]

# 3. Extract intervention flows
# For each row with side_a_2nd, create flow records:
# - from: intervening country (cleaned name)
# - to: conflict location
# - year: year
# - deaths: conflict deaths

# 4. Aggregate by (from, to, year)
# Sum deaths for duplicate from-to-year combinations

# 5. Add country centroids (lat/lon) for both from and to
# Use a reference file or calculate from GeoJSON

# 6. Export to JSON
```

### Output JSON Structure

```json
{
  "metadata": {
    "title": "Military Interventions in Armed Conflicts",
    "source": "UCDP Battle Deaths Dataset v25.1",
    "date_range": "2015-2024",
    "note": "Deaths in internationalized conflicts where foreign governments provided military support"
  },
  "centroids": {
    "USA": { "lat": 39.8283, "lon": -98.5795 },
    "Russia": { "lat": 61.524, "lon": 105.3188 },
    "Syria": { "lat": 34.8021, "lon": 38.9968 },
    ...
  },
  "flows": [
    {
      "from": "USA",
      "to": "Afghanistan",
      "year": 2015,
      "deaths": 15234
    },
    {
      "from": "USA",
      "to": "Afghanistan",
      "year": 2016,
      "deaths": 18456
    },
    ...
  ]
}
```

### Files to Create
- `data-processing/viz-datasets/viz9_intervention_flows.json`
- Copy to `public/src/assets/data/viz9_intervention_flows.json`

---

## 2. Vue Component Structure

### File: `public/src/components/visualizations/InterventionFlowMap.vue`

```
┌─────────────────────────────────────────────────────────────┐
│  Military Interventions in Armed Conflicts                  │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │                    WORLD MAP                          │  │
│  │                                                       │  │
│  │     ════════►  (curved arrows with varying           │  │
│  │                 thickness based on deaths)            │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  2015 ●──────────────────────────────────○ 2024            │
│                    Year: 2019                               │
│                                                             │
│  Legend: Arrow thickness = conflict deaths                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Props/State

```javascript
// Reactive state
const selectedYear = ref(2024)        // Current year from slider
const chartRef = ref(null)            // SVG container reference

// Computed
const filteredFlows = computed(() => {
  return data.flows.filter(f => f.year === selectedYear.value)
})
```

---

## 3. D3.js Implementation Details

### 3.1 Map Projection

```javascript
// Use same projection as existing maps for consistency
const projection = d3.geoMercator()
  .scale(150)
  .translate([width / 2, height / 1.5])

const path = d3.geoPath().projection(projection)
```

### 3.2 Drawing Flow Arcs

```javascript
// Create curved arc between two points
function createArc(source, target) {
  const sourceXY = projection([source.lon, source.lat])
  const targetXY = projection([target.lon, target.lat])

  // Calculate midpoint with curve offset
  const midX = (sourceXY[0] + targetXY[0]) / 2
  const midY = (sourceXY[1] + targetXY[1]) / 2

  // Offset perpendicular to line for curve
  const dx = targetXY[0] - sourceXY[0]
  const dy = targetXY[1] - sourceXY[1]
  const dist = Math.sqrt(dx * dx + dy * dy)
  const offset = dist * 0.2  // 20% curve

  const controlX = midX - (dy / dist) * offset
  const controlY = midY + (dx / dist) * offset

  return `M ${sourceXY[0]},${sourceXY[1]}
          Q ${controlX},${controlY}
            ${targetXY[0]},${targetXY[1]}`
}
```

### 3.3 Arrow Styling

```javascript
// Stroke width based on deaths (log scale)
const strokeScale = d3.scaleSqrt()
  .domain([100, 50000])
  .range([1, 12])
  .clamp(true)

// Color scheme
const colors = {
  western: '#3b82f6',    // Blue - USA, UK, France, etc.
  russian: '#ef4444',    // Red - Russia, Iran
  regional: '#f59e0b',   // Orange - Kenya, Ethiopia, etc.
  other: '#8b5cf6'       // Purple - others
}

// Arrow markers for direction
svg.append('defs')
  .append('marker')
  .attr('id', 'arrowhead')
  .attr('viewBox', '0 -5 10 10')
  .attr('refX', 8)
  .attr('refY', 0)
  .attr('markerWidth', 4)
  .attr('markerHeight', 4)
  .attr('orient', 'auto')
  .append('path')
  .attr('d', 'M0,-5L10,0L0,5')
  .attr('fill', 'currentColor')
```

### 3.4 Year Slider

```html
<template>
  <div class="slider-container">
    <span>2015</span>
    <input
      type="range"
      v-model="selectedYear"
      min="2015"
      max="2024"
      step="1"
      class="year-slider"
    />
    <span>2024</span>
  </div>
  <div class="year-display">Year: {{ selectedYear }}</div>
</template>
```

### 3.5 Update on Year Change

```javascript
// Watch for year changes and redraw
watch(selectedYear, (newYear) => {
  updateFlows(newYear)
})

function updateFlows(year) {
  const flows = data.flows.filter(f => f.year === year)

  // Simple enter/exit pattern
  const arcs = svg.selectAll('.flow-arc')
    .data(flows, d => `${d.from}-${d.to}`)

  // Remove old arcs
  arcs.exit().remove()

  // Add new arcs
  arcs.enter()
    .append('path')
    .attr('class', 'flow-arc')
    .attr('d', d => createArc(centroids[d.from], centroids[d.to]))
    .attr('stroke-width', d => strokeScale(d.deaths))
    .attr('stroke', d => getColor(d.from))
    .attr('fill', 'none')
    .attr('opacity', 0.7)
    .attr('marker-end', 'url(#arrowhead)')

  // Update existing arcs (stroke width may change)
  arcs.attr('stroke-width', d => strokeScale(d.deaths))
}
```

---

## 4. Tooltip Design

```javascript
// Show on hover over arc
const tooltip = d3.select('body')
  .append('div')
  .attr('class', 'intervention-tooltip')

// Tooltip content
function showTooltip(event, d) {
  tooltip
    .style('opacity', 1)
    .style('left', (event.pageX + 10) + 'px')
    .style('top', (event.pageY - 10) + 'px')
    .html(`
      <strong>${d.from} → ${d.to}</strong><br/>
      Year: ${d.year}<br/>
      Battle Deaths: ${d.deaths.toLocaleString()}<br/>
      Conflict: ${d.conflict_name}
    `)
}
```

---

## 5. Legend Component

Simple inline legend showing arrow thickness meaning:

```
Arrow thickness indicates conflict deaths
── thin = fewer deaths   ═══ thick = more deaths
```

---

## 6. File Structure

```
public/src/
├── components/
│   └── visualizations/
│       └── InterventionFlowMap.vue    # New component
├── assets/
│   └── data/
│       └── viz9_intervention_flows.json  # New data file

data-processing/
├── notebooks/
│   └── week4-visualisations.ipynb     # Add processing code
└── viz-datasets/
    └── viz9_intervention_flows.json   # Generated data
```

---

## 7. Implementation Steps

### Step 1: Data Processing (Jupyter)
- [ ] Load UCDP BattleDeaths data
- [ ] Filter to 2015-2024
- [ ] Parse `side_a_2nd` field to extract intervening countries
- [ ] Clean country names to match GeoJSON
- [ ] Add centroid coordinates for each country
- [ ] Aggregate by (from, to, year)
- [ ] Export to JSON

### Step 2: Create Vue Component
- [ ] Set up component scaffold with refs
- [ ] Import D3 and data JSON
- [ ] Create base map (copy structure from ColorplethMap)
- [ ] Implement arc drawing function
- [ ] Add year slider with v-model
- [ ] Implement flow filtering by year

### Step 3: Styling & Polish
- [ ] Style year slider
- [ ] Implement tooltips
- [ ] Create simple legend
- [ ] Test responsiveness

### Step 4: Integration
- [ ] Import component in Section5.vue
- [ ] Position alongside existing maps
- [ ] Test with full dataset

---

## 8. Estimated Complexity

| Task | Difficulty | Time |
|------|------------|------|
| Data processing | Medium | 1-2 hours |
| Base map setup | Easy | 30 min |
| Arc drawing | Medium | 1 hour |
| Year slider | Easy | 20 min |
| Tooltips & legend | Easy | 30 min |
| Testing | Easy | 30 min |
| **Total** | | **4-5 hours** |

---

## 9. Data Validation Checklist

Before implementation, verify:
- [ ] All country names in UCDP match our GeoJSON country names
- [ ] Centroids are accurate for all countries
- [ ] No missing years in the 2015-2024 range
- [ ] Death counts are reasonable (no obvious errors)
- [ ] At least 10+ interventions per year for visual interest
