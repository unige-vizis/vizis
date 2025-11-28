<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import fatalityData from '@/assets/data/viz8_bubble_map_fatalities.json'

// Extract data (all countries with fatalities - 174 countries)
const dataset = Array.isArray(fatalityData?.data) ? fatalityData.data : []

const chartRef = ref(null)
const containerWidth = ref(0)
const containerHeight = ref(0)

// Country name mapping: GeoJSON name -> ACLED data name
const geoToDataName = {
  'united states of america': 'united states',
  'dem. rep. congo': 'democratic republic of congo',
  'burma': 'myanmar',
  'russia': 'russia',
  'ivory coast': 'ivory coast',
  'cote d\'ivoire': 'ivory coast',
  'czech rep.': 'czech republic',
  'bosnia and herz.': 'bosnia and herzegovina',
  'central african rep.': 'central african republic',
  'dominican rep.': 'dominican republic',
  'eq. guinea': 'equatorial guinea',
  'n. korea': 'north korea',
  's. korea': 'south korea',
  's. sudan': 'south sudan',
  'w. sahara': 'western sahara',
  'lao pdr': 'laos',
  'solomon is.': 'solomon islands',
  'falkland is.': 'falkland islands',
  'fr. s. antarctic lands': 'french southern territories'
}

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

onUnmounted(() => {
  resizeObserver?.disconnect()
  d3.select('body').selectAll('.bubble-map-tooltip').remove()
})

