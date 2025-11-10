<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)
const normalizeByPopulation = ref(false)

// Load the data and extract the array
import data from '@/assets/data/viz1_bar_chart_sectors_conflicts.json'
const dataset = Array.isArray(data && data.data) ? data.data : []

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

  const margin = { top: 20, right: 20, bottom: 60, left: 80 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 400
  const subgroups = ['Primary_%', 'Secondary_%', 'Tertiary_%', 'Tourism_%']
  // human-friendly labels for the x axis
  const xLabels = {
    'Primary_%': 'Primary',
    'Secondary_%': 'Secondary',
    'Tertiary_%': 'Tertiary',
    'Tourism_%': 'Tourism'
  }

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(0,0)`)

  // Scale
  // // compute numeric max across subgroups, coercing values to numbers and ignoring NaN
  const maxVal = d3.max(dataset, d => d3.max(subgroups, key => {
    const v = +d[key];
    return isNaN(v) ? undefined : v;
  })) || 1;
  const y = d3.scaleLinear()
    .domain([0, Math.ceil(maxVal / 10) * 10])
    .range([height - margin.bottom, margin.top]);

  // increase padding to give more horizontal space between items
  const x = d3.scaleBand()
    .domain(subgroups)
    .range([margin.left, width - margin.right])
    .padding(0.7);

  svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x)
        .tickFormat(d => xLabels[d] || d)
        .tickSizeOuter(0)
        .tickPadding(12)
      )
      .style('font-size', '1rem')
      .call(g => g.selectAll('text')
        .attr('transform', null)
        .style('text-anchor', 'middle')
        .attr('dy', '0.75em')
      )

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickFormat(d => d + '%'))
    .style('font-size', '1rem')


  // numeric formatter for labels
  const fmt = d3.format('.2f');

  subgroups.forEach((sector, i) => {
    // Coerce to numbers and filter out non-numeric values before computing quantiles
    const values = dataset
      .map(d => +d[sector])
      .filter(v => !isNaN(v))
      .sort(d3.ascending);

    // Skip drawing if no numeric data for this sector
    if (values.length === 0) return;

    const q1 = d3.quantile(values, 0.25);
    const median = d3.quantile(values, 0.5);
    const q3 = d3.quantile(values, 0.75);
    const min = d3.min(values);
    const max = d3.max(values);

    const center = x(sector) + x.bandwidth() / 2;

    // Draw box (guard against undefined quantiles)
    svg.append('rect')
      .attr('x', x(sector))
      .attr('y', y(q3))
      .attr('height', Math.abs(y(q1) - y(q3)))
      .attr('width', x.bandwidth())
      .attr('fill', '#8d6aff')

    // Median line
    svg.append('line')
      .attr('x1', x(sector))
      .attr('x2', x(sector) + x.bandwidth())
      .attr('y1', y(median))
      .attr('y2', y(median))
      .attr('stroke', 'black');

    // Whisker to max: vertical line and cap + label
    if (q3 != null && max != null) {
      svg.append('line')
        .attr('x1', center)
        .attr('x2', center)
        .attr('y1', y(q3))
        .attr('y2', y(max))
        .attr('stroke', 'black');

      svg.append('line')
        .attr('x1', center - x.bandwidth() * 0.25)
        .attr('x2', center + x.bandwidth() * 0.25)
        .attr('y1', y(max))
        .attr('y2', y(max))
        .attr('stroke', 'black');

      svg.append('text')
        .text(fmt(max) + "%")
        .attr('x', center + x.bandwidth() * 0.55)
        .attr('y', y(max))
        .attr('dy', '0.35em')
        .style('font-size', '1rem')
        .style('fill', '#333');
    }

    // Whisker to min: vertical line and cap + label
    if (q1 != null && min != null) {
      svg.append('line')
        .attr('x1', center)
        .attr('x2', center)
        .attr('y1', y(q1))
        .attr('y2', y(min))
        .attr('stroke', 'black');

      svg.append('line')
        .attr('x1', center - x.bandwidth() * 0.25)
        .attr('x2', center + x.bandwidth() * 0.25)
        .attr('y1', y(min))
        .attr('y2', y(min))
        .attr('stroke', 'black');

      svg.append('text')
        .text(fmt(min))
        .attr('x', center + x.bandwidth() * 0.55)
        .attr('y', y(min))
        .attr('dy', (min === 0) ? '-.2em' : '0.35em')
        .style('font-size', '1rem')
        .style('fill', '#333');
    }
  });
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
