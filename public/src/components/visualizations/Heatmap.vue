<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const data = ref([])
const years = ref([])
const eventTypes = ref([])

// Load the data from assets folder
async function loadData() {
  try {
    const response = await fetch('/vizis/src/assets/data/viz4_heatmap_event_types_years.json')
    const jsonData = await response.json()
    data.value = Array.isArray(jsonData && jsonData.data) ? jsonData.data : []

    // Extract unique years and event types
    years.value = [...new Set(data.value.map(d => d.year))].sort()
    eventTypes.value = [...new Set(data.value.map(d => d.event_type))].sort()
  } catch (error) {
    console.error('Error loading heatmap data:', error)
  }
}

onMounted(async () => {
  await loadData()
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 120, bottom: 60, left: 220 }
  const width = 1100 - margin.left - margin.right
  const height = 420 - margin.top - margin.bottom

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
    .domain(years.value)
    .range([0, width])
    .padding(0.05)

  const y = d3.scaleBand()
    .domain(eventTypes.value)
    .range([0, height])
    .padding(0.05)

  // Two monochrome color scales for dual encoding
  // Purples for event counts (upper half)
  const eventColorScale = d3.scaleSequential()
    .interpolator(d3.interpolatePurples)
    .domain([0, d3.max(data.value, d => d.event_count)])

  // Reds for fatalities (lower half) - red implies danger/death
  const fatalityColorScale = d3.scaleSequential()
    .interpolator(d3.interpolateReds)
    .domain([0, d3.max(data.value, d => d.total_fatalities)])

  // Function to determine text color based on background intensity
  const getTextColor = (value, maxValue) => {
    const normalized = value / maxValue
    // Use white text for dark backgrounds (high intensity), dark text for light
    return normalized > 0.5 ? '#ffffff' : '#1a1a1a'
  }

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '11px')

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  // Add Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '12px')

  // Tooltip
  const tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', '#fff')
    .style('padding', '8px 12px')
    .style('border-radius', '4px')
    .style('font-size', '12px')
    .style('pointer-events', 'none')
    .style('opacity', 0)

  // Add cells with horizontal split
  const cells = svg.selectAll('.cell')
    .data(data.value)
    .enter()
    .append('g')
    .attr('class', 'cell')

  // Upper half (event counts - blue)
  cells.append('rect')
    .attr('x', d => x(d.year))
    .attr('y', d => y(d.event_type))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth() / 2)
    .attr('fill', d => eventColorScale(d.event_count))
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 0.5)
    .on('mouseover', function(event, d) {
      d3.select(this.parentNode).selectAll('rect')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)

      tooltip
        .style('opacity', 1)
        .html(`<strong>${d.event_type}</strong><br/>${d.year}: ${d.event_count.toLocaleString()} events<br/>Fatalities: ${d.total_fatalities.toLocaleString()}`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this.parentNode).selectAll('rect')
        .attr('stroke', '#1a1a1a')
        .attr('stroke-width', 0.5)

      tooltip.style('opacity', 0)
    })

  // Lower half (fatalities - orange)
  cells.append('rect')
    .attr('x', d => x(d.year))
    .attr('y', d => y(d.event_type) + y.bandwidth() / 2)
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth() / 2)
    .attr('fill', d => fatalityColorScale(d.total_fatalities))
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 0.5)
    .on('mouseover', function(event, d) {
      d3.select(this.parentNode).selectAll('rect')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)

      tooltip
        .style('opacity', 1)
        .html(`<strong>${d.event_type}</strong><br/>${d.year}: ${d.event_count.toLocaleString()} events<br/>Fatalities: ${d.total_fatalities.toLocaleString()}`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this.parentNode).selectAll('rect')
        .attr('stroke', '#1a1a1a')
        .attr('stroke-width', 0.5)

      tooltip.style('opacity', 0)
    })

  // Add text labels for event counts (upper half - blue area)
  cells.append('text')
    .attr('x', d => x(d.year) + x.bandwidth() / 2)
    .attr('y', d => y(d.event_type) + y.bandwidth() * 0.25)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('fill', d => getTextColor(d.event_count, d3.max(data.value, d => d.event_count)))
    .style('font-size', '9px')
    .style('font-weight', '600')
    .style('pointer-events', 'none')
    .text(d => {
      // Format numbers: use K for thousands
      if (d.event_count >= 1000) {
        return (d.event_count / 1000).toFixed(1) + 'K'
      }
      return d.event_count
    })

  // Add text labels for fatalities (lower half - orange area)
  cells.append('text')
    .attr('x', d => x(d.year) + x.bandwidth() / 2)
    .attr('y', d => y(d.event_type) + y.bandwidth() * 0.75)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('fill', d => getTextColor(d.total_fatalities, d3.max(data.value, d => d.total_fatalities)))
    .style('font-size', '9px')
    .style('font-weight', '600')
    .style('pointer-events', 'none')
    .text(d => {
      // Format numbers: use K for thousands
      if (d.total_fatalities >= 1000) {
        return (d.total_fatalities / 1000).toFixed(1) + 'K'
      }
      return d.total_fatalities
    })

  // Add legend labels at the end of the first row
  const firstEventType = eventTypes.value[0]
  const lastYear = years.value[years.value.length - 1]

  // Get mid-intensity colors for backgrounds
  const maxEvents = d3.max(data.value, d => d.event_count)
  const maxFatalities = d3.max(data.value, d => d.total_fatalities)
  const midPurple = eventColorScale(maxEvents * 0.5)
  const midRed = fatalityColorScale(maxFatalities * 0.5)

  // "Events" label with background in upper half
  const eventsLabelX = x(lastYear) + x.bandwidth() + 10
  const eventsLabelY = y(firstEventType) + y.bandwidth() * 0.25

  svg.append('rect')
    .attr('x', eventsLabelX - 5)
    .attr('y', eventsLabelY - 11)
    .attr('width', 60)
    .attr('height', 22)
    .attr('fill', midPurple)
    .attr('rx', 3)

  svg.append('text')
    .attr('x', eventsLabelX + 30)
    .attr('y', eventsLabelY)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('fill', '#ffffff')
    .style('font-size', '13px')
    .style('font-weight', '600')
    .text('Events')

  // "Fatalities" label with background in lower half
  const fatalitiesLabelX = x(lastYear) + x.bandwidth() + 10
  const fatalitiesLabelY = y(firstEventType) + y.bandwidth() * 0.75

  svg.append('rect')
    .attr('x', fatalitiesLabelX - 5)
    .attr('y', fatalitiesLabelY - 11)
    .attr('width', 75)
    .attr('height', 22)
    .attr('fill', midRed)
    .attr('rx', 3)

  svg.append('text')
    .attr('x', fatalitiesLabelX + 37.5)
    .attr('y', fatalitiesLabelY)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('fill', '#ffffff')
    .style('font-size', '13px')
    .style('font-weight', '600')
    .text('Fatalities')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart {
  width: 100%;
  /* Inherits max-width from global .chart (--viz-content-width) */
  position: relative;
}

.chart svg {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}

.data-note {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #888;
  font-style: italic;
  text-align: center;
}
</style>
