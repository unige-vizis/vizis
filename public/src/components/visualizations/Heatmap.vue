<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Placeholder data - monthly frequency of religion-related protests across countries
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const countries = ['Syria', 'Nigeria', 'Iraq', 'Pakistan', 'India', 'Yemen']

// Generate placeholder data
const data = []
countries.forEach(country => {
  months.forEach((month, i) => {
    data.push({
      country,
      month,
      monthIndex: i,
      value: Math.floor(Math.random() * 50) + 10
    })
  })
})

onMounted(() => {
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 30, bottom: 60, left: 100 }
  const width = 900 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

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
    .domain(months)
    .range([0, width])
    .padding(0.05)

  const y = d3.scaleBand()
    .domain(countries)
    .range([0, height])
    .padding(0.05)

  // Color scale
  const colorScale = d3.scaleSequential()
    .interpolator(d3.interpolateRgb('#2d1b3d', '#c6c7ff'))
    .domain([0, d3.max(data, d => d.value)])

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

  // Add cells
  svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', d => x(d.month))
    .attr('y', d => y(d.country))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .attr('fill', d => colorScale(d.value))
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 1)
    .on('mouseover', function(event, d) {
      d3.select(this)
        .attr('stroke', '#c6c7ff')
        .attr('stroke-width', 2)

      tooltip
        .style('opacity', 1)
        .html(`<strong>${d.country}</strong><br/>${d.month}: ${d.value} events`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this)
        .attr('stroke', '#1a1a1a')
        .attr('stroke-width', 1)

      tooltip.style('opacity', 0)
    })

  // Add legend
  const legendWidth = 300
  const legendHeight = 10

  const legend = svg.append('g')
    .attr('transform', `translate(${(width - legendWidth) / 2}, ${height + 40})`)

  const legendScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .range([0, legendWidth])

  const legendAxis = d3.axisBottom(legendScale)
    .ticks(5)

  // Create gradient
  const defs = svg.append('defs')
  const gradient = defs.append('linearGradient')
    .attr('id', 'heatmap-gradient')

  gradient.selectAll('stop')
    .data([
      { offset: '0%', color: '#2d1b3d' },
      { offset: '100%', color: '#c6c7ff' }
    ])
    .enter()
    .append('stop')
    .attr('offset', d => d.offset)
    .attr('stop-color', d => d.color)

  legend.append('rect')
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .style('fill', 'url(#heatmap-gradient)')

  legend.append('g')
    .attr('transform', `translate(0, ${legendHeight})`)
    .call(legendAxis)
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '11px')

  legend.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  legend.append('text')
    .attr('x', legendWidth / 2)
    .attr('y', legendHeight + 35)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '12px')
    .text('Number of Protests')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
    <p class="data-note">Note: This visualization uses placeholder data. Real data from ACLED will be integrated in the next iteration.</p>
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
  max-width: 950px;
  overflow-x: auto;
  position: relative;
}

.chart svg {
  display: block;
  margin: 0 auto;
}

.data-note {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #888;
  font-style: italic;
  text-align: center;
}
</style>
