<script setup>
import { onMounted, ref } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)

// Placeholder data - representing scale of religion-related events
// Each square represents a certain number of events (e.g., 100 events)
const totalSquares = 100
const religionRelatedPercentage = 35 // 35% of all conflict events are religion-related

onMounted(() => {
  createChart()
})

function createChart() {
  const margin = { top: 20, right: 30, bottom: 80, left: 30 }
  const squareSize = 25
  const squareGap = 3
  const columns = 10
  const rows = Math.ceil(totalSquares / columns)

  const width = columns * (squareSize + squareGap) - squareGap
  const height = rows * (squareSize + squareGap) - squareGap

  // Clear any existing chart
  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Generate data for squares
  const data = []
  for (let i = 0; i < totalSquares; i++) {
    data.push({
      id: i,
      row: Math.floor(i / columns),
      col: i % columns,
      isReligionRelated: i < (totalSquares * religionRelatedPercentage / 100)
    })
  }

  // Shuffle to distribute religion-related squares more naturally
  const shuffledData = d3.shuffle(data)

  // Color scale
  const getColor = (d) => d.isReligionRelated ? '#c6c7ff' : '#3a3a3a'

  // Tooltip
  const tooltip = d3.select(chartRef.value)
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', '#fff')
    .style('padding', '8px 12px')
    .style('border-radius', '4px')
    .style('font-size', '1rem')
    .style('pointer-events', 'none')
    .style('opacity', 0)

  // Add squares
  svg.selectAll('rect')
    .data(shuffledData)
    .enter()
    .append('rect')
    .attr('x', d => d.col * (squareSize + squareGap))
    .attr('y', d => d.row * (squareSize + squareGap))
    .attr('width', squareSize)
    .attr('height', squareSize)
    .attr('fill', d => getColor(d))
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 1)
    .attr('rx', 2)
    .attr('ry', 2)
    .attr('opacity', 0.8)
    .on('mouseover', function(event, d) {
      d3.select(this)
        .attr('opacity', 1)
        .attr('stroke', d.isReligionRelated ? '#fff' : '#666')
        .attr('stroke-width', 2)

      const label = d.isReligionRelated ? 'Religion-related event' : 'Other conflict event'
      tooltip
        .style('opacity', 1)
        .html(label)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function(event, d) {
      d3.select(this)
        .attr('opacity', 0.8)
        .attr('stroke', '#1a1a1a')
        .attr('stroke-width', 1)

      tooltip.style('opacity', 0)
    })

  // Add legend
  const legend = svg.append('g')
    .attr('transform', `translate(0, ${height + 30})`)

  const legendData = [
    { label: 'Religion-related events', color: '#c6c7ff', percentage: religionRelatedPercentage },
    { label: 'Other conflict events', color: '#3a3a3a', percentage: 100 - religionRelatedPercentage }
  ]

  const legendItems = legend.selectAll('.legend-item')
    .data(legendData)
    .enter()
    .append('g')
    .attr('class', 'legend-item')
    .attr('transform', (d, i) => `translate(${i * 180}, 0)`)

  legendItems.append('rect')
    .attr('width', 20)
    .attr('height', 20)
    .attr('fill', d => d.color)
    .attr('opacity', 0.8)
    .attr('rx', 2)
    .attr('ry', 2)

  legendItems.append('text')
    .attr('x', 28)
    .attr('y', 15)
    .text(d => `${d.label} (${d.percentage}%)`)
    .style('font-size', '1rem')

  // Add explanatory text
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height + 60)
    .attr('text-anchor', 'middle')
    .style('fill', '#999')
    .style('font-size', '1rem')
    .text('Each square represents 1% of all conflict events globally')
}
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart"></div>
    <p class="data-note">
      Note: This visualization uses placeholder data. Real data from ACLED will be integrated in the next iteration.
    </p>
  </div>
</template>
