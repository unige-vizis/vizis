<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)
const normalizeByPopulation = ref(false)

// Load the data from data-processing/viz-datasets/viz1_bar_chart_sectors_conflicts.json and extract the array
import data from '../../../../data-processing/viz-datasets/viz1_bar_chart_sectors_conflicts.json'
const dataset = Array.isArray(data && data.data) ? data.data : []

// Distinct countries to highlight (analysis subset)
const highlightedCountries = new Set(['Somalia', 'United States', 'Afghanistan', 'India', 'Ukraine', 'Mexico', 'Italy'])

// Watch for toggle changes and update chart with transitions
watch(normalizeByPopulation, () => {
  updateChart()
})

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

  const margin = { top: 20, right: 80, bottom: 60, left: 130 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 500

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales - use either absolute or per capita values
  const getValue = d => normalizeByPopulation.value ? d.events_per_100k : d.event_count
  const x = d3.scaleLinear()
    .domain([0, d3.max(dataset, d => getValue(d)) || 0])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(dataset.map(d => d.country))
    .range([0, height])
    .padding(0.2)

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  // Add Y axis
  svg.append('g')
    .attr('class', 'y-axis')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '1rem')

  // Add bars
  const bars = svg.selectAll('.bar')
    .data(dataset)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', 0)
    .attr('y', d => y(d.country))
    .attr('width', d => x(getValue(d)))
    .attr('height', y.bandwidth())
    .attr('fill', d => highlightedCountries.has(d.country) ? '#CC9966' : '#9966cc')
    .attr('opacity', 0.9)
    .on('mouseover', function() {
      d3.select(this).attr('opacity', 1)
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0.9)
    })

  // Add tooltips to bars
  bars.append('title')
    .text(d => {
      const value = normalizeByPopulation.value
        ? `${d.events_per_100k} per 100k`
        : d.event_count
      return `${d.country}\nEvents: ${value}`
    })

  // Add value labels
  svg.selectAll('.label')
    .data(dataset)
    .enter()
    .append('text')
    .attr('class', 'label')
    .attr('x', d => x(getValue(d)) + 5)
    .attr('y', d => y(d.country) + y.bandwidth() / 2)
    .attr('dy', '.35em')
    .text(d => normalizeByPopulation.value
      ? d.events_per_100k.toFixed(1)
      : d.event_count)
    .style('font-size', '1rem')

  // Add axis labels
  const axisLabel = normalizeByPopulation.value
    ? 'Conflict Events per 100000 Population'
    : 'Number of Conflict Events'

  svg.append('text')
    .attr('class', 'x-axis-label')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 10)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .text(axisLabel)
}

function updateChart() {
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 20, right: 80, bottom: 60, left: 100 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 500

  // Select the existing SVG group
  const svg = d3.select(chartRef.value).select('svg g')
  if (svg.empty()) {
    createChart()
    return
  }

  // Update scales with new values
  const getValue = d => normalizeByPopulation.value ? d.events_per_100k : d.event_count
  const x = d3.scaleLinear()
    .domain([0, d3.max(dataset, d => getValue(d)) || 0])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(dataset.map(d => d.country))
    .range([0, height])
    .padding(0.2)

  // Update bars with smooth transitions
  svg.selectAll('.bar')
    .data(dataset)
    .transition()
    .duration(600)
    .ease(d3.easeCubicInOut)
    .attr('width', d => x(getValue(d)))
    .attr('fill', d => highlightedCountries.has(d.country) ? '#CC9966' : '#9966cc')

  // Update tooltips
  svg.selectAll('.bar')
    .select('title')
    .text(d => {
      const value = normalizeByPopulation.value
        ? `${d.events_per_100k} per 100k`
        : d.event_count
      return `${d.country}\nEvents: ${value}`
    })

  // Update value labels with smooth transitions
  svg.selectAll('.label')
    .data(dataset)
    .transition()
    .duration(600)
    .ease(d3.easeCubicInOut)
    .attr('x', d => x(getValue(d)) + 5)
    .tween('text', function(d) {
      const node = this
      const oldValue = parseFloat(node.textContent.replace(/,/g, '')) || 0
      const newValue = normalizeByPopulation.value ? d.events_per_100k : d.event_count
      const interpolator = d3.interpolateNumber(oldValue, newValue)

      return function(t) {
        const val = interpolator(t)
        node.textContent = normalizeByPopulation.value
          ? val.toFixed(1)
          : Math.round(val).toLocaleString()
      }
    })

  // Update axis label
  const axisLabel = normalizeByPopulation.value
    ? 'Conflict Events per 100000 Population'
    : 'Number of Conflict Events'

  svg.select('.x-axis-label')
    .text(axisLabel)
}
</script>

<template>
  <div class="chart-wrapper">
    <div class="chart-controls">
      <label class="toggle-label">
        <input type="checkbox" v-model="normalizeByPopulation" class="toggle-checkbox-hidden" />
        <span class="toggle-switch">
          <span class="toggle-slider"></span>
        </span>
        <span class="toggle-text">Normalized by population</span>
      </label>
    </div>
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
