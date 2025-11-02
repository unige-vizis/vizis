<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Load the data from data-processing/viz-datasets/viz1_bar_chart_sectors_conflicts.json and extract the array
import data from '../../../../data-processing/viz-datasets/viz1_bar_chart_sectors_conflicts.json'
const dataset = Array.isArray(data && data.data) ? data.data : []

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

  const margin = { top: 20, right: 120, bottom: 60, left: 100 }
  const width = containerWidth.value - margin.left - margin.right
  const height = containerHeight.value - margin.top - margin.bottom

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const x = d3.scaleLinear()
    .domain([0, d3.max(dataset, d => d.event_count) || 0])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(dataset.map(d => d.country))
    .range([0, height])
    .padding(0.2)

  // Use a 0-100 domain for percentage mapping so the legend is always percent-based.
  const color = d3.scaleSequential()
    .domain([0, 100])
    .interpolator(value => d3.interpolatePurples(0.3 + value * 0.7))

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  // Add Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '12px')

  // Add bars
  svg.selectAll('rect')
    .data(dataset)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', d => y(d.country))
    .attr('width', d => x(d.event_count))
    .attr('height', y.bandwidth())
    .attr('fill', d => color(d["Primary_%"]))
    .attr('opacity', 0.9)
    .on('mouseover', function() {
      d3.select(this).attr('opacity', 1)
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0.9)
    })
    // Add a simple tooltip via <title>
    .append('title')
    .text(d => `${d.country} — Primary: ${d["Primary_%"]}%\nEvents: ${d.event_count}`)

  // Add value labels
  svg.selectAll('.label')
    .data(dataset)
    .enter()
    .append('text')
    .attr('class', 'label')
    .attr('x', d => x(d.event_count) + 5)
    .attr('y', d => y(d.country) + y.bandwidth() / 2)
    .attr('dy', '.35em')
    .text(d => d.event_count)
    .style('fill', '#e0e0e0')
    .style('font-size', '11px')

  // Add axis labels
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 10)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '13px')
    .text('Number of Conflict Events')

  // Legend: vertical gradient showing Primary_% from 0 to 100
  const legendWidth = 15
  const legendHeight = height
  const legendX = width + 60
  const legendY = height * 0.01

  // defs + linearGradient
  const defs = svg.append('defs')
  const gradientId = 'legend-gradient'
  const gradient = defs.append('linearGradient')
    .attr('id', gradientId)
    .attr('x1', '0%')
    .attr('x2', '0%')
    .attr('y1', '100%')
    .attr('y2', '0%')

  const stops = d3.range(0, 1.001, 0.05)
  gradient.selectAll('stop')
    .data(stops)
    .enter()
    .append('stop')
    .attr('offset', d => `${d * 100}%`)
    .attr('stop-color', d => d3.interpolatePurples(0.3 + d * 0.7))

  // Draw legend rect
  svg.append('rect')
    .attr('x', legendX)
    .attr('y', legendY)
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .style('fill', `url(#${gradientId})`)
    .style('stroke', '#666')
    .style('stroke-width', 0.5)

  // Legend axis scale (0-100)
  const legendScale = d3.scaleLinear()
    .domain([0, 100])
    .range([legendHeight, 0])

  const legendAxis = d3.axisRight(legendScale)
    .ticks(5)
    .tickFormat(d => d + '%')

  svg.append('g')
    .attr('transform', `translate(${legendX + legendWidth}, ${legendY})`)
    .call(legendAxis)
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '11px')

  // Legend label
  svg.append('text')
    .attr('x', legendX + legendWidth / 2)
    .attr('y', legendY - 15)
    .style('fill', '#999')
    .style('font-size', '12px')
    .style('text-anchor', 'middle')
    .text('Primary %')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
