<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Number of top violent events to show per country
const TOP_EVENTS_COUNT = 200

// Load the data
import jsonData from '../../../../data-processing/viz-datasets/viz2-3_violin_fatalities_distribution.json'
const dataset = ref(Array.isArray(jsonData && jsonData.data) ? jsonData.data : [])

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
})

function createChart() {
  if (!containerWidth.value || !containerHeight.value || !dataset.value.length) return

  const margin = { top: 40, right: 40, bottom: 100, left: 80 }
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

  // Prepare data: filter top violent events per country
  const processedData = dataset.value.map(countryData => {
    const nonZeroValues = countryData.values.filter(v => v > 0)
    // Sort descending and take top N
    const topValues = nonZeroValues.sort((a, b) => b - a).slice(0, TOP_EVENTS_COUNT)
    return {
      country: countryData.country,
      values: topValues,
      allValuesCount: nonZeroValues.length,
      topValuesCount: topValues.length
    }
  })

  // Find min/max across all top events
  const allTopValues = processedData.flatMap(d => d.values)
  const maxFatality = d3.max(allTopValues) || 1000
  const yMax = Math.min(1000, maxFatality)

  // Y scale - linear fatalities
  const y = d3.scaleLinear()
    .domain([0, yMax])
    .range([height, 0])
    .nice()

  // X scale - countries
  const x = d3.scaleBand()
    .domain(processedData.map(d => d.country))
    .range([0, width])
    .padding(0.15)

  // Add axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .style('font-size', '0.9rem')
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end')

  // Y-axis with absolute value formatting
  svg.append('g')
    .call(d3.axisLeft(y)
      .ticks(10, "~s")
      .tickFormat(d => d3.format("~s")(d)))
    .style('font-size', '0.9rem')

  // Y-axis label
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', -margin.left + 20)
    .attr('x', -height / 2)
    .attr('text-anchor', 'middle')
    .style('font-size', '0.9rem')
    .style('fill', 'currentColor')
    .text('Fatalities per Event')

  // Color scale for individual points based on fatality value
  const pointColorScale = d3.scaleSequential()
    .domain([0, yMax])
    .interpolator(d3.interpolateYlOrRd)

  // Histogram function for creating bins
  const histogram = d3.histogram()
    .domain(y.domain())
    .thresholds(y.ticks(20))
    .value(d => d)

  // Compute binning for each country
  const sumstat = processedData.map(countryData => {
    const bins = histogram(countryData.values)
    return {
      country: countryData.country,
      bins: bins,
      values: countryData.values,
      allValuesCount: countryData.allValuesCount,
      topValuesCount: countryData.topValuesCount
    }
  })

  // Find maximum bin count across all countries for width scaling
  let maxNum = 0
  sumstat.forEach(d => {
    const lengths = d.bins.map(b => b.length)
    const longest = d3.max(lengths)
    if (longest > maxNum) maxNum = longest
  })

  // Scale for violin width (one-sided)
  const xNum = d3.scaleLinear()
    .range([0, x.bandwidth() / 2])
    .domain([0, maxNum])

  // Add violin shapes (left side only)
  sumstat.forEach(d => {
    const g = svg.append('g')
      .attr('transform', `translate(${x(d.country)}, 0)`)

    // Draw violin shape on left side
    g.append('path')
      .datum(d.bins)
      .style('stroke', 'none')
      .style('fill', '#999')
      .style('opacity', 0.6)
      .attr('d', d3.area()
        .x0(xNum(0))
        .x1(bin => xNum(bin.length))
        .y(bin => y(bin.x0))
        .curve(d3.curveCatmullRom)
      )
  })

  // Jitter width for individual points
  const jitterWidth = x.bandwidth() / 2.5

  // Flatten data for individual points
  const allPoints = []
  processedData.forEach(countryData => {
    countryData.values.forEach(value => {
      allPoints.push({
        country: countryData.country,
        value: value
      })
    })
  })

  // Add tooltip
  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('visibility', 'hidden')
    .style('background-color', 'rgba(0, 0, 0, 0.9)')
    .style('color', 'white')
    .style('padding', '6px 10px')
    .style('border-radius', '4px')
    .style('font-size', '0.8rem')
    .style('pointer-events', 'none')
    .style('z-index', '1000')

  // Add individual points with jitter on the right side
  svg
    .selectAll('indPoints')
    .data(allPoints)
    .enter()
    .append('circle')
    .attr('cx', d => x(d.country) + x.bandwidth() / 2 + Math.random() * jitterWidth)
    .attr('cy', d => y(d.value))
    .attr('r', 3)
    .style('fill', d => pointColorScale(d.value))
    .attr('stroke', 'white')
    .attr('stroke-width', 0.5)
    .style('opacity', 0.7)
    .on('mouseover', function(event, d) {
      d3.select(this)
        .style('opacity', 1)
        .attr('r', 4.5)
        .attr('stroke-width', 1.5)

      tooltip.style('visibility', 'visible')
        .html(`<strong>${d.country}</strong><br/>${d.value} fatalities`)
    })
    .on('mousemove', function(event) {
      tooltip
        .style('top', (event.pageY - 10) + 'px')
        .style('left', (event.pageX + 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this)
        .style('opacity', 0.7)
        .attr('r', 3)
        .attr('stroke-width', 0.5)

      tooltip.style('visibility', 'hidden')
    })

  // Add title
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', -20)
    .attr('text-anchor', 'middle')
    .style('font-size', '1.1rem')
    .style('font-weight', '600')
    .style('fill', 'currentColor')
    .text(`Distribution of Top ${TOP_EVENTS_COUNT} Most Violent Events by Country`)

  // Add note about data filtering
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 10)
    .attr('text-anchor', 'middle')
    .style('font-size', '0.75rem')
    .style('fill', '#666')
    .text(`Showing top ${TOP_EVENTS_COUNT} most violent events per country (excluding zero-fatality events)`)
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
