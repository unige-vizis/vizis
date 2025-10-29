<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Placeholder data - event types distribution
const data = [
  { country: 'Syria', protests: 25, violence: 55, battles: 20 },
  { country: 'Nigeria', protests: 40, violence: 35, battles: 25 },
  { country: 'Iraq', protests: 30, violence: 45, battles: 25 },
  { country: 'Pakistan', protests: 50, violence: 30, battles: 20 },
  { country: 'India', protests: 60, violence: 25, battles: 15 },
  { country: 'Yemen', protests: 20, violence: 50, battles: 30 }
]

onMounted(() => {
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 150, bottom: 60, left: 100 }
  const width = 800 - margin.left - margin.right
  const height = 450 - margin.top - margin.bottom

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Process data to calculate percentages
  const processedData = data.map(d => {
    const total = d.protests + d.violence + d.battles
    return {
      country: d.country,
      protests: (d.protests / total) * 100,
      violence: (d.violence / total) * 100,
      battles: (d.battles / total) * 100
    }
  })

  const subgroups = ['protests', 'violence', 'battles']
  const countries = data.map(d => d.country)

  // Stack the data
  const stackedData = d3.stack()
    .keys(subgroups)
    (processedData)

  // Create scales
  const x = d3.scaleLinear()
    .domain([0, 100])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(countries)
    .range([0, height])
    .padding(0.2)

  // Color scale
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(['#c6c7ff', '#9370db', '#721288'])

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
    .text('Percentage of Event Types (%)')
}

function formatLabel(key) {
  const labels = {
    protests: 'Protests',
    violence: 'Violence Against Civilians',
    battles: 'Battles'
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
