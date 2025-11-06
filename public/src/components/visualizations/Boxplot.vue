<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)
const normalizeByPopulation = ref(false)

// Load the data from data-processing/viz-datasets/viz1_bar_chart_sectors_conflicts.json and extract the array
import data from '../../../../data-processing/viz-datasets/viz2-1_boxplot_fatalities_per_million_inhabitants.json'
const dataset = Array.isArray(data && data.data) ? data.data : []
console.log('Boxplot dataset:', dataset);

// Watch for toggle changes and update chart with transitions
watch(normalizeByPopulation, () => {
  updateChart()
})

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || container.clientWidth * 0.6 // 60% aspect ratio if height not constrained
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
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 20, right: 80, bottom: 60, left: 80 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 400

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(0,0)`)

  // Scale
  const y = d3.scaleLinear()
    .domain([0, d3.max(dataset.map(d => Math.max(d.Primary_Impact, d.Secondary_Impact, d.Tertiary_Impact, d.Tourism_Impact)))])
    .range([height - margin.bottom, margin.top]);

  const x = d3.scaleBand()
    .domain(["Primary_Impact", "Secondary_Impact", "Tertiary_Impact", "Tourism_Impact"])
    .range([margin.left, width - margin.right])
    .padding(0.4);

  svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x))
      .style('font-size', '1rem')

  svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y))
      .style('font-size', '1rem')

  const impacts = ["Primary_Impact", "Secondary_Impact", "Tertiary_Impact", "Tourism_Impact"];

  impacts.forEach((impact, i) => {
    const values = dataset.map(d => d[impact]).sort(d3.ascending);
    const q1 = d3.quantile(values, 0.25);
    const median = d3.quantile(values, 0.5);
    const q3 = d3.quantile(values, 0.75);
    const min = d3.min(values);
    const max = d3.max(values);

    // Draw box
    svg.append("rect")
        .attr("x", x(impact))
        .attr("y", y(q3))
        .attr("height", y(q1) - y(q3))
        .attr("width", x.bandwidth())
        .attr("fill", "steelblue");

    // Median line
    svg.append("line")
        .attr("x1", x(impact))
        .attr("x2", x(impact) + x.bandwidth())
        .attr("y1", y(median))
        .attr("y2", y(median))
        .attr("stroke", "black");
  });
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
