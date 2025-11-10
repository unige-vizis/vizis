<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Load the data
import jsonData from '../../../../data-processing/viz-datasets/viz2-2_pyramid_gdp_per_capita.json'
const dataset = ref(Array.isArray(jsonData && jsonData.data) ? jsonData.data : [])
const metadata = jsonData.metadata
const countriesByCategory = jsonData.countries_by_category || {}

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || container.clientWidth * 0.6
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
  // Remove any tooltips
  d3.selectAll('.pyramid-tooltip').remove()
})

function createChart() {
  if (!containerWidth.value || !containerHeight.value || !dataset.value.length) return

  const margin = { top: 50, right: 20, bottom: 60, left: 100 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 300

  // Clear any existing chart and tooltips
  d3.select(chartRef.value).selectAll('*').remove()
  d3.selectAll('.pyramid-tooltip').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Organize data for pyramid chart
  const primarySecondary = dataset.value.filter(d => d.Category === 'Primary+Secondary Dominated')
  const tertiary = dataset.value.filter(d => d.Category === 'Tertiary Dominated')

  // Get all unique GDP brackets in order and their groups
  const gdpBrackets = metadata.bins
  const binGroups = metadata.bin_groups || []

  // Separate bins into low and high groups
  const lowBins = []
  const highBins = []
  gdpBrackets.forEach((bin, i) => {
    if (binGroups[i] === 'low') {
      lowBins.push(bin)
    } else {
      highBins.push(bin)
    }
  })

  // Create tooltip
  const tooltip = d3.select('body').append('div')
    .attr('class', 'pyramid-tooltip')
    .style('position', 'absolute')
    .style('visibility', 'hidden')
    .style('background-color', 'rgba(0, 0, 0, 0.85)')
    .style('color', 'white')
    .style('padding', '10px')
    .style('border-radius', '5px')
    .style('font-size', '0.9rem')
    .style('max-width', '300px')
    .style('z-index', '1000')
    .style('pointer-events', 'none')
    .style('line-height', '1.4')

  // Create two separate Y scales with a gap
  const gapSize = 30  // Space between the two groups
  const totalBins = lowBins.length + highBins.length
  const availableHeight = height - gapSize

  // Allocate height proportional to number of bins in each group
  const lowGroupHeight = (lowBins.length / totalBins) * availableHeight
  const highGroupHeight = (highBins.length / totalBins) * availableHeight

  const yLow = d3.scaleBand()
    .domain(lowBins)
    .range([0, lowGroupHeight])
    .padding(0.2)

  const yHigh = d3.scaleBand()
    .domain(highBins)
    .range([lowGroupHeight + gapSize, lowGroupHeight + gapSize + highGroupHeight])
    .padding(0.2)

  // Combined scale function
  const y = (bracket) => {
    const idx = gdpBrackets.indexOf(bracket)
    if (binGroups[idx] === 'low') {
      return yLow(bracket)
    } else {
      return yHigh(bracket)
    }
  }
  y.bandwidth = (bracket) => {
    const idx = gdpBrackets.indexOf(bracket)
    if (binGroups[idx] === 'low') {
      return yLow.bandwidth()
    } else {
      return yHigh.bandwidth()
    }
  }

  // X scale - count of countries (symmetric for pyramid)
  const maxCount = d3.max(dataset.value, d => d.count)
  const x = d3.scaleLinear()
    .domain([0, maxCount])
    .range([0, width / 2 - 10])

  // Add center line
  svg.append('line')
    .attr('x1', width / 2)
    .attr('x2', width / 2)
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', '#666')
    .attr('stroke-width', 1)
    .attr('stroke-dasharray', '4,4')

  // Add horizontal separator line between low and high groups
  const separatorY = lowGroupHeight + gapSize / 2
  svg.append('line')
    .attr('x1', -50)
    .attr('x2', width + 50)
    .attr('y1', separatorY)
    .attr('y2', separatorY)
    .attr('stroke', '#999')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '5,5')

  // Create bars for Primary+Secondary (left side)
  primarySecondary.forEach(d => {
    const bracket = d.GDP_bracket
    svg.append('rect')
      .attr('x', width / 2 - x(d.count))
      .attr('y', y(bracket))
      .attr('width', x(d.count))
      .attr('height', y.bandwidth())
      .attr('fill', '#8B4513')
      .attr('opacity', 0.8)
      .style('cursor', 'pointer')
      .on('mouseover', function(event) {
        d3.select(this).attr('opacity', 1)
        const countries = d.countries || []
        tooltip.html(`
          <strong>${bracket}</strong><br/>
          <strong>${d.count} countries:</strong><br/>
          ${countries.join(', ')}
        `)
        .style('visibility', 'visible')
      })
      .on('mousemove', function(event) {
        tooltip
          .style('top', (event.pageY - 10) + 'px')
          .style('left', (event.pageX + 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this).attr('opacity', 0.8)
        tooltip.style('visibility', 'hidden')
      })

    // Add count label on left side
    svg.append('text')
      .attr('x', width / 2 - x(d.count) - 5)
      .attr('y', y(bracket) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .attr('class', 'axis-text')
      .text(d.count)
      .style('font-size', '1rem')
  })

  // Create bars for Tertiary (right side)
  tertiary.forEach(d => {
    const bracket = d.GDP_bracket
    svg.append('rect')
      .attr('x', width / 2)
      .attr('y', y(bracket))
      .attr('width', x(d.count))
      .attr('height', y.bandwidth())
      .attr('fill', '#9370DB')
      .attr('opacity', 0.8)
      .style('cursor', 'pointer')
      .on('mouseover', function(event) {
        d3.select(this).attr('opacity', 1)
        const countries = d.countries || []
        tooltip.html(`
          <strong>${bracket}</strong><br/>
          <strong>${d.count} countries:</strong><br/>
          ${countries.join(', ')}
        `)
        .style('visibility', 'visible')
      })
      .on('mousemove', function(event) {
        tooltip
          .style('top', (event.pageY - 10) + 'px')
          .style('left', (event.pageX + 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this).attr('opacity', 0.8)
        tooltip.style('visibility', 'hidden')
      })

    // Add count label on right side
    svg.append('text')
      .attr('x', width / 2 + x(d.count) + 5)
      .attr('y', y(bracket) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'start')
      .text(d.count)
      .style('font-size', '1rem')
  })

  // Y-axis (GDP brackets) on the left - two separate axes
  svg.append('g')
    .call(d3.axisLeft(yLow))
    .attr('class', 'axis-text')

  svg.append('g')
    .call(d3.axisLeft(yHigh))
    .attr('class', 'axis-text')

  // Add "Number of Countries" headers (one for each side)
  svg.append('text')
    .attr('class', 'pyramid-legend-header pyramid-legend-header-primary')
    .attr('x', width / 4)
    .attr('y', -30)
    .attr('text-anchor', 'middle')
    .text('Number of Countries')
    .style('font-size', '1rem')


  svg.append('text')
    .attr('class', 'pyramid-legend-header pyramid-legend-header-tertiary')
    .attr('x', width * 3 / 4)
    .attr('y', -30)
    .attr('text-anchor', 'middle')
    .text('Number of Countries')
    .style('font-size', '1rem')

  svg.append('g')
    .call(d3.axisLeft(yHigh))
    .style('font-size', '1rem')

  // Add category labels
  svg.append('text')
    .attr('class', 'pyramid-category-label pyramid-category-label-primary')
    .attr('x', width / 4)
    .attr('y', -15)
    .attr('text-anchor', 'middle')
    .text('Primary+Secondary Dominated')
    .style('font-size', '1rem')

  svg.append('text')
    .attr('class', 'pyramid-category-label pyramid-category-label-tertiary')
    .attr('x', width * 3 / 4)
    .attr('y', -15)
    .attr('text-anchor', 'middle')
    .text('Tertiary Dominated')
    .style('font-size', '1rem')

  // Add Y-axis label
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -margin.left + 20)
    .attr('text-anchor', 'middle')
    .attr('class', 'axis-label')
    .text('GDP per Capita (USD)')
    .style('font-size', '1rem')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
