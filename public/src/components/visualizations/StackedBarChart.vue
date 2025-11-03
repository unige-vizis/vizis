<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const data = ref([])
const countries = ref([])

onMounted(async () => {
  await loadData()
  createChart()
})

async function loadData() {
  try {
    const response = await fetch('/vizis/src/assets/data/viz5_stacked_bar_sectors.json')
    const jsonData = await response.json()

    // Store countries order
    countries.value = jsonData.countries

    // Transform the data structure for D3
    const countryData = {}
    jsonData.data.forEach(item => {
      if (!countryData[item.country]) {
        countryData[item.country] = { country: item.country }
      }
      countryData[item.country][item.sector] = item.percentage
    })

    // Convert to array in the correct order
    data.value = countries.value.map(country => countryData[country])
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

function createChart() {
  if (!data.value || data.value.length === 0) return

  const margin = { top: 20, right: 150, bottom: 60, left: 100 }
  const width = 800 - margin.left - margin.right
  const height = 600 - margin.top - margin.bottom // Increased height for 20 countries

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

  // Define sectors in the order they should be stacked
  const subgroups = ['Primary', 'Secondary', 'Tertiary', 'Tourism']
  const countryList = processedData.map(d => d.country)

  // Stack the data - filter out Tourism if not present
  const stackedData = d3.stack()
    .keys(subgroups)
    .value((d, key) => d[key] || 0) // Default to 0 if Tourism is missing
    (processedData)

  // Create scales
  const x = d3.scaleLinear()
    .domain([0, 100])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(countryList)
    .range([0, height])
    .padding(0.2)

  // Color scale for economic sectors
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(['#8B4513', '#4682B4', '#9370DB', '#FFB366']) // Brown, Steel Blue, Medium Purple, Light Orange

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(10).tickFormat(d => d + '%'))
    .selectAll('text')
    .style('fill', '#c7c7c7')

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

  // Add legend
  const legend = svg.append('g')
    .attr('transform', `translate(${width + 20}, 0)`)

  const legendItems = legend.selectAll('.legend-item')
    .data(subgroups)
    .enter()
    .append('g')
    .attr('class', 'legend-item')
    .attr('transform', (d, i) => `translate(0, ${i * 25})`)

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
    .style('font-size', '12px')

  // Add axis labels
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 15)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '13px')
    .text('Economic Sector Composition (%)')
}

function formatLabel(key) {
  const labels = {
    'Primary': 'Primary Sector (Agriculture, Mining)',
    'Secondary': 'Secondary Sector (Manufacturing)',
    'Tertiary': 'Tertiary Sector (Services)',
    'Tourism': 'Tourism'
  }
  return labels[key] || key
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
