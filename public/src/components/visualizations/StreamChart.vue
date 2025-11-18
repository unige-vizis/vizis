<script setup>
import { onMounted, onUnmounted, onBeforeUnmount, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const containerWidth = ref(0)

// Load the data directly via import
import jsonData from '@/assets/data/viz6_stream_mexico_india_timeline.json'
const data = ref(jsonData)

// Update dimensions and redraw chart when container size changes
function updateDimensions() {
  if (!chartRef.value) return
  const container = chartRef.value
  containerWidth.value = container.clientWidth
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

onBeforeUnmount(() => {
  // Clean up tooltip when component is destroyed
  d3.selectAll('.tooltip').remove()
})

function createChart() {
  if (!data.value) return

  // ============================================================
  // TOGGLE: Set to false to use monthly data (original behavior)
  // ============================================================
  const USE_QUARTERLY_DATA = false

  // Helper function to aggregate monthly data into 3-month buckets
  function aggregateToQuarterly(monthlyData) {
    const quarterly = []

    for (let i = 0; i < monthlyData.length; i += 3) {
      const chunk = monthlyData.slice(i, i + 3)
      if (chunk.length === 0) continue

      // Use the date of the first month in the quarter
      const aggregated = { date: chunk[0].date }

      // Sum all numeric fields across the 3 months
      const allKeys = new Set()
      chunk.forEach(month => Object.keys(month).forEach(key => allKeys.add(key)))

      allKeys.forEach(key => {
        if (key === 'date') return
        aggregated[key] = chunk.reduce((sum, month) => sum + (month[key] || 0), 0)
      })

      quarterly.push(aggregated)
    }

    return quarterly
  }

  if (!containerWidth.value) return

  const margin = { top: 65, right: 200, bottom: 50, left: 60 }
  const marginMexico = { top: 65, right: 15, bottom: 50, left: 60 }
  const marginIndia = { top: 65, right: 200, bottom: 50, left: containerWidth.value > 600 ? 15 : 60 }
  let chartWidth = 0
  if( containerWidth.value > 600 ) {
    chartWidth = (containerWidth.value - margin.left - margin.right) / 2
  } else {
    chartWidth = containerWidth.value - margin.left - margin.right
  }
  const chartHeight = 250

  d3.select(chartRef.value).selectAll('*').remove()
  d3.selectAll('.tooltip').remove()

  const container = d3.select(chartRef.value)
    .append('div')
    .attr('class', 'double-chart')

  // Tooltip
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('position', 'fixed')

  const eventColors = {
    'Battles': '#2563EB',
    'Protests & Riots': '#059669',
    'Violence against civilians': '#DC2626',
    'Other': '#9CA3AF'
  }

  const eventCategories = ['Other', ...data.value.metadata.event_categories.filter(c => c !== 'Other')]

  // Apply quarterly aggregation if enabled
  const indiaData = USE_QUARTERLY_DATA ? aggregateToQuarterly(data.value.india) : data.value.india
  const mexicoData = USE_QUARTERLY_DATA ? aggregateToQuarterly(data.value.mexico) : data.value.mexico

  const countries = [
    { name: 'India', data: indiaData },
    { name: 'Mexico', data: mexicoData }
  ]

  const stack = d3.stack()
    .keys(eventCategories)
    .value((d, key) => d[key] || 0)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetWiggle)

  const allSeries = countries.map(country => stack(country.data))

  const globalYMin = d3.min(allSeries, series =>
    d3.min(series, s => d3.min(s, d => d[0]))
  )
  const globalYMax = d3.max(allSeries, series =>
    d3.max(series, s => d3.max(s, d => d[1]))
  )

  countries.forEach((country, index) => {
    const margin = index === 0 ? marginMexico : marginIndia

    const svg = container.append('svg')
      .attr('width', chartWidth + margin.left + margin.right)
      .attr('height', chartHeight + margin.top + margin.bottom)
      .style('overflow', 'visible')

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    svg.append('text')
      .attr('x', margin.left + chartWidth / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .text(country.name)

    const stackData = country.data
    const parseDate = d3.timeParse('%Y-%m')

    const xScale = d3.scaleTime()
      .domain(d3.extent(stackData, d => parseDate(d.date)))
      .range([0, chartWidth])

    const series = allSeries[index]

    const yScale = d3.scaleLinear()
      .domain([globalYMin, globalYMax])
      .range([chartHeight, 0])

    const yearGroups = d3.group(stackData, d => d.date.split('-')[0])
    const years = Array.from(yearGroups.keys()).sort()

    const clipId = `stream-clip-${country.name}-${Math.random().toString(36).substr(2, 9)}`

    const envelopeData = stackData.map((d, i) => {
      const minY = d3.min(series, s => s[i][0])
      const maxY = d3.max(series, s => s[i][1])
      return { date: d.date, minY, maxY }
    })

    const area = d3.area()
      .x(d => xScale(parseDate(d.date)))
      .y0(d => yScale(d.minY))
      .y1(d => yScale(d.maxY))
      .curve(d3.curveBasis)

    g.append('defs')
      .append('clipPath')
      .attr('id', clipId)
      .append('path')
      .attr('d', area(envelopeData))

    //
    // ---------------------------------------------------------
    //  STREAM SEGMENTS (unchanged)
    // ---------------------------------------------------------
    //

    series.forEach(categoryData => {
      const eventType = categoryData.key
      const color = eventColors[eventType] || '#999'

      years.forEach(year => {
        const yearMonths = yearGroups.get(year)
        const startIndex = categoryData.findIndex(d => d.data.date.startsWith(year))
        if (startIndex === -1) return

        const endIndex = categoryData.findIndex((d, i) => i > startIndex && !d.data.date.startsWith(year))
        const lastIndex = endIndex === -1 ? categoryData.length - 1 : endIndex - 1

        const nextData = categoryData[lastIndex + 1]

        // totals
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

        let pathPoints = []

        for (let i = startIndex; i <= lastIndex; i++) {
          const d = categoryData[i]
          pathPoints.push([xScale(parseDate(d.data.date)), yScale(d[1])])
        }
        if (nextData) {
          pathPoints.push([xScale(parseDate(nextData.data.date)), yScale(nextData[1])])
        }

        const bottom = []
        for (let i = startIndex; i <= lastIndex; i++) {
          const d = categoryData[i]
          bottom.push([xScale(parseDate(d.data.date)), yScale(d[0])])
        }
        if (nextData) {
          bottom.push([xScale(parseDate(nextData.data.date)), yScale(nextData[0])])
        }
        bottom.reverse()

        pathPoints = pathPoints.concat(bottom)

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

            tooltip
              .html(`
                <strong style="font-size: 1rem; color: ${color}">${eventType}</strong>
                  <div>Year: ${year}</div>
                  <div>Events: ${totalCount.toLocaleString()} (${percentage}%)</div>
                  <div>Fatalities: ${totalFatalities.toLocaleString()}</div>
                  <div>Avg per event: ${avgFatalityRate}</div>
              `)
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
            tooltip.style('opacity', 0)
          })
      })
    })

    //
    // ---------------------------------------------------------
    //  AXIS + COVID LINE
    // ---------------------------------------------------------
    //

    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.timeFormat('%Y'))
      .ticks(d3.timeYear.every(1))

    g.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxis)
      .style('font-size', '12px')

    if (index === 0 || containerWidth.value <= 600) {
      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -chartHeight / 2)
        .attr('y', -15)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .text('Number of Events')
    }

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

    //
    // ---------------------------------------------------------
    //  GRIDLINES — ON TOP OF COLORS (Manual lines)
    // ---------------------------------------------------------
    //

    years.forEach(year => {
      const yearDate = parseDate(`${year}-01`)
      const xPos = xScale(yearDate)

      g.append('line')
        .attr('x1', xPos)
        .attr('x2', xPos)
        .attr('y1', 0)
        .attr('y2', chartHeight)
        .style('stroke', '#666')
        .style('stroke-width', 1.2)
        .style('opacity', 2.0)
        .style('pointer-events', 'none')
        .attr('clip-path', `url(#${clipId})`)
    })

    if (index === 1) {
      series.forEach(s => {
        const category = s.key
        const lastPoint = s[s.length - 1]
        const yMid = (yScale(lastPoint[0]) + yScale(lastPoint[1])) / 2

        g.append('text')
          .attr('x', chartWidth + 15)
          .attr('y', yMid)
          .attr('text-anchor', 'start')
          .attr('dominant-baseline', 'middle')
          .style('font-size', '13px')
          .style('fill', eventColors[category])
          .text(category)
      })
    }
  })
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart chart-min-width"></div>
  </div>
</template>
