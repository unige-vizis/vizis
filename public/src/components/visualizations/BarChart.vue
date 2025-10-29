<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Placeholder data - will be replaced with real JSON data later
const data = [
  { country: 'Syria', events: 1245 },
  { country: 'Nigeria', events: 987 },
  { country: 'Iraq', events: 856 },
  { country: 'Afghanistan', events: 734 },
  { country: 'Pakistan', events: 623 },
  { country: 'Yemen', events: 512 },
  { country: 'India', events: 445 },
  { country: 'Somalia', events: 398 },
  { country: 'Libya', events: 321 },
  { country: 'Egypt', events: 287 }
]

onMounted(() => {
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 30, bottom: 60, left: 100 }
  const width = 800 - margin.left - margin.right
  const height = 500 - margin.top - margin.bottom

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
    .domain([0, d3.max(data, d => d.events)])
    .range([0, width])

  const y = d3.scaleBand()
    .domain(data.map(d => d.country))
    .range([0, height])
    .padding(0.2)

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
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

  // Add bars
  svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', d => y(d.country))
    .attr('width', d => x(d.events))
    .attr('height', y.bandwidth())
    .attr('fill', '#c6c7ff')
    .attr('opacity', 0.8)
    .on('mouseover', function() {
      d3.select(this).attr('opacity', 1)
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0.8)
    })

  // Add value labels
  svg.selectAll('.label')
    .data(data)
    .enter()
    .append('text')
    .attr('class', 'label')
    .attr('x', d => x(d.events) + 5)
    .attr('y', d => y(d.country) + y.bandwidth() / 2)
    .attr('dy', '.35em')
    .text(d => d.events)
    .style('fill', '#e0e0e0')
    .style('font-size', '11px')

  // Add axis labels
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 10)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '13px')
    .text('Number of Religion-Related Violent Events')
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
  max-width: 850px;
  overflow-x: auto;
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
