<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import flowData from '@/assets/data/viz9_intervention_flows.json'

const centroids = flowData.centroids
const allFlows = flowData.flows

const chartRef = ref(null)
const containerWidth = ref(0)
const selectedYear = ref(2024)
const showPeacekeeping = ref(false) // Toggle to include UN peacekeeping missions

// Color coding by intervener type
const westernCountries = new Set([
  'USA', 'UK', 'France', 'Germany', 'Canada', 'Australia', 'Netherlands',
  'Belgium', 'Denmark', 'Norway', 'Sweden', 'Italy', 'Spain', 'Portugal',
  'Poland', 'Czech Republic', 'Austria', 'Greece', 'Finland', 'Ireland',
  'New Zealand', 'Estonia', 'Latvia', 'Lithuania', 'Luxembourg', 'Hungary',
  'Romania', 'Bulgaria', 'Slovenia', 'Slovakia', 'Croatia'
])

const russianBlocCountries = new Set([
  'Russia', 'Iran', 'North Korea', 'Syria', 'Belarus'
])

const africanRegionalCountries = new Set([
  'Kenya', 'Ethiopia', 'Uganda', 'Rwanda', 'Burundi', 'Tanzania',
  'South Africa', 'Nigeria', 'Senegal', 'Ghana', 'Cameroon', 'Chad',
  'Niger', 'Mali', 'Burkina Faso', 'Benin', 'Togo', 'Ivory Coast',
  'Djibouti', 'Eritrea', 'Zambia', 'Zimbabwe', 'Malawi', 'Botswana',
  'Gabon', 'Congo', 'DR Congo', 'CAR', 'South Sudan', 'Mauritania',
  'Gambia', 'Guinea', 'Guinea-Bissau', 'Liberia', 'Sierra Leone'
])

function getInterventionColor(country) {
  if (westernCountries.has(country)) return '#3b82f6' // Blue
  if (russianBlocCountries.has(country)) return '#dc2626' // Red
  if (africanRegionalCountries.has(country)) return '#f59e0b' // Orange/Amber
  return '#8b5cf6' // Purple for others (Middle East, Asia, etc.)
}

function getMarkerType(country) {
  if (westernCountries.has(country)) return 'western'
  if (russianBlocCountries.has(country)) return 'russian'
  if (africanRegionalCountries.has(country)) return 'african'
  return 'other'
}

// Get min/max years from data
const years = [...new Set(allFlows.map(f => f.year))].sort()
const minYear = Math.min(...years)
const maxYear = Math.max(...years)

// Store D3 elements for updates
let svg = null
let projection = null
let flowGroup = null
let tooltip = null

function updateDimensions() {
  if (!chartRef.value) return
  containerWidth.value = chartRef.value.clientWidth
  createChart()
}

let resizeObserver
onMounted(() => {
  updateDimensions()
  resizeObserver = new ResizeObserver(updateDimensions)
  resizeObserver.observe(chartRef.value)
})

onUnmounted(() => resizeObserver?.disconnect())

// Watch for year and filter changes
watch([selectedYear, showPeacekeeping], () => {
  if (flowGroup) updateFlows()
})

// Create curved arc path between two points
function createArc(from, to) {
  const source = projection([centroids[from][1], centroids[from][0]])
  const target = projection([centroids[to][1], centroids[to][0]])

  if (!source || !target) return null

  // Calculate control point for quadratic curve
  const midX = (source[0] + target[0]) / 2
  const midY = (source[1] + target[1]) / 2

  // Offset perpendicular to the line for curve
  const dx = target[0] - source[0]
  const dy = target[1] - source[1]
  const dist = Math.sqrt(dx * dx + dy * dy)

  // Curve amount based on distance (longer = more curve)
  const offset = Math.min(dist * 0.2, 50)

  // Perpendicular offset
  const controlX = midX - (dy / dist) * offset
  const controlY = midY + (dx / dist) * offset

  return {
    path: `M ${source[0]},${source[1]} Q ${controlX},${controlY} ${target[0]},${target[1]}`,
    source,
    target
  }
}

function updateFlows() {
  const year = parseInt(selectedYear.value)
  let yearFlows = allFlows.filter(f => f.year === year)

  // Filter out peacekeeping unless toggle is on
  if (!showPeacekeeping.value) {
    yearFlows = yearFlows.filter(f => f.type === 'direct')
  }

  // Prepare flow data with paths
  const flowPaths = yearFlows
    .map(f => {
      const arc = createArc(f.from, f.to)
      if (!arc) return null
      return { ...f, ...arc }
    })
    .filter(d => d !== null)

  // Update flows using D3 data join
  const paths = flowGroup.selectAll('.flow-arc')
    .data(flowPaths, d => `${d.from}-${d.to}`)

  // Remove old
  paths.exit().remove()

  // Add new
  paths.enter()
    .append('path')
    .attr('class', 'flow-arc')
    .attr('d', d => d.path)
    .attr('fill', 'none')
    .attr('stroke', d => getInterventionColor(d.from))
    .attr('stroke-width', 2)
    .attr('stroke-linecap', 'round')
    .attr('opacity', 0.7)
    .attr('marker-end', d => `url(#arrow-${getMarkerType(d.from)})`)
    .style('cursor', 'pointer')
    .on('mouseover', function(event, d) {
      d3.select(this)
        .attr('opacity', 1)
        .attr('stroke-width', 4)
        .raise()

      const typeLabel = d.type === 'direct' ? 'Military intervention' : d.type === 'coalition' ? 'Coalition' : 'UN Peacekeeping'
      tooltip
        .style('opacity', 1)
        .html(`
          <strong>${d.from}</strong> → <strong>${d.to}</strong><br/>
          <span style="color:#aaa">${d.conflict_type}</span><br/>
          <strong>Issue:</strong> ${d.issue}<br/>
          <strong>Against:</strong> ${d.opponent}<br/>
          <strong>Type:</strong> ${typeLabel} (${d.num_interveners} nations)<br/>
          <strong>Deaths:</strong> ${d.deaths.toLocaleString()}
        `.trim())
    })
    .on('mousemove', function(event) {
      const containerRect = chartRef.value.getBoundingClientRect()
      tooltip
        .style('left', (event.clientX - containerRect.left + 15) + 'px')
        .style('top', (event.clientY - containerRect.top - 10) + 'px')
    })
    .on('mouseout', function(event, d) {
      d3.select(this)
        .attr('opacity', 0.7)
        .attr('stroke-width', 2)
      tooltip.style('opacity', 0)
    })

  // Update existing
  paths.attr('d', d => d.path)
}

