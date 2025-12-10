# Week 6: Complex Sankey Visualization Implementation Plan

## 🎯 Project Overview

**Visualization Goal**: "The Actors most involved in Conflict"
- **Level 1**: Actor selection dropdown (top 5 per actor type)
- **Level 2**: Countries where actor was active
- **Level 3**: Conflict types in those countries
- **Future Level 4**: Timeline showing years of activity (planned for later)

**Data Source**: ACLED dataset (2.37M events, 1997-2024)
**Flow Characteristics**:
- Width: Proportional to event count
- Color: Intensity based on fatalities
- Interactive: Actor selection drives entire visualization

## 📊 Data Structure Design

### Required Processed Data Format
```json
{
  "actor_types": {
    "State forces": ["Military Forces of Syria (2000-2024)", "Military Forces of Ukraine (2019-)", ...],
    "Rebel group": ["Taliban", "NAF: United Armed Forces of Novorossiya", "Al Shabaab", ...],
    "Political militia": ["Unidentified Gang (Mexico)", "Unidentified Armed Group (Mexico)", ...],
    "Identity militia": ["Fulani Ethnic Militia (Nigeria)", "Darfur Communal Militia (Sudan)", ...],
    "External/Other forces": ["Military Forces of Russia (2000-)", "Military Forces of Israel (2022-)", ...]
  },
  "flows": [
    {
      "actor": "Taliban",
      "actor_type": "Rebel group", 
      "country": "Afghanistan",
      "event_type": "Battles",
      "sub_event_type": "Armed clash",
      "events": 15420,
      "fatalities": 45230,
      "years": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], // TIMELINE HOOK
      "year_breakdown": {  // TIMELINE HOOK
        "2024": {"events": 1250, "fatalities": 3200},
        "2023": {"events": 1890, "fatalities": 5100}
      }
    }
  ]
}
```

## 🎨 Visual Design Specifications

### Color Coding System (Fatality-based)
```javascript
// Fatality-based color scale
const fatalityColorScale = d3.scaleSequential()
  .domain([1, maxFatalities])
  .interpolator(d3.interpolateOrRd)  // Orange to dark red

// Alternative: Categorical ranges
const fatalityRanges = {
  low: {range: [1, 100], color: '#FEF0D9'},      // Light orange
  medium: {range: [101, 1000], color: '#FD8D3C'}, // Orange  
  high: {range: [1001, 5000], color: '#D94701'},  // Dark orange
  extreme: {range: [5001, Infinity], color: '#7F2704'} // Dark red
}
```

### Layout Structure
```javascript
const layout = {
  actorDropdown: { x: 0, width: 200 },
  sankeyMain: { x: 220, width: containerWidth * 0.65 },
  timelineReserved: { x: containerWidth * 0.85, width: containerWidth * 0.15 }, // FUTURE HOOK
  totalWidth: containerWidth
}
```

## 🚀 Implementation Phases

### **Phase 1: Data Preprocessing (PRIORITY)**
**File**: `data-processing/notebooks/week6-sankey-preprocessing.ipynb`

**Tasks**:
1. Load ACLED dataset (`data-processing/raw-data/ACLED/ACLED_2025-10-29.csv`)
2. Identify top 5 actors per actor type (by total event count)
3. Aggregate data: actor → country → event_type → year
4. Calculate fatality statistics for color coding
5. Export to `data-processing/viz-datasets/viz10_actor_sankey.json`

**Key Aggregations**:
```python
# Group by actor, country, event_type
actor_flows = df.groupby(['actor1', 'inter1', 'country', 'event_type']).agg({
    'event_id_cnty': 'count',  # Event count
    'fatalities': 'sum',       # Total fatalities
    'year': lambda x: sorted(x.unique())  # Years active
}).rename(columns={'event_id_cnty': 'events'})

# Get top 5 actors per type
top_actors_by_type = df.groupby(['inter1', 'actor1'])['event_id_cnty'].count().groupby('inter1').nlargest(5)
```

### **Phase 2: Core Sankey Implementation**
**File**: `public/src/components/visualizations/SankeyChart.vue`

**Components**:
1. **Actor Selection Dropdown**
   - Grouped by actor type
   - Search functionality
   - Event count display

2. **3-Level Sankey Diagram**
   - Selected Actor → Countries → Conflict Types
   - D3.js sankey layout
   - Flow width based on event counts
   - Flow color based on fatality intensity

