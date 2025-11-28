# Third Map Visualization Ideas

## Current Maps on Website

| Map | Type | Data Shown |
|-----|------|------------|
| ColorplethMap | Choropleth (color fill) | Primary sector share by country |
| ProportionalSymbolMap | Bubble map | Total conflict fatalities by country |

---

## Available Data Sources

| Dataset | Records | Coverage | Key Fields |
|---------|---------|----------|------------|
| ACLED Events | 2.4M events | 236 countries, 1997-2024 | Events, fatalities, actors, coordinates |
| Economics Master | 11K rows | 220 countries, 1970-2023 | GDP, Population, Sector %, Inflation, Debt |
| UCDP Battle Deaths | 2K records | Global conflicts | Deaths, **external interventions** |
| UCDP Actors | - | Cross-national | Government involvement in foreign conflicts |

---

## Option 1: Military Intervention Flow Map ⭐ RECOMMENDED

### Concept
Curved arrows flowing FROM intervening countries TO conflict zones, with line thickness representing associated battle deaths.

### Visual Style
- Great-circle arcs connecting country centroids
- Arrow thickness = log(battle_deaths)
- Color coding by intervener type (Western/Russian/Regional)
- Animated flow direction (optional)

### Key Data (2015-2024)

#### Top Intervention Flows

| From | To | Battle Deaths | Years |
|------|-----|---------------|-------|
| USA | Afghanistan | 165,291 | 2015-2021 |
| Iran | Syria | 148,541 | 2015-2024 |
| Russia | Syria | 148,541 | 2015-2024 |
| North Korea | Ukraine | 75,686 | 2024 |
| Pakistan | Afghanistan | 74,217 | 2015-2018 |
| USA | Iraq | 34,274 | 2015-2024 |
| France | Iraq | 34,274 | 2015-2024 |
| USA | Somalia | 22,313 | 2015-2024 |
| Kenya | Somalia | 22,156 | 2015-2024 |
| Ethiopia | Somalia | 22,156 | 2015-2024 |

#### Top Intervening Nations (by associated battle deaths)

| Country | Total Deaths | Conflicts Involved |
|---------|--------------|-------------------|
| USA | 232,241 | 8 countries |
| Iran | 152,358 | 2 countries |
| Russia | 150,404 | 3 countries |
| Pakistan | 81,765 | 4 countries |
| North Korea | 75,686 | 1 country |
| France | 47,887 | 5 countries |
| UK | 39,799 | 2 countries |
| Kenya | 32,367 | 6 countries |

### Why This Option?

1. **Visually striking** - arrows on maps are immediately comprehensible
2. **Unique** - not shown anywhere else on the site
3. **Clean data** - UCDP has structured intervention records
4. **Ties to theme** - wealthy service economies projecting power into primary-sector economies
5. **Compelling narrative** - "Who fights in other people's wars?"

### Technical Implementation

```javascript
// Libraries needed
import * as d3 from 'd3'
import { geoPath, geoInterpolate } from 'd3-geo'

// Create curved arc between two points
function createArc(source, target) {
  const interpolate = geoInterpolate(source, target)
  const midpoint = interpolate(0.5)
  // Curve the arc by offsetting midpoint
  return d3.line().curve(d3.curveBasis)([source, midpoint, target])
}
```