async function createChart() {
  if (!containerWidth.value || !containerHeight.value) return

  const margin = { top: 10, right: 10, bottom: 60, left: 10 }
  const width = containerWidth.value - margin.left - margin.right
  const height = 600

  d3.select(chartRef.value).selectAll('*').remove()

  // Create tooltip on body to avoid overflow issues
  d3.select('body').selectAll('.bubble-map-tooltip').remove()
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'bubble-map-tooltip')
    .style('position', 'fixed')
    .style('background', 'rgba(0, 0, 0, 0.85)')
    .style('color', '#fff')
    .style('padding', '10px 14px')
    .style('border-radius', '4px')
    .style('font-size', '0.9rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)
    .style('max-width', '280px')

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height + margin.bottom)

  // Load world map
  const world = await d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  const countries = topojson.feature(world, world.objects.countries).features

  // Projection (full width, shifted up to crop Antarctica at bottom)
  const projection = d3.geoMercator()
    .fitSize([width, height + 200], {
      type: "FeatureCollection",
      features: countries
    })
  // Shift map down to hide Antarctica at bottom
  const currentTranslate = projection.translate()
  projection.translate([currentTranslate[0], currentTranslate[1] + 100])

  const path = d3.geoPath(projection)

  // Draw base map (light gray)
  svg.append("g")
    .selectAll("path")
    .data(countries)
    .enter()
    .append("path")
    .attr("d", path)
    .attr("fill", "#e8e8e8")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 0.5)

  // Sqrt radius scale for better visual proportion (area scales with value)
  const maxFatalities = d3.max(dataset, d => d.total_fatalities)
  const radiusScale = d3.scaleSqrt()
    .domain([0, maxFatalities])
    .range([1.5, 25])

  // Build a lookup of country names to centroids from GeoJSON
  const countryCentroids = {}
  countries.forEach(feature => {
    const geoName = feature.properties.name?.toLowerCase() || ''
    // Calculate centroid from the feature geometry
    const centroid = d3.geoCentroid(feature)
    if (centroid && !isNaN(centroid[0]) && !isNaN(centroid[1])) {
      countryCentroids[geoName] = centroid
      // Also store by mapped name if applicable
      if (geoToDataName[geoName]) {
        countryCentroids[geoToDataName[geoName]] = centroid
      }
    }
  })

  // Prepare bubble data with computed centroids
  const bubbleData = dataset
    .filter(d => d.total_fatalities > 0)
    .map(d => {
      const countryKey = d.country.toLowerCase()
      // Try direct match first, then check reverse mapping
      let centroid = countryCentroids[countryKey]

      // If not found, search for approximate match
      if (!centroid) {
        for (const [geoName, coords] of Object.entries(countryCentroids)) {
          if (geoName.includes(countryKey) || countryKey.includes(geoName)) {
            centroid = coords
            break
          }
        }
      }

      if (!centroid) return null
      const projected = projection(centroid)
      if (!projected || isNaN(projected[0])) return null
      return {
        ...d,
        x: projected[0],
        y: projected[1]
      }
    })
    .filter(d => d !== null)
    .sort((a, b) => b.total_fatalities - a.total_fatalities)

  // Draw bubbles
  svg.append("g")
    .selectAll("circle")
    .data(bubbleData)
    .enter()
    .append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", d => radiusScale(d.total_fatalities))
    .attr("fill", "rgba(220, 38, 38, 0.5)")
    .attr("stroke", "#991b1b")
    .attr("stroke-width", 0.5)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      d3.select(this)
        .attr("fill", "rgba(220, 38, 38, 0.85)")
        .attr("stroke-width", 2)
        .raise() // Bring to front

      tooltip
        .style('opacity', 1)
        .html(`
          <strong>${d.country}</strong><br/>
          <strong>Fatalities:</strong> ${d.total_fatalities.toLocaleString()} · <strong>Events:</strong> ${d.event_count.toLocaleString()}<br/>
          <hr style="border:0;border-top:1px solid #444;margin:6px 0"/>
          <table style="font-size:0.75rem;border-collapse:collapse;width:100%">
            <tr><td>Battles</td><td style="text-align:right">${(d.battles || 0).toLocaleString()}</td><td style="text-align:right;color:#f87171;padding-left:8px">${(d.battles_fatal || 0).toLocaleString()}</td></tr>
            <tr><td>Explosions</td><td style="text-align:right">${(d.explosions || 0).toLocaleString()}</td><td style="text-align:right;color:#f87171;padding-left:8px">${(d.explosions_fatal || 0).toLocaleString()}</td></tr>
            <tr><td>Violence</td><td style="text-align:right">${(d.violence_civilians || 0).toLocaleString()}</td><td style="text-align:right;color:#f87171;padding-left:8px">${(d.violence_civilians_fatal || 0).toLocaleString()}</td></tr>
            <tr><td>Riots</td><td style="text-align:right">${(d.riots || 0).toLocaleString()}</td><td style="text-align:right;color:#f87171;padding-left:8px">${(d.riots_fatal || 0).toLocaleString()}</td></tr>
            <tr><td>Protests</td><td style="text-align:right">${(d.protests || 0).toLocaleString()}</td><td style="text-align:right;color:#f87171;padding-left:8px">${(d.protests_fatal || 0).toLocaleString()}</td></tr>
          </table>
          <div style="font-size:0.65rem;color:#888;margin-top:4px">events · <span style="color:#f87171">fatalities</span></div>
        `)
    })
    .on("mousemove", function(event) {
      tooltip
        .style('left', (event.clientX + 15) + 'px')
        .style('top', (event.clientY - 10) + 'px')
    })
    .on("mouseout", function() {
      d3.select(this)
        .attr("fill", "rgba(220, 38, 38, 0.5)")
        .attr("stroke-width", 0.5)
      tooltip.style('opacity', 0)
    })

  // Legend - Vertical on right side
  const legendX = width - 55
  const legendY = 60
  const legendValues = [1000, 10000, 50000, 200000]

  // Legend title
  svg.append("text")
    .attr("x", legendX + 25)
    .attr("y", legendY - 12)
    .attr("text-anchor", "middle")
    .style("font-size", "0.7rem")
    .style("fill", "#333")
    .style("font-weight", "500")
    .text("Fatalities")

  const legendGroup = svg.append("g")
    .attr("transform", `translate(${legendX}, ${legendY})`)

  // Calculate cumulative Y positions based on bubble sizes
  let cumulativeY = 0
  legendValues.forEach((val, i) => {
    const r = radiusScale(val)
    const prevR = i > 0 ? radiusScale(legendValues[i - 1]) : 0

    // Add spacing: previous radius + gap + current radius
    if (i > 0) {
      cumulativeY += prevR + 20 + r
    } else {
      cumulativeY = r
    }

    legendGroup.append("circle")
      .attr("cx", 25)
      .attr("cy", cumulativeY)
      .attr("r", r)
      .attr("fill", "rgba(220, 38, 38, 0.5)")
      .attr("stroke", "#991b1b")
      .attr("stroke-width", 0.5)

    legendGroup.append("text")
      .attr("x", 25)
      .attr("y", cumulativeY + r + 12)
      .attr("text-anchor", "middle")
      .style("font-size", "0.6rem")
      .style("fill", "#555")
      .text(val >= 1000 ? (val / 1000) + "K" : val)
  })
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>

<style scoped>
.chart {
  position: relative;
}
</style>
