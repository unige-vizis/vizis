<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Load the data directly via import
import jsonData from '@/assets/data/viz5_waffle_sectors_by_event_type.json'
const data = ref(jsonData)

onMounted(() => {
  createChart()
})

function createChart() {
  if (!data.value) return

  const margin = { top: 60, right: 20, bottom: 80, left: 20 }
  const squareSize = 10
  const squareGap = 2
  const columns = 10
  const rows = 10
  const totalSquares = columns * rows

  const chartWidth = columns * (squareSize + squareGap) - squareGap
  const chartHeight = rows * (squareSize + squareGap) - squareGap

  const gapBetweenCharts = 40

  // All charts in ONE ROW
  const eventTypes = data.value.data
  const chartsPerRow = eventTypes.length

  const totalWidth = chartsPerRow * (chartWidth + gapBetweenCharts) - gapBetweenCharts + margin.left + margin.right
  const totalHeight = chartHeight + margin.top + margin.bottom

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', totalWidth)
    .attr('height', totalHeight)
    .attr('viewBox', `0 0 ${totalWidth} ${totalHeight}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')

  // Color scale for sectors - matching viz2 colors
  const sectorColors = {
    'Primary': '#8B4513',        // Brown (same as viz2)
    'Secondary': '#4682B4',      // Steel Blue (same as viz2)
    'Tertiary': '#9370DB'        // Medium Purple (same as viz2)
  }

  // Tooltip
  const tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.9)')
    .style('color', '#fff')
    .style('padding', '8px 12px')
    .style('border-radius', '4px')
    .style('font-size', '12px')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)

  // Create a waffle chart for each event type (all in one row)
  eventTypes.forEach((eventType, index) => {
    const xOffset = margin.left + index * (chartWidth + gapBetweenCharts)
    const yOffset = margin.top

    const chartGroup = svg.append('g')
      .attr('transform', `translate(${xOffset}, ${yOffset})`)

    // Get primary sector percentage
    const primarySector = eventType.sectors.find(s => s.sector === 'Primary')
    const primaryPct = primarySector ? primarySector.percentage : 0

    // Add title for this waffle chart
    chartGroup.append('text')
      .attr('x', chartWidth / 2)
      .attr('y', -35)
      .attr('text-anchor', 'middle')
      .style('fill', '#c7c7c7')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(eventType.event_type)

    // Add primary sector percentage below title
    chartGroup.append('text')
      .attr('x', chartWidth / 2)
      .attr('y', -18)
      .attr('text-anchor', 'middle')
      .style('fill', sectorColors['Primary'])
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .text(`${primaryPct.toFixed(1)}% Primary`)

    // Generate squares data based on sector percentages
    const squaresData = []
    let currentSquare = 0

    eventType.sectors.forEach(sector => {
      const numSquares = Math.round((sector.percentage / 100) * totalSquares)
      for (let i = 0; i < numSquares; i++) {
        if (currentSquare < totalSquares) {
          squaresData.push({
            id: currentSquare,
            row: Math.floor(currentSquare / columns),
            col: currentSquare % columns,
            sector: sector.sector,
            percentage: sector.percentage,
            eventType: eventType.event_type
          })
          currentSquare++
        }
      }
    })

    // Fill remaining squares if any (due to rounding)
    while (currentSquare < totalSquares) {
      const lastSector = eventType.sectors[eventType.sectors.length - 1]
      squaresData.push({
        id: currentSquare,
        row: Math.floor(currentSquare / columns),
        col: currentSquare % columns,
        sector: lastSector.sector,
        percentage: lastSector.percentage,
        eventType: eventType.event_type
      })
      currentSquare++
    }

    // Draw squares
    chartGroup.selectAll('rect')
      .data(squaresData)
      .enter()
      .append('rect')
      .attr('x', d => d.col * (squareSize + squareGap))
      .attr('y', d => d.row * (squareSize + squareGap))
      .attr('width', squareSize)
      .attr('height', squareSize)
      .attr('fill', d => sectorColors[d.sector])
      .attr('stroke', '#1a1a1a')
      .attr('stroke-width', 0.5)
      .attr('rx', 1)
      .attr('ry', 1)
      .attr('opacity', 0.8)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('opacity', 1)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2)

        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.eventType}</strong><br/>${d.sector}: ${d.percentage.toFixed(1)}%`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('opacity', 0.8)
          .attr('stroke', '#1a1a1a')
          .attr('stroke-width', 0.5)

        tooltip.style('opacity', 0)
      })
  })

  // Add global legend at the bottom
  const legendY = totalHeight - 50
  const legend = svg.append('g')
    .attr('transform', `translate(${totalWidth / 2 - 225}, ${legendY})`)

  const sectors = ['Primary', 'Secondary', 'Tertiary']
  const legendItemWidth = 150

  sectors.forEach((sector, i) => {
    const legendItem = legend.append('g')
      .attr('transform', `translate(${i * legendItemWidth}, 0)`)

    legendItem.append('rect')
      .attr('width', 16)
      .attr('height', 16)
      .attr('fill', sectorColors[sector])
      .attr('opacity', 0.8)
      .attr('rx', 2)
      .attr('ry', 2)

    legendItem.append('text')
      .attr('x', 22)
      .attr('y', 12)
      .text(sector)
      .style('fill', '#c7c7c7')
      .style('font-size', '12px')
  })

  // Add note about data
  svg.append('text')
    .attr('x', totalWidth / 2)
    .attr('y', totalHeight - 10)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '10px')
    .text('Sorted by Primary sector percentage • Each square = 1% • Weighted by event frequency')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2rem 0;
}

.chart {
  width: 100%;
  position: relative;
}

.chart svg {
  display: block;
  margin: 0 auto;
  width: 100%;
  height: auto;
}
</style>