async function createChart() {
  if (!containerWidth.value) return

  const margin = { top: 10, right: 10, bottom: 10, left: 10 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 500

  d3.select(chartRef.value).selectAll('*').remove()

  // Create tooltip
  tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.85)')
    .style('color', '#fff')
    .style('padding', '10px 14px')
    .style('border-radius', '4px')
    .style('font-size', '0.9rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)
    .style('max-width', '280px')

  svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // Define arrow markers for each color
  const defs = svg.append('defs')
  const colors = {
    'western': '#3b82f6',
    'russian': '#dc2626',
    'african': '#f59e0b',
    'other': '#8b5cf6'
  }

  Object.entries(colors).forEach(([name, color]) => {
    defs.append('marker')
      .attr('id', `arrow-${name}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 4)
      .attr('markerHeight', 4)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', color)
  })

  // Create layer groups in correct order BEFORE async loading
  // This ensures flows are always rendered on top of the map
  const mapGroup = svg.append("g").attr("class", "map-layer")
  flowGroup = svg.append("g").attr("class", "flows")

  // Load world map
  const world = await d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  const countries = topojson.feature(world, world.objects.countries).features

  // Projection
  projection = d3.geoMercator()
    .fitSize([width, height + 150], {
      type: "FeatureCollection",
      features: countries
    })
  const currentTranslate = projection.translate()
  projection.translate([currentTranslate[0], currentTranslate[1] + 75])

  const path = d3.geoPath(projection)

  // Draw base map into the map layer group
  mapGroup.selectAll("path")
    .data(countries)
    .enter()
    .append("path")
    .attr("d", path)
    .attr("fill", "#e8e8e8")
    .attr("stroke", "#ccc")
    .attr("stroke-width", 0.5)

  // Draw initial flows
  updateFlows()
}
</script>

<template>
  <div class="chart-wrapper">
    <!-- Color Legend -->
    <div class="color-legend">
      <div class="legend-item">
        <span class="legend-dot western"></span>
        <span class="legend-label">Western</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot russian"></span>
        <span class="legend-label">Russian Bloc</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot african"></span>
        <span class="legend-label">African Regional</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot other"></span>
        <span class="legend-label">Other</span>
      </div>
    </div>

    <div ref="chartRef" class="chart chart-min-width"></div>

    <!-- Controls Row -->
    <div class="controls-row">
      <!-- Year Slider -->
      <div class="slider-container">
        <span class="year-label">{{ minYear }}</span>
        <input
          type="range"
          v-model="selectedYear"
          :min="minYear"
          :max="maxYear"
          step="1"
          class="year-slider"
        />
        <span class="year-label">{{ maxYear }}</span>
      </div>

      <!-- Intervention Type Toggle -->
      <div class="toggle-container">
        <label class="toggle-label">
          <input
            type="checkbox"
            v-model="showPeacekeeping"
            class="toggle-checkbox"
          />
          <span class="toggle-switch"></span>
          <span class="toggle-text">Include UN Peacekeeping</span>
        </label>
      </div>
    </div>
    <div class="year-display">Year: {{ selectedYear }}</div>
  </div>
</template>

<style scoped>
.chart {
  position: relative;
}

/* Color Legend */
.color-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.western {
  background-color: #3b82f6;
}

.legend-dot.russian {
  background-color: #dc2626;
}

.legend-dot.african {
  background-color: #f59e0b;
}

.legend-dot.other {
  background-color: #8b5cf6;
}

.legend-label {
  font-size: 0.75rem;
  color: #666;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
  padding: 0 20px;
  flex-wrap: wrap;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 14px;
}

.year-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #555;
  min-width: 40px;
}

.year-slider {
  flex: 1;
  max-width: 350px;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: #666;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
}

.year-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  border: 3px solid #333;
}

.year-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid #333;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

.year-display {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-top: 8px;
}

/* Toggle Switch Styles */
.toggle-container {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.toggle-checkbox {
  display: none;
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  background: #ccc;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.toggle-checkbox:checked + .toggle-switch {
  background: #3b82f6;
}

.toggle-checkbox:checked + .toggle-switch::after {
  transform: translateX(20px);
}

.toggle-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #555;
}
</style>
