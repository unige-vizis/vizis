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

  const margin = { top: 70, right: 20, bottom: 90, left: 20 }
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

  const contDiv = d3.select(chartRef.value)
    .append('div')
    .attr('width', totalWidth)
    .attr('height', totalHeight)
    .attr('viewBox', `0 0 ${totalWidth} ${totalHeight}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('margin-bottom', '2rem')

    const chartDiv = contDiv.append('div')
    .attr('width', totalWidth)
    .attr('height', totalHeight)
    .style('display', "flex")
    .style('flex-wrap', "wrap")
    .style('justify-content', "center")

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
    .style('font-size', '1rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', 1000)

  // Create a waffle chart for each event type (all in one row)
  eventTypes.forEach((eventType, index) => {
    const xOffset = 0
    const yOffset = margin.top

    const svg = chartDiv.append('svg')
      .attr('height', chartHeight + margin.bottom)
      .style('flex', "0")
      .style('min-width', "120px")

    const chartGroup = svg.append('g')
      .attr('transform', `translate(${xOffset}, ${yOffset})`)

    // Get primary sector percentage
    const primarySector = eventType.sectors.find(s => s.sector === 'Primary')
    const primaryPct = primarySector ? primarySector.percentage : 0

    // Add title for this waffle chart
    const titleText = chartGroup.append('text')
      .attr('x', chartWidth / 2)
      .attr('y', -55)
      .attr('text-anchor', 'middle')
      .style('font-size', '0.8rem')
      .style('font-weight', '700')

    const text = eventType.event_type;

    // Measure text width (approximate)
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 0.8rem sans-serif';
    const textWidth = ctx.measureText(text).width;

    if (textWidth > (chartWidth / 2)) {
      // Split text into words
      const words = text.split(' ');
      const mid = Math.ceil(words.length / 2);

      // First line
      titleText.append('tspan')
        .attr('x', chartWidth / 2)
        .attr('dy', 0)
        .text(words.slice(0, mid).join(' '))
        .style('font-size', '0.8rem')
        .style('font-weight', '700');

      // Second line
      titleText.append('tspan')
        .attr('x', chartWidth / 2)
        .attr('dy', '1em')
        .text(words.slice(mid).join(' '))
        .style('font-size', '0.8rem')
        .style('font-weight', '700');
    } else {
      // Single line
      titleText.text(text);
    }

    // Add primary sector percentage below title
    chartGroup.append('text')
      .attr('x', chartWidth / 2)
      .attr('y', -18)
      .attr('text-anchor', 'middle')
      .style('fill', sectorColors['Primary'])
      .style('font-size', '1rem')
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
  const legendItemWidth = 120
  const contLegend = contDiv.append('div')
  .style('margin-top', "0")
  .style('display', "flex")
  .style('justify-content', "center")

  const legend = contLegend.append('svg')
    .attr('transform', `translate(0, 0)`)
    .style('margin', `0`)
    .attr('width', `${legendItemWidth * 3}`)
    .style('height', "2rem")

  const sectors = ['Primary', 'Secondary', 'Tertiary']

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
      .style('font-size', '1rem')
  })

  // Add note about data
  contDiv.append('div')
    .attr('x', totalWidth / 2)
    .attr('y', totalHeight - 10)
    .attr('text-anchor', 'middle')
    .style('font-size', '1rem')
    .style('margin','0 auto')
    .style('width','fit-content')
    .text('Sorted by Primary sector percentage • Each square = 1% • Weighted by event frequency')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>
