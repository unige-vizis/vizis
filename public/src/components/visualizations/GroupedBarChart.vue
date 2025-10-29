<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Placeholder data - comparing Middle East vs Sub-Saharan Africa (2020 vs 2023)
const data = [
  { region: 'Middle East', year2020: 1245, year2023: 987 },
  { region: 'Sub-Saharan Africa', year2020: 856, year2023: 1134 },
]

onMounted(() => {
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 30, bottom: 60, left: 80 }
  const width = 600 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // List of subgroups (years)
  const subgroups = ['year2020', 'year2023']

  // List of groups (regions)
  const groups = data.map(d => d.region)

  // Create scales
  const x0 = d3.scaleBand()
    .domain(groups)
    .range([0, width])
    .padding(0.3)

  const x1 = d3.scaleBand()
    .domain(subgroups)
    .range([0, x0.bandwidth()])
    .padding(0.1)

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => Math.max(d.year2020, d.year2023))])
    .range([height, 0])

  // Add X axis
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x0))
    .selectAll('text')
    .style('fill', '#c7c7c7')
    .style('font-size', '12px')
    .attr('transform', 'rotate(-15)')
    .style('text-anchor', 'end')

  svg.selectAll('.domain, .tick line')
    .style('stroke', '#666')

  // Add Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('fill', '#c7c7c7')

  // Color scale
  const color = d3.scaleOrdinal()
    .domain(subgroups)
    .range(['#c6c7ff', '#721288'])

  // Add bars
  svg.append('g')
    .selectAll('g')
    .data(data)
    .enter()
    .append('g')
    .attr('transform', d => `translate(${x0(d.region)},0)`)
    .selectAll('rect')
    .data(d => subgroups.map(key => ({ key, value: d[key], region: d.region })))
    .enter()
    .append('rect')
    .attr('x', d => x1(d.key))
    .attr('y', d => y(d.value))
    .attr('width', x1.bandwidth())
    .attr('height', d => height - y(d.value))
    .attr('fill', d => color(d.key))
    .attr('opacity', 0.8)
    .on('mouseover', function() {
      d3.select(this).attr('opacity', 1)
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0.8)
    })

  // Add value labels on bars
  svg.selectAll('.bar-label')
    .data(data.flatMap(d =>
      subgroups.map(key => ({ key, value: d[key], region: d.region }))
    ))
    .enter()
    .append('text')
    .attr('class', 'bar-label')
    .attr('x', d => x0(d.region) + x1(d.key) + x1.bandwidth() / 2)
    .attr('y', d => y(d.value) - 5)
    .attr('text-anchor', 'middle')
    .text(d => d.value)
    .style('fill', '#e0e0e0')
    .style('font-size', '11px')

  // Add legend
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 150}, 0)`)

  legend.selectAll('rect')
    .data(['2020', '2023'])
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d, i) => i * 25)
    .attr('width', 18)
    .attr('height', 18)
    .attr('fill', (d, i) => color(subgroups[i]))
    .attr('opacity', 0.8)

  legend.selectAll('text')
    .data(['2020', '2023'])
    .enter()
    .append('text')
    .attr('x', 25)
    .attr('y', (d, i) => i * 25 + 13)
    .text(d => d)
    .style('fill', '#c7c7c7')
    .style('font-size', '12px')

  // Add axis label
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + margin.bottom - 5)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '13px')
    .text('Region')

  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -margin.left + 20)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '13px')
    .text('Number of Events')
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
  max-width: 650px;
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
