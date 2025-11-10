<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Load the data
import jsonData from '../../../../data-processing/viz-datasets/viz2-3_ridge_inflation.json'
const dataset = ref(Array.isArray(jsonData && jsonData.data) ? jsonData.data : [])
const metadata = jsonData.metadata

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || container.clientWidth * 0.8
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
  if (!containerWidth.value || !containerHeight.value || !dataset.value.length) return

  const margin = { top: 100, right: 20, bottom: 80, left: 80 }
  const width = containerWidth.value - margin.left - margin.right
  const ridgeHeight = 60
  const ridgeSpacing = 45

  // Get unique years
  const years = [...new Set(dataset.value.map(d => d.year))].sort()
  const height = years.length * ridgeSpacing

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svgRoot = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)

  const svg = svgRoot
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // X scale - linear from 0 to 20%
  const x = d3.scaleLinear()
    .domain([0, 20])
    .range([0, width])

  // Y scale - position for each year
  const y = d3.scalePoint()
    .domain(years)
    .range([0, height])
    .padding(0)

  // Color scale for categories - matching pyramid chart colors
  const colorScale = {
    'Primary+Secondary Dominated': '#8B4513',
    'Tertiary Dominated': '#9370DB'
  }

  // Kernel density estimation
  function kernelDensityEstimator(kernel, X) {
    return function(V) {
      return X.map(x => [x, d3.mean(V, v => kernel(x - v))])
    }
  }

  function kernelEpanechnikov(k) {
    return v => Math.abs(v /= k) <= 1 ? 0.75 * (1 - v * v) / k : 0
  }

  // Bandwidth for density estimation - larger value for smoother curves
  const bandwidth = 1.0

  // Sample points for density estimation from 0 to 20%
  const xTicks = d3.range(0, 20, 20 / 300)

  // Draw ridges for each year and category
  years.forEach((year, yearIndex) => {
    const yearData = dataset.value.filter(d => d.year === year)
    const baselineY = y(year)

    // Draw horizontal baseline for each year
    svg.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', baselineY)
      .attr('y2', baselineY)
      .attr('stroke', '#ddd')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2')

    yearData.forEach(categoryData => {
      if (categoryData.values.length === 0) return

      const kde = kernelDensityEstimator(kernelEpanechnikov(bandwidth), xTicks)
      const density = kde(categoryData.values)

      // Scale density values to fit ridge height
      const maxDensity = d3.max(density, d => d[1])
      const yScale = d3.scaleLinear()
        .domain([0, maxDensity])
        .range([0, ridgeHeight])

      // Create area path - centered on the year line
      const area = d3.area()
        .curve(d3.curveBasis)
        .x(d => x(d[0]))
        .y0(baselineY)
        .y1(d => baselineY - yScale(d[1]))

      // Draw filled area
      svg.append('path')
        .datum(density)
        .attr('fill', colorScale[categoryData.category])
        .attr('opacity', 0.7)
        .attr('stroke', '#000')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.8)
        .attr('d', area)
    })
  })

  // Add X-axis at bottom
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x)
      .ticks(10)
      .tickFormat(d => `${d}%`)
    )
    .attr('class', 'axis-text')

  // Add Y-axis with years
  svg.append('g')
    .call(d3.axisLeft(y))
    .attr('class', 'axis-text')

  // Add X-axis label
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 35)
    .attr('text-anchor', 'middle')
    .attr('class', 'axis-label')
    .text('Annual Inflation Rate')

  // Add Y-axis label
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -margin.left + 20)
    .attr('text-anchor', 'middle')
    .attr('class', 'axis-label')
    .text('Year')

  // Add legend (horizontal at top, outside plot area)
  const legend = svgRoot.append('g')
    .attr('transform', `translate(${margin.left + width / 2}, 10)`)

  // Primary+Secondary legend item
  legend.append('rect')
    .attr('class', 'ridge-legend-rect ridge-legend-rect-primary')
    .attr('x', -250)
    .attr('y', 0)
    .attr('width', 20)
    .attr('height', 20)

  legend.append('text')
    .attr('class', 'ridge-legend-text ridge-legend-text-primary')
    .attr('x', -222)
    .attr('y', 10)
    .attr('dy', '0.35em')
    .text('Primary+Secondary Dominated')

  // Tertiary legend item
  legend.append('rect')
    .attr('class', 'ridge-legend-rect ridge-legend-rect-tertiary')
    .attr('x', 60)
    .attr('y', 0)
    .attr('width', 20)
    .attr('height', 20)

  legend.append('text')
    .attr('class', 'ridge-legend-text ridge-legend-text-tertiary')
    .attr('x', 88)
    .attr('y', 10)
    .attr('dy', '0.35em')
    .text('Tertiary Dominated')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
