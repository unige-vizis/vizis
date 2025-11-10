<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const tooltipRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Load the data
import jsonData from '../../../../data-processing/viz-datasets/viz2-3b_violin_debt_per_capita.json'
const dataset = ref(Array.isArray(jsonData && jsonData.data) ? jsonData.data : [])

// Color scale matching pyramid and ridge charts
const colorScale = {
  'Primary+Secondary Dominated': '#8B4513',
  'Tertiary Dominated': '#9370DB'
}

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

  console.log('Creating chart with data:', dataset.value)
  console.log('Tooltip ref:', tooltipRef.value)

  const margin = { top: 60, right: 40, bottom: 40, left: 100 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 210

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Find max value across all data
  const allValues = dataset.value.flatMap(d => d.data_points.map(p => p.value))
  const maxValue = d3.max(allValues) || 100000

  // Y scale - linear debt per capita
  const y = d3.scaleLinear()
    .domain([0, maxValue])
    .range([height, 0])
    .nice()

  // X scale - categories
  const x = d3.scaleBand()
    .domain(dataset.value.map(d => d.category))
    .range([0, width])
    .padding(0.3)

  // Add axes
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .style('font-size', '1rem')
    .selectAll('text')
    .style('text-anchor', 'middle')

  // Add horizontal grid lines
  svg.append('g')
    .attr('class', 'grid')
    .call(d3.axisLeft(y)
      .ticks(8)
      .tickSize(-width)
      .tickFormat('')
    )
    .style('stroke', '#444')
    .style('stroke-opacity', 0.3)
    .style('stroke-dasharray', '2,2')

  // Y-axis with dollar formatting
  svg.append('g')
    .call(d3.axisLeft(y)
      .ticks(8)
      .tickFormat(d => `$${d3.format(',.0f')(d)}`)
    )
    .style('font-size', '1rem')

  // Add Y-axis label
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -margin.left + 20)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .text('Debt per Capita (USD)')

  // Create tooltip
  const tooltip = d3.select(tooltipRef.value)

  // Kernel density estimation functions
  function kernelDensityEstimator(kernel, Y) {
    return function(V) {
      return Y.map(y => [y, d3.mean(V, v => kernel(y - v))])
    }
  }

  function kernelEpanechnikov(k) {
    return v => Math.abs(v /= k) <= 1 ? 0.75 * (1 - v * v) / k : 0
  }

  // Draw bubbles for each category
  dataset.value.forEach(categoryData => {
    console.log('Processing category:', categoryData.category, 'with', categoryData.data_points?.length, 'data points')

    if (!categoryData.data_points || categoryData.data_points.length === 0) {
      console.warn('No data_points for category:', categoryData.category)
      return
    }

    const categoryCenter = x(categoryData.category) + x.bandwidth() / 2
    const maxJitterRange = x.bandwidth() * 1.2

    // Calculate kernel density estimation for this category
    const values = categoryData.data_points.map(d => d.value)
    const bandwidth = (d3.max(values) - d3.min(values)) * 0.05 || 1
    const yTicks = d3.range(d3.min(values), d3.max(values), (d3.max(values) - d3.min(values)) / 100)
    const kde = kernelDensityEstimator(kernelEpanechnikov(bandwidth), yTicks)
    const density = kde(values)

    // Find max density for scaling
    const maxDensity = d3.max(density, d => d[1])

    // Create density lookup function
    function getDensityAt(value) {
      // Find closest density point
      let closestDensity = density[0]
      let minDiff = Math.abs(density[0][0] - value)

      for (const d of density) {
        const diff = Math.abs(d[0] - value)
        if (diff < minDiff) {
          minDiff = diff
          closestDensity = d
        }
      }

      return closestDensity[1]
    }

    // Prepare data with initial positions
    const nodes = categoryData.data_points.map(d => ({
      ...d,
      targetY: y(d.value),
      targetX: categoryCenter,
      densityWidth: maxJitterRange * (getDensityAt(d.value) / maxDensity),
      radius: 4
    }))

    // Create circles
    const circles = svg.selectAll(`.bubble-${categoryData.category.replace(/\+/g, '').replace(/\s/g, '')}`)
      .data(nodes)
      .enter()
      .append('circle')
      .attr('class', 'bubble')
      .attr('r', d => d.radius)
      .attr('fill', colorScale[categoryData.category])
      .attr('opacity', 0.6)
      .attr('stroke', '#000')
      .attr('stroke-width', 0.5)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        console.log('Mouseover:', d.country, d.value)
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 6)
          .attr('opacity', 1)
          .attr('stroke-width', 2)

        tooltip
          .style('opacity', 1)
          .style('left', `${event.clientX + 10}px`)
          .style('top', `${event.clientY - 10}px`)
          .html(`
            <strong>${d.country}</strong><br/>
            ${d.year ? `<span style="font-size: 0.85em; color: #ccc;">${d.year}</span><br/>` : ''}
            Debt: $${d3.format(',.0f')(d.value)}
          `)
      })
      .on('mousemove', function(event) {
        tooltip
          .style('left', `${event.clientX + 10}px`)
          .style('top', `${event.clientY - 10}px`)
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', 4)
          .attr('opacity', 0.6)
          .attr('stroke-width', 0.5)

        tooltip.style('opacity', 0)
      })

    // Create force simulation to prevent overlap
    const simulation = d3.forceSimulation(nodes)
      .force('x', d3.forceX(d => d.targetX).strength(0.05))
      .force('y', d3.forceY(d => d.targetY).strength(1.5))
      .force('collide', d3.forceCollide().radius(d => d.radius + 0.5).strength(0.9))
      .force('bounds', () => {
        // Custom force to constrain within violin width and above x-axis
        nodes.forEach(node => {
          const maxX = node.targetX + node.densityWidth
          const minX = node.targetX - node.densityWidth
          if (node.x > maxX) node.x = maxX
          if (node.x < minX) node.x = minX

          // Prevent bubbles from overlapping with x-axis (accounting for radius)
          if (node.y > height - node.radius) node.y = height - node.radius
          // Keep bubbles above the top
          if (node.y < node.radius) node.y = node.radius
        })
      })
      .stop()

    // Run simulation synchronously
    for (let i = 0; i < 300; i++) {
      simulation.tick()
    }

    // Position circles after simulation
    circles
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
  })

  // Add note
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', -35)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .style('font-style', 'italic')
    .text('Displaying last reported value per country within 10-year timeframe')
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', -15)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .style('font-style', 'italic')
    .text('(sparse data coverage in World Bank Data).')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
    <div ref="tooltipRef" class="tooltip"></div>
  </div>
</template>

<style scoped></style>