### Alternative Libraries
- [d3-geo](https://d3js.org/d3-geo) - Great circle arcs
- [Leaflet.migrationLayer](https://github.com/hallahan/LeafletPlayback) - Animated flows
- [deck.gl ArcLayer](https://deck.gl/docs/api-reference/layers/arc-layer) - WebGL performance

---

## Option 2: Dorling Cartogram - Conflict Intensity

### Concept
Country circles sized by **fatalities per capita** (conflict burden relative to population). Geography is distorted to show where conflict hits hardest proportionally.

### Visual Style
- Each country becomes a circle
- Circle area proportional to fatalities/million inhabitants
- Circles maintain approximate geographic positions
- Color by region or economic category

### Key Data

#### Deadliest Conflicts (by fatality rate per event)

| Country | Events | Fatalities | Fatality Rate |
|---------|--------|------------|---------------|
| Chad | 1,385 | 4,582 | 3.31 |
| Ethiopia | 11,789 | 36,346 | 3.08 |
| Afghanistan | 67,194 | 202,145 | 3.01 |
| Nigeria | 32,148 | 80,338 | 2.50 |
| South Sudan | 12,589 | 30,490 | 2.42 |
| Burkina Faso | 11,026 | 26,639 | 2.42 |
| Niger | 4,174 | 9,109 | 2.18 |
| Mali | 10,800 | 22,770 | 2.11 |
| CAR | 4,928 | 9,289 | 1.88 |
| Sudan | 24,196 | 44,545 | 1.84 |

### Why This Option?

1. **Normalizes by population** - reveals proportional suffering
2. **Visually dramatic** - small countries with deadly conflicts become visible
3. **Different perspective** - your bubble map shows absolute numbers, this shows relative burden

### Technical Implementation

```javascript
// Libraries
import { Cartogram } from 'd3-cartogram'
// or use: https://github.com/shawnbot/topogram
```

### Alternative Libraries
- [d3-cartogram](https://github.com/shawnbot/topogram)
- [Dorling cartogram Observable](https://observablehq.com/@d3/dorling-cartogram)
- [cartogram-chart](https://github.com/nicola/cartogram-chart)

---

## Option 3: Economic Transformation Cartogram

### Concept
Country sizes distorted by **how much their economy shifted** toward or away from services (tertiary sector) between 2015 and 2023.

### Visual Style
- Size = absolute value of tertiary sector change
- Color = direction (green = toward services, red = away from services)
- Reveals economic de-development caused by conflict

### Key Data

#### Countries Shifting AWAY from Services (De-development)

| Country | Tertiary 2015 | Tertiary 2023 | Change |
|---------|---------------|---------------|--------|
| Guyana | 46.79% | 19.54% | -27.25% |
| **Afghanistan** | 68.35% | 49.21% | -19.14% |
| **Nigeria** | 58.76% | 43.60% | -15.16% |
| Guinea | 51.32% | 38.16% | -13.16% |
| **Niger** | 41.22% | 28.37% | -12.85% |
| **Iran** | 56.63% | 43.81% | -12.82% |
| **Libya** | 64.88% | 52.84% | -12.04% |
| Laos | 49.38% | 40.25% | -9.13% |
| Angola | 48.80% | 39.85% | -8.95% |
| **Iraq** | 50.85% | 41.99% | -8.86% |

*Bold = conflict-affected countries*

#### Countries Shifting TOWARD Services (Modernization)

| Country | Tertiary 2015 | Tertiary 2023 | Change |
|---------|---------------|---------------|--------|
| Turkmenistan | 35.45% | 49.02% | +13.57% |
| Armenia | 52.90% | 64.71% | +11.81% |
| Ukraine | 60.23% | 70.04% | +9.81% |
| Bhutan | 46.43% | 54.20% | +7.77% |
| Cook Islands | 85.45% | 92.61% | +7.16% |

### Why This Option?

1. **Unique narrative** - shows economic consequences of conflict
2. **Clear pattern** - conflict countries regress economically
3. **Ties perfectly to your thesis** - economic composition vs conflict

### Caveat
- Guyana's shift is due to oil discovery, not conflict
- Need to distinguish resource-driven vs conflict-driven changes

---

## Option 4: Cross-Border Actor Network Map

### Concept
Network graph overlaid on map showing non-state armed actors that operate across multiple countries.

### Visual Style
- Nodes = countries where actor operates
- Edges = shared actors
- Node size = number of events
- Edge weight = actor activity level

### Key Data

#### Multinational Military Forces (from ACLED)

| Actor | Countries | Example Locations |
|-------|-----------|-------------------|
| US Military (2021-2025) | 30 | Iraq, Yemen, Saudi Arabia, Somalia |
| Russian Military | 21 | Syria, Ukraine, CAR, Libya, Mali |
| US Military (2017-2021) | 21 | Yemen, Somalia, Pakistan, Afghanistan |
| French Military | ~15 | Mali, Niger, Burkina Faso, Chad |

#### Cross-Border Non-State Actors

| Actor | Countries | Type |
|-------|-----------|------|
| Al-Shabaab | Somalia, Kenya | Rebel group |
| ISIS variants | Syria, Iraq, Egypt, Libya, Afghanistan | Rebel group |
| Wagner Group | Syria, CAR, Mali, Libya, Sudan | PMC |

### Why This Option?

1. Shows conflict "spillover" across borders
2. Reveals transnational threat networks
3. More complex to implement but very informative

---

## Comparison Summary

| Option | Data Complexity | Visual Impact | Narrative Fit | Implementation |
|--------|-----------------|---------------|---------------|----------------|
| 1. Flow Map | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium |
| 2. Dorling Cartogram | Low | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium |
| 3. Economic Cartogram | Low | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium |
| 4. Actor Network | High | ⭐⭐⭐⭐ | ⭐⭐⭐ | Hard |

---

## Recommendation

**Option 1: Military Intervention Flow Map** is the strongest choice because:

1. It's the most **visually distinctive** map type you don't have yet
2. The data is **clean and ready** from UCDP
3. It **directly connects** to your economic analysis (wealthy nations intervening in poorer ones)
4. The narrative is **compelling**: "Who fights in other people's wars?"
5. It shows **relationships between countries** rather than just individual country metrics

---

## Next Steps

1. Choose preferred option
2. Process data in Jupyter notebook
3. Export to `viz-datasets/viz9_*.json`
4. Create Vue component in `visualizations/`
5. Add to Section5.vue
