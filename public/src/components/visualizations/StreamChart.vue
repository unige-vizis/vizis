<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Load the data directly via import
import jsonData from '@/assets/data/viz6_stream_mexico_india_timeline.json'
const data = ref(jsonData)

onMounted(() => {
  createChart()
})

onBeforeUnmount(() => {
  // Clean up tooltip when component is destroyed
  d3.selectAll('.stream-tooltip').remove()
})

function createChart() {
  if (!data.value) return

  // Chart dimensions - made thinner vertically and narrower to fit in container
  // Different margins for each chart to minimize gap between them
  const marginMexico = { top: 65, right: 15, bottom: 50, left: 50 }  // Increased top margin for spacing
  const marginIndia = { top: 65, right: 120, bottom: 50, left: 15 }  // Increased top margin for spacing
  const chartWidth = 380  // Reduced to fit both charts side-by-side
  const chartHeight = 250
  const gapBetweenCharts = 15  // Small gap between charts

  // Clear any existing chart and tooltips
  d3.select(chartRef.value).selectAll('*').remove()
  d3.selectAll('.stream-tooltip').remove()

  const container = d3.select(chartRef.value)
    .append('div')
    .style('display', 'flex')
    .style('justify-content', 'center')
    .style('align-items', 'flex-start')
    .style('gap', `${gapBetweenCharts}px`)
    .style('flex-wrap', 'nowrap')  // Changed from 'wrap' to 'nowrap' to keep side-by-side

  // Create single tooltip for both charts - append to body for proper positioning
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'stream-tooltip')
    .style('position', 'fixed')
    .style('background', 'rgba(0, 0, 0, 0.95)')
    .style('color', '#fff')
    .style('padding', '6px 10px')
    .style('border-radius', '4px')
    .style('font-size', '0.85rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 10000)
    .style('box-shadow', '0 4px 6px rgba(0,0,0,0.3)')
    .style('max-width', '280px')
    .style('line-height', '1.3')

  // Color scale for event types
  const eventColors = {
    'Battles': '#2563EB',                        // Blue
    'Protests & Riots': '#059669',               // Green
    'Violence against civilians': '#DC2626',     // Red
    'Other': '#9CA3AF'                           // Grey (combined Explosions/Remote violence and Strategic developments)
  }

  // Get event categories from metadata and reorder to put "Other" first (bottom of stream)
  const eventCategories = ['Other', ...data.value.metadata.event_categories.filter(c => c !== 'Other')]

  // Create charts for both countries
  const countries = [
    { name: 'India', data: data.value.india },
    { name: 'Mexico', data: data.value.mexico }
  ]

  // Calculate global min/max across BOTH countries for consistent scaling
  const stack = d3.stack()
    .keys(eventCategories)
    .value((d, key) => d[key] || 0)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetWiggle)

  // Get stacked data for both countries
  const allSeries = countries.map(country => stack(country.data))

  // Find global min and max across both countries
  const globalYMin = d3.min(allSeries, series =>
    d3.min(series, s => d3.min(s, d => d[0]))
  )
  const globalYMax = d3.max(allSeries, series =>
    d3.max(series, s => d3.max(s, d => d[1]))
  )

  countries.forEach((country, index) => {
    // Use appropriate margin - first chart (India) gets left-side margins, second (Mexico) gets right-side margins
    const margin = index === 0 ? marginMexico : marginIndia

    // Create SVG for each country
    const svg = container.append('svg')
      .attr('width', chartWidth + margin.left + margin.right)
      .attr('height', chartHeight + margin.top + margin.bottom)
      .style('overflow', 'visible')

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Title - centered over the plot area only (not including legend)
    svg.append('text')
      .attr('x', margin.left + chartWidth / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .text(country.name)

    // Prepare data for stack
    const stackData = country.data

    // Parse dates from "YYYY-MM" format
    const parseDate = d3.timeParse('%Y-%m')
    const formatDate = d3.timeFormat('%Y-%m')

    // Create scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(stackData, d => parseDate(d.date)))
      .range([0, chartWidth])

    // Use pre-calculated stacked data for this country
    const series = allSeries[index]

    // Y scale - using GLOBAL min/max so both charts have proportional scaling
    const yScale = d3.scaleLinear()
      .domain([globalYMin, globalYMax])
      .range([chartHeight, 0])

    // Group data by year for hoverable segments
    const yearGroups = d3.group(stackData, d => d.date.split('-')[0])
    const years = Array.from(yearGroups.keys()).sort()

    // Create a clip path for the stream bounds - encompass entire stream
    const clipId = `stream-clip-${country.name}-${Math.random().toString(36).substr(2, 9)}`

    // Find the envelope of the entire stream (min y0 and max y1 at each point)
    const envelopeData = stackData.map((d, i) => {
      const minY = d3.min(series, s => s[i][0])
      const maxY = d3.max(series, s => s[i][1])
      return {
        date: d.date,
        minY: minY,
        maxY: maxY
      }
    })

    const area = d3.area()
      .x(d => xScale(parseDate(d.date)))
      .y0(d => yScale(d.minY))
      .y1(d => yScale(d.maxY))
      .curve(d3.curveMonotoneX)

    g.append('defs')
      .append('clipPath')
      .attr('id', clipId)
      .append('path')
      .attr('d', area(envelopeData))

    // Draw individual year segments for each category
    // Each year is independently hoverable
    series.forEach((categoryData) => {
      const eventType = categoryData.key
      const color = eventColors[eventType] || '#999'

      // Create a segment for each year
      years.forEach((year, yearIndex) => {
        // Get all monthly data points for this year
        const yearMonths = yearGroups.get(year)

        // Find indices in the series data
        const startIndex = categoryData.findIndex(d => d.data.date.startsWith(year))
        if (startIndex === -1) return

        const endIndex = categoryData.findIndex((d, i) => i > startIndex && !d.data.date.startsWith(year))
        const lastIndex = endIndex === -1 ? categoryData.length - 1 : endIndex - 1

        // Get start and end points for this year
        const startData = categoryData[startIndex]
        const endData = categoryData[lastIndex]

        // For the last point, we need to extend to the next data point if it exists
        const nextData = categoryData[lastIndex + 1]

        // Calculate aggregate values for the entire year
        let totalCount = 0
        let totalFatalities = 0
        let totalAllEvents = 0
        let totalAllFatalities = 0

        yearMonths.forEach(monthData => {
          totalCount += monthData[eventType] || 0
          totalFatalities += monthData[`${eventType}_fatalities`] || 0
          totalAllEvents += monthData['_total_events'] || 0
          totalAllFatalities += monthData['_total_fatalities'] || 0
        })

        const avgFatalityRate = totalCount > 0 ? (totalFatalities / totalCount).toFixed(2) : '0.00'
        const percentage = totalAllEvents > 0 ? ((totalCount / totalAllEvents) * 100).toFixed(1) : '0.0'

        // Create path points for the year segment
        const x0 = xScale(parseDate(startData.data.date))
        const x1 = nextData ? xScale(parseDate(nextData.data.date)) : xScale(parseDate(endData.data.date))

        // Build path going through all months in the year
        let pathPoints = []

        // Top edge (y1 values) - forward through the year
        for (let i = startIndex; i <= lastIndex; i++) {
          const d = categoryData[i]
          pathPoints.push([xScale(parseDate(d.data.date)), yScale(d[1])])
        }
        if (nextData) {
          pathPoints.push([xScale(parseDate(nextData.data.date)), yScale(nextData[1])])
        }

        // Bottom edge (y0 values) - backward through the year
        const bottomPoints = []
        for (let i = startIndex; i <= lastIndex; i++) {
          const d = categoryData[i]
          bottomPoints.push([xScale(parseDate(d.data.date)), yScale(d[0])])
        }
        if (nextData) {
          bottomPoints.push([xScale(parseDate(nextData.data.date)), yScale(nextData[0])])
        }
        bottomPoints.reverse()
        pathPoints = pathPoints.concat(bottomPoints)

        // Build the path string
        let pathString = `M ${pathPoints[0][0]},${pathPoints[0][1]}`
        for (let i = 1; i < pathPoints.length; i++) {
          pathString += ` L ${pathPoints[i][0]},${pathPoints[i][1]}`
        }
        pathString += ' Z'

        g.append('path')
          .attr('class', 'stream-segment')
          .attr('d', pathString)
          .style('fill', color)
          .style('opacity', 0.8)
          .style('cursor', 'pointer')
          .on('mouseover', function(event) {
            d3.select(this)
              .style('opacity', 1)
              .style('stroke', '#000')
              .style('stroke-width', 1.5)

            tooltip
              .html(`
                <strong style="font-size: 0.95rem; color: ${color}">${eventType}</strong>
                <div style="margin-top: 2px; font-size: 0.8rem;">
                  <div><strong>Year:</strong> ${year}</div>
                  <div><strong>Events:</strong> ${totalCount.toLocaleString()} (${percentage}%)</div>
                  <div><strong>Fatalities:</strong> ${totalFatalities.toLocaleString()}</div>
                  <div><strong>Avg per event:</strong> ${avgFatalityRate}</div>
                </div>
              `)
              .style('left', (event.clientX + 10) + 'px')
              .style('top', (event.clientY - 10) + 'px')
              .style('opacity', 1)
          })
          .on('mousemove', function(event) {
            tooltip
              .style('left', (event.clientX + 10) + 'px')
              .style('top', (event.clientY - 10) + 'px')
          })
          .on('mouseout', function() {
            d3.select(this)
              .style('opacity', 0.8)
              .style('stroke', 'none')

            tooltip.style('opacity', 0)
          })
      })
    })

    // Add vertical grid lines for years (clipped to stream bounds)
    const xGrid = d3.axisBottom(xScale)
      .tickFormat('')
      .tickSize(-chartHeight)
      .ticks(d3.timeYear.every(1))

    g.append('g')
      .attr('class', 'x-grid')
      .attr('transform', `translate(0,${chartHeight})`)
      .attr('clip-path', `url(#${clipId})`)
      .call(xGrid)
      .selectAll('line')
      .style('stroke', '#fff')
      .style('stroke-width', 1.5)
      .style('opacity', 0.7)
      .style('pointer-events', 'none')

    // Remove the domain line from the grid
    g.select('.x-grid .domain').remove()

    // X-axis
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.timeFormat('%Y'))
      .ticks(d3.timeYear.every(1))

    g.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxis)
      .style('font-size', '12px')

    // Y-axis label (only for left chart - India)
    if (index === 0) {
      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -chartHeight / 2)
        .attr('y', -45)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .text('Number of Events')
    }

    // COVID-19 pandemic declaration reference line (March 11, 2020)
    const covidDate = parseDate('2020-03')
    const covidX = xScale(covidDate)

    g.append('line')
      .attr('x1', covidX)
      .attr('x2', covidX)
      .attr('y1', 0)
      .attr('y2', chartHeight)
      .style('stroke', '#000')
      .style('stroke-width', 1)
      .style('stroke-dasharray', '4,4')
      .style('opacity', 0.5)

    g.append('text')
      .attr('x', covidX + 5)
      .attr('y', 10)
      .attr('text-anchor', 'start')
      .style('font-size', '10px')
      .style('fill', '#000')
      .style('font-weight', '600')
      .text('COVID-19 Pandemic')

    g.append('text')
      .attr('x', covidX + 5)
      .attr('y', 22)
      .attr('text-anchor', 'start')
      .style('font-size', '9px')
      .style('fill', '#666')
      .text('Mar 11, 2020')

    // Add inline labels on the right side for Mexico chart only (second chart)
    if (index === 1) {
      series.forEach((s, i) => {
        const category = s.key
        const lastPoint = s[s.length - 1]

        // Calculate the middle y-position of this stream segment at the end
        const yMid = (yScale(lastPoint[0]) + yScale(lastPoint[1])) / 2

        g.append('text')
          .attr('x', chartWidth + 15)
          .attr('y', yMid)
          .attr('text-anchor', 'start')
          .attr('dominant-baseline', 'middle')
          .style('font-size', '13px')
          .style('fill', eventColors[category])
          .style('font-weight', 'normal')
          .text(category)
      })
    }
  })
}
</script>

<template>
  <div ref="chartRef" style="position: relative; width: 100%; margin: 0.5rem 0;"></div>
</template>

<style scoped>
/* Add any specific styles if needed */
</style>
