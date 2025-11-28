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

// Helper to normalize and lookup country name
function getDataForCountry(geoName) {
  if (!geoName) return null
  const lowerName = geoName.toLowerCase()
  const mappedName = lowerName
  return dataset.find(d => d.country?.toLowerCase() === mappedName)
}

async function createChart() {
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 10, right: 10, bottom: 60, left: 10 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 600

  // Clear previous chart
  d3.select(chartRef.value).selectAll('*').remove()

  // Create tooltip
  const tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.85)')
    .style('color', '#fff')
    .style('padding', '10px 14px')
    .style('border-radius', '4px')
    .style('font-size', '0.9rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)
    .style('max-width', '250px')

  // Create svg
  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height + margin.bottom)

  // ---------------------------
  // Load GeoJSON World Map
  // ---------------------------
  const world = await d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  const countries = topojson.feature(world, world.objects.countries).features

  // ---------------------------
  // Color scale
  // ---------------------------
  const maxPrimary = d3.max(dataset, d => d.primary) || 75
  const color = d3.scaleSequential()
    .domain([0, maxPrimary])
    .interpolator(d3.interpolateYlOrBr)

  // ---------------------------
  // Projection (full width, shifted up to crop Antarctica at bottom)
  // ---------------------------
  const projection = d3.geoMercator()
    .fitSize([width, height + 200], {
      type: "FeatureCollection",
      features: countries
    })
  // Shift map down to hide Antarctica at bottom
  const currentTranslate = projection.translate()
  projection.translate([currentTranslate[0], currentTranslate[1] + 100])

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
      const countryData = getDataForCountry(d.properties.name)
      return countryData ? color(countryData.primary) : "#ddd"
    })
    .attr("stroke", "#555")
    .attr("stroke-width", 0.5)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      const countryData = getDataForCountry(d.properties.name)
      d3.select(this).attr("stroke", "#000").attr("stroke-width", 1.5)

      if (countryData) {
        tooltip
          .style('opacity', 1)
          .html(`
            <strong>${countryData.country}</strong><br/>
            Primary Sector: <strong>${countryData.primary.toFixed(1)}%</strong><br/>
            GDP per capita: <strong>$${countryData.gdp_per_capita.toLocaleString(undefined, {maximumFractionDigits: 0})}</strong>
          `)
      } else {
        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.properties.name}</strong><br/><em>No data available</em>`)
      }
    })
    .on("mousemove", function(event) {
      const containerRect = chartRef.value.getBoundingClientRect()
      tooltip
        .style('left', (event.clientX - containerRect.left + 15) + 'px')
        .style('top', (event.clientY - containerRect.top - 10) + 'px')
    })
    .on("mouseout", function() {
      d3.select(this).attr("stroke", "#555").attr("stroke-width", 0.5)
      tooltip.style('opacity', 0)
    })

  // ---------------------------
  // Legend
  // ---------------------------
  const legendWidth = 300
  const legendHeight = 12
  const legendX = (width - legendWidth) / 2
  const legendY = height + 20

  // Create gradient
  const defs = svg.append("defs")
  const gradient = defs.append("linearGradient")
    .attr("id", "colorpleth-legend-gradient")
    .attr("x1", "0%")
    .attr("x2", "100%")

  // Add color stops
  const numStops = 10
  for (let i = 0; i <= numStops; i++) {
    gradient.append("stop")
      .attr("offset", `${(i / numStops) * 100}%`)
      .attr("stop-color", color((i / numStops) * maxPrimary))
  }

  // Legend rectangle
  svg.append("rect")
    .attr("x", legendX)
    .attr("y", legendY)
    .attr("width", legendWidth)
    .attr("height", legendHeight)
    .style("fill", "url(#colorpleth-legend-gradient)")
    .attr("stroke", "#555")
    .attr("stroke-width", 0.5)

  // Legend axis
  const legendScale = d3.scaleLinear()
    .domain([0, maxPrimary])
    .range([0, legendWidth])

  const legendAxis = d3.axisBottom(legendScale)
    .ticks(5)
    .tickFormat(d => d + "%")

  svg.append("g")
    .attr("transform", `translate(${legendX}, ${legendY + legendHeight})`)
    .call(legendAxis)
    .selectAll("text")
    .style("font-size", "0.75rem")

  // Legend title
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", legendY - 6)
    .attr("text-anchor", "middle")
    .style("font-size", "0.85rem")
    .style("fill", "#333")
    .text("Primary Sector as % of GDP")
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width" style="position: relative;"></div>
  </div>
</template>
