<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Load the data directly via import
import jsonData from '@/assets/data/viz2_stacked_bar_sectors.json'

// Store countries order
const countries = ref(jsonData.countries)

// Transform the data structure for D3
const countryData = {}
jsonData.data.forEach(item => {
  if (!countryData[item.country]) {
    countryData[item.country] = { country: item.country }
  }
  countryData[item.country][item.sector] = item.percentage
})

// Convert to array in the correct order
const data = ref(countries.value.map(country => countryData[country]))

onMounted(() => {
  createChart()
})

function createChart() {
  if (!data.value || data.value.length === 0) return

  const margin = { top: 50, right: 80, bottom: 20, left: 100 } // More space on top for legend, less on right and bottom
  const legendItemWidth = 180 // Width allocated for each legend item
  const width = legendItemWidth * 4 // Bar width matches legend width (4 items)
  const height = 350 - margin.top - margin.bottom // Adjusted for 7 countries

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Data is already in percentages, no need to recalculate
  const processedData = data.value

  // Define sectors in the order they should be stacked (Tourism shown separately)
  const subgroups = ['Primary', 'Secondary', 'Tertiary', 'Tourism']
  const countryList = processedData.map(d => d.country)

  // Stack the data
  const stackedData = d3.stack()
    .keys(subgroups)
    (processedData)

  // Create scales
  const x = d3.scaleLinear()
    .domain([0, 100])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(countryList)
    .range([0, height])
    .padding(0.3)

  // Color scale for economic sectors (4 colors)
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(['#8B4513', '#4682B4', '#9370DB', '#FFB366']) // Brown, Steel Blue, Medium Purple, Light Orange

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

  // Add bars
  svg.append('g')
    .selectAll('g')
    .data(stackedData)
    .enter()
    .append('g')
    .attr('fill', d => color(d.key))
    .attr('opacity', 0.8)
    .selectAll('rect')
    .data(d => d)
    .enter()
    .append('rect')
    .attr('x', d => x(d[0]))
    .attr('y', d => y(d.data.country))
    .attr('width', d => x(d[1]) - x(d[0]))
    .attr('height', y.bandwidth())
    .on('mouseover', function(event, d) {
      const key = d3.select(this.parentNode).datum().key
      const value = d[1] - d[0]

      d3.select(this.parentNode).attr('opacity', 1)

      tooltip
        .style('opacity', 1)
        .html(`<strong>${d.data.country}</strong><br/>${formatLabel(key)}: ${value.toFixed(1)}%`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this.parentNode).attr('opacity', 0.8)
      tooltip.style('opacity', 0)
    })

  // Add legend horizontally at the top
  const legend = svg.append('g')
    .attr('transform', `translate(0, -35)`) // Position above the chart

  const legendItems = legend.selectAll('.legend-item')
    .data(subgroups)
    .enter()
    .append('g')
    .attr('class', 'legend-item')
    .attr('transform', (d, i) => `translate(${i * legendItemWidth}, 0)`)

  legendItems.append('rect')
    .attr('width', 18)
    .attr('height', 18)
    .attr('fill', d => color(d))
    .attr('opacity', 0.8)

  legendItems.append('text')
    .attr('x', 25)
    .attr('y', 13)
    .text(d => formatLabel(d))
    .style('fill', '#c7c7c7')
    .style('font-size', '11px')

  // Add "No Data" labels for countries with missing tourism data (Tourism = 0)
  const countriesWithNoTourism = processedData.filter(d => !d.Tourism || d.Tourism === 0)

  svg.selectAll('.no-data-label')
    .data(countriesWithNoTourism)
    .enter()
    .append('text')
    .attr('class', 'no-data-label')
    .attr('x', width - 45) // Position on the bar, near the right end
    .attr('y', d => y(d.country) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .style('fill', '#FFB366') // Same orange as Tourism segment
    .style('font-size', '10px')
    .style('font-weight', 'bold')
    .text('No Data')
}

function formatLabel(key) {
  const labels = {
    'Primary': 'Primary',
    'Secondary': 'Secondary',
    'Tertiary': 'Tertiary',
    'Tourism': 'Tourism (part of Tertiary)'
  }
  return labels[key] || key
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
  max-width: 950px;
  position: relative;
}

.chart svg {
  display: block;
  margin: 0 auto;
}
</style>
