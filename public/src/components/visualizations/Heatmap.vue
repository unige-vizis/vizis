<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  show: {
    type: String,
    default: 'events'
  },
  y_labels: Boolean
})

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)
const normalizeByPopulation = ref(false)

// Load the data from viz4_heatmap_event_types_years.json
import jsonData from '@/assets/data/viz4_heatmap_event_types_years.json'
const data = Array.isArray(jsonData && jsonData.data) ? jsonData.data : []

// Extract unique years and event types
const years = [...new Set(data.map(d => d.year))].sort()
const eventTypes = [...new Set(data.map(d => d.event_type))].sort()

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || container.clientWidth * 0.6 // 60% aspect ratio if height not constrained
  createChart()
}

// Set up resize observer
let resizeObserver
onMounted(() => {
  updateDimensions()
  resizeObserver = new ResizeObserver(updateDimensions)
  if (chartRef.value) {
    resizeObserver.observe(chartRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})

function createChart() {
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 20, right: 120, bottom: 60, left: 220 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 300 || containerHeight.value - margin.top - margin.bottom

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const x = d3.scaleBand()
    .domain(years)
    .range([0, width])
    .padding(0.05)

  const y = d3.scaleBand()
    .domain(eventTypes)
    .range([0, height])
    .padding(0.05)
  // Single-metric heatmap: use the passed `data` prop to decide which field to visualise
  // Supported prop values: 'events' -> 'event_count', 'fatalities' -> 'total_fatalities'
  const metricKey = (props.show === 'fatalities') ? 'total_fatalities' : 'event_count'
  const maxMetric = d3.max(data, d => d[metricKey]) || 0

  const colorScale = d3.scaleSequential()
    .interpolator(metricKey === 'total_fatalities' ? d3.interpolateReds : d3.interpolatePurples)
    .domain([0, maxMetric])

  // Function to determine text color based on background intensity
  const getTextColor = (value, maxValue) => {
    const normalized = maxValue > 0 ? value / maxValue : 0
    return normalized > 0.5 ? '#ffffff' : '#1a1a1a'
  }

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .style('font-size', '1rem')

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  if (props.y_labels ) {
    // Add Y axis
    svg.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .style('font-size', '1rem')
  }

  // Tooltip
  const tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', '#fff')
    .style('padding', '8px 12px')
    .style('border-radius', '4px')
    .style('font-size', '1rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)

  // Draw cells (single metric)
  const cells = svg.selectAll('.cell')
    .data(data)
    .enter()
    .append('g')
    .attr('class', 'cell')

  cells.append('rect')
    .attr('x', d => x(d.year))
    .attr('y', d => y(d.event_type))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .attr('fill', d => colorScale(d[metricKey]))
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 0.5)
    .on('mouseover', function(event, d) {
      d3.select(this).attr('stroke', '#ffffff').attr('stroke-width', 2)
      tooltip
        .style('opacity', 1)
        .html(`<strong>${d.event_type}</strong><br/>${d.year}: ${d.event_count.toLocaleString()} events<br/>Fatalities: ${d.total_fatalities.toLocaleString()}`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this).attr('stroke', '#1a1a1a').attr('stroke-width', 0.5)
      tooltip.style('opacity', 0)
    })

  // Labels inside cells for the selected metric
  cells.append('text')
    .attr('x', d => x(d.year) + x.bandwidth() / 2)
    .attr('y', d => y(d.event_type) + y.bandwidth() / 2)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('fill', d => getTextColor(d[metricKey], maxMetric))
    .style('font-size', '1rem')
    .style('font-weight', '600')
    .style('pointer-events', 'none')
    .text(d => (d[metricKey] >= 1000 ? (d[metricKey] / 1000).toFixed(1) + 'K' : d[metricKey]))
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
