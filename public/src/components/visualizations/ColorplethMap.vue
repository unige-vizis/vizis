<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import data from '@/assets/data/viz7_maps.json'

// Extract array
const dataset = Array.isArray(data?.data) ? data.data : []

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Resize handling
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value

  containerWidth.value = container.clientWidth
  containerHeight.value = container.clientHeight || container.clientWidth * 0.6

  createChart()
}

let resizeObserver
onMounted(() => {
  updateDimensions()
  resizeObserver = new ResizeObserver(updateDimensions)
  resizeObserver.observe(chartRef.value)
})

onUnmounted(() => resizeObserver?.disconnect())

async function createChart() {
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 10, right: 10, bottom: 10, left: 10 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 600

  // Clear previous chart
  d3.select(chartRef.value).selectAll('*').remove()

  // Create svg
  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // ---------------------------
  // Load GeoJSON World Map
  // ---------------------------
  const world = await d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  const countries = topojson.feature(world, world.objects.countries).features

  // ---------------------------
  // Prepare data: map country → value
  // ---------------------------
  const dataByCountry = new Map()
  dataset.forEach(d => {
    if (!d.country) return
    const value = d.primary;
    dataByCountry.set(d.country.toLowerCase(), value)
  })

  // ---------------------------
  // Color scale
  // ---------------------------
  const values = [...dataByCountry.values()]
  const color = d3.scaleSequential()
  .domain([0, d3.max(dataset, d => d.primary)])
  .interpolator(d3.interpolateYlOrBr);

  // ---------------------------
  // Projection
  // ---------------------------
  const projection = d3.geoMercator().fitSize([width, height], {
    type: "FeatureCollection",
    features: countries
  })

  const path = d3.geoPath(projection)

  // ---------------------------
  // Draw countries
  // ---------------------------
  svg.append("g")
    .selectAll("path")
    .data(countries)
    .enter()
    .append("path")
    .attr("d", path)
    .attr("fill", d => {
      const name = d.properties.name?.toLowerCase()
      const v = dataByCountry.get(name)
      if(!v) console.log(name)
      return v ? color(v) : "#eee"
    })
    .attr("stroke", "#555")
    .attr("stroke-width", 0.5)
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
