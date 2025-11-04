<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Load the data directly via import
import jsonData from '@/assets/data/viz3_event_types.json'
const dataset = ref(Array.isArray(jsonData && jsonData.data) ? jsonData.data : [])

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || 500 // Fixed height for very narrow, compact visualization
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
  if (!containerWidth.value || !containerHeight.value || dataset.value.length === 0) return

  const margin = { top: 15, right: 30, bottom: 60, left: 110 }
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

  // List of subgroups (event types) - updated to match viz3 data
  const subgroups = ['Battles', 'Explosions/Remote violence', 'Protests & Riots', 'Violence against civilians']

  // List of groups (countries)
  const groups = dataset.value.map(d => d.country)

  // Create scales for horizontal grouped bars
  // y0: country bands (vertical position), y1: subgroups within each country
  const y0 = d3.scaleBand()
    .domain(groups)
    .range([0, height])
    .padding(0.1) // Minimal padding for thicker bars

  const y1 = d3.scaleBand()
    .domain(subgroups)
    .range([0, y0.bandwidth()])
    .padding(0.05) // Reduced padding for thicker individual bars

  // x: linear scale for counts (horizontal)
  const x = d3.scaleLinear()
    .domain([0, d3.max(dataset.value, d => d3.max(subgroups, k => (d[k] || 0))) || 0])
    .range([0, width])

  // Add X axis (counts)
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(',')))
    .selectAll('text')
    .style('font-size', '1rem')

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  // Add Y axis (countries)
  svg.append('g')
    .call(d3.axisLeft(y0))
    .selectAll('text')
    .style('font-size', '1rem')

  // Color scale for 4 event types
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(['#2563EB', '#D97706', '#059669', '#DC2626']) // Blue, Orange, Green, Red

  // Add bars (horizontal grouped bars)
  svg.append('g')
    .selectAll('g')
    .data(dataset.value)
    .enter()
    .append('g')
    .attr('transform', d => `translate(0,${y0(d.country)})`)
    .selectAll('rect')
    .data(d => subgroups.map(key => ({ key, value: d[key], country: d.country })))
    .enter()
    .append('rect')
    .attr('y', d => y1(d.key))
    .attr('x', 0)
    .attr('height', y1.bandwidth())
    .attr('width', d => x(d.value))
    .attr('fill', d => color(d.key))
    .attr('opacity', 0.8)
    .on('mouseover', function() {
      d3.select(this).attr('opacity', 1)
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0.8)
    })

  // Add legend - bottom right corner
  const legend = svg.append('g')
    .attr('transform', `translate(${Math.max(width - 200, 10)}, ${height - 110})`)

  legend.selectAll('rect')
    .data([...subgroups])
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d, i) => i * 25)
    .attr('width', 18)
    .attr('height', 18)
    .attr('fill', (d, i) => color(subgroups[i]))
    .attr('opacity', 0.8)

  legend.selectAll('text')
    .data([...subgroups])
    .enter()
    .append('text')
    .attr('x', 25)
    .attr('y', (d, i) => i * 25 + 13)
    .text(d => d)
    .style('font-size', '1rem')

  // Add X axis label (counts)
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 8)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .text('Number of Events')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