3. **Interactive Features**
   - Hover tooltips with details
   - Flow highlighting
   - Dynamic updates on actor change

### **Phase 3: Timeline Hooks (Future-Proofing)**
**Preparation for future timeline integration without implementing**:

1. **Data Structure Hooks**
   - Include `years` and `year_breakdown` in flow data
   - Process timeline data but don't visualize

2. **Layout Hooks**
   - Reserve SVG space for timeline
   - Structure components for easy timeline addition

3. **Code Hooks**
   ```vue
   <template>
     <div class="sankey-container">
       <ActorSelector />
       <SankeyDiagram />
       <!-- <TimelineComponent v-if="showTimeline" /> FUTURE HOOK -->
     </div>
   </template>
   ```

## 🚨 Technical Challenges & Solutions

### **Challenge 1: Data Volume**
- **Issue**: ACLED has 2.37M events
- **Solution**: Aggressive preprocessing and aggregation
- **Mitigation**: Focus on top actors only, event-level filtering

### **Challenge 2: Performance**
- **Issue**: Many flows for popular actors
- **Solution**: 
  - Canvas rendering for heavy datasets
  - Flow filtering (minimum threshold)
  - Lazy loading

### **Challenge 3: Dynamic Layout**
- **Issue**: Actor selection changes entire visualization
- **Solution**: Rebuild sankey on selection change
- **Optimization**: Smooth transitions between states

### **Challenge 4: Flow Complexity**
- **Issue**: Single actor may have 50+ countries × 6 event types = 300+ flows
- **Solution**: 
  - Hierarchical flow bundling
  - Minimum flow threshold filtering
  - Progressive disclosure

## 📋 Implementation Checklist

### Phase 1: Data Preprocessing
- [ ] Create Jupyter notebook
- [ ] Load and explore ACLED data
- [ ] Identify actor type distribution
- [ ] Extract top 5 actors per type
- [ ] Aggregate flows by actor-country-event_type
- [ ] Calculate fatality statistics
- [ ] Include timeline data hooks
- [ ] Export processed JSON

### Phase 2: Core Sankey
- [ ] Create actor selection dropdown
- [ ] Implement 3-level sankey layout
- [ ] Add fatality-based color coding
- [ ] Implement flow proportionality
- [ ] Add interactive tooltips
- [ ] Handle actor selection changes
- [ ] Optimize performance

### Phase 3: Timeline Preparation
- [ ] Include timeline data in processing
- [ ] Reserve layout space for timeline
- [ ] Add component structure hooks
- [ ] Document timeline integration points

## 🔮 Future Timeline Integration Plan

**When ready for timeline implementation**:

1. **Timeline Component**
   - Vertical timeline on right side (years 2015-2024)
   - Year markers with activity indicators

2. **Connections**
   - Curved lines from conflict type nodes to timeline years
   - Line thickness = activity intensity for that year
   - Color = fatality intensity for that year

3. **Interactivity**
   - Click year to filter entire visualization
   - Hover year to highlight related flows
   - Scrub timeline to see temporal patterns

**Estimated Timeline Integration Effort**: 8-12 additional hours

## 📁 File Structure

```
data-processing/
├── notebooks/
│   └── week6-sankey-preprocessing.ipynb     # NEW: Data processing
└── viz-datasets/
    └── viz10_actor_sankey.json              # NEW: Processed data

public/src/components/
├── Section6.vue                             # EXISTING: Section wrapper
└── visualizations/
    └── SankeyChart.vue                      # EXISTING: Sankey implementation

docs/
└── week6-sankey-implementation-plan.md     # THIS FILE
```

## 🎯 Success Criteria

### Core Functionality
- [ ] Actor dropdown with top 5 per type works
- [ ] 3-level sankey displays correctly
- [ ] Flow colors reflect fatality intensity
- [ ] Flow widths reflect event proportions
- [ ] Actor selection updates entire visualization
- [ ] Performance acceptable for all actors

### Timeline Readiness
- [ ] Timeline data included in processing
- [ ] Layout structured for easy timeline addition
- [ ] Component architecture supports timeline extension
- [ ] No refactoring needed for timeline integration

**Estimated Development Time**: 10-16 hours (without timeline)
**Timeline Integration**: +8-12 hours (future enhancement)