<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import sankeyData from '../../assets/data/viz10_actor_sankey.json'

const svgContainer = ref(null)

// Fatality color scale (matching Sankey: Yellow-Orange-Red)
const getFatalityColor = (fatalities) => {
  if (fatalities === 0) return '#fee8c8'
  const maxLogFatalities = Math.log10(100000)
  const logValue = Math.log10(fatalities + 1)
  const normalized = logValue / maxLogFatalities
  const scaled = Math.pow(normalized, 2.5) * 0.75 + 0.1
  return d3.interpolateYlOrRd(scaled)
}

const buildNetwork = () => {
  // Step 1: Compute top-10 rebel groups by event count
  const rebelCounts = new Map()
  sankeyData.flows.forEach(entry => {
    if (entry.actor && entry.actor_type === 'Rebel group') {
      const prev = rebelCounts.get(entry.actor) || 0
      rebelCounts.set(entry.actor, prev + (entry.events || 0))
    }
  })

  const top10rebels = Array.from(rebelCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(d => d[0])

  const top10set = new Set(top10rebels)

  // Step 2: Build network data
  // Nodes: rebel groups + countries
  // Edges: rebel group -> country with fatality data
  const rebelNodes = top10rebels.map(rebel => ({
    id: rebel,
    type: 'rebel',
    totalEvents: rebelCounts.get(rebel),
    label: rebel.split(':')[0]
  }))

  const countrySet = new Set()
  const links = []
  const linkMap = new Map()

  sankeyData.flows.forEach(entry => {
    if (!entry.actor || !top10set.has(entry.actor)) return

    const rebel = entry.actor
    const country = entry.country
    const fatalities = entry.fatalities || 0
    const events = entry.events || 0

    countrySet.add(country)

    const linkKey = `${rebel}|${country}`
    if (!linkMap.has(linkKey)) {
      linkMap.set(linkKey, {
        source: rebel,
        target: country,
        fatalities: 0,
        events: 0
      })
    }

    const link = linkMap.get(linkKey)
    link.fatalities += fatalities
    link.events += events
  })

  const countryNodes = Array.from(countrySet).map(country => ({
    id: country,
    type: 'country',
    label: country
  }))

  const allNodes = [...rebelNodes, ...countryNodes]
  const edges = Array.from(linkMap.values())

  renderNetwork(rebelNodes, countryNodes, allNodes, edges)
}

const renderNetwork = (rebelNodes, countryNodes, allNodes, edges) => {
  if (!svgContainer.value) return

  d3.select(svgContainer.value).selectAll('*').remove()

  const width = svgContainer.value.clientWidth || 1200
  const height = 700

  const svg = d3
    .select(svgContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])

  // Add zoomable container
  const gContainer = svg.append('g').attr('class', 'zoom-container')

  // Calculate degree (number of connected rebels) for each country
  const countryDegree = new Map()
  const countryConnectedRebels = new Map()
  countryNodes.forEach(country => {
    const connectedRebels = edges
      .filter(e => (e.target === country.id || e.source === country.id))
      .map(e => {
        const rebelId = e.source === country.id ? e.target : e.source
        return rebelNodes.find(r => r.id === rebelId)
      })
      .filter(Boolean)
    const degree = connectedRebels.length
    countryDegree.set(country.id, degree)
    countryConnectedRebels.set(country.id, connectedRebels)
  })

  // Calculate angular positions for countries in a circle
  const centerX = width / 2
  const centerY = height / 2
  const radius = 250
  const countryPositions = new Map()

  // Get angles for rebel groups
  const rebelAngles = new Map()
  rebelNodes.forEach((rebel, index) => {
    const angle = (index / rebelNodes.length) * 2 * Math.PI
    rebelAngles.set(rebel.id, angle)
  })

  // Position countries based on their connected rebels
  countryNodes.forEach((country, countryIndex) => {
    const connectedRebels = countryConnectedRebels.get(country.id)
    let angle

    if (connectedRebels.length === 0) {
      // No connections: position evenly around circle
      angle = (countryIndex / countryNodes.length) * 2 * Math.PI
    } else if (connectedRebels.length === 1) {
      // Single connection: position on the ray of that rebel
      angle = rebelAngles.get(connectedRebels[0].id)
    } else {
      // Multiple connections: position at average angle of connected rebels
      const angles = connectedRebels.map(r => rebelAngles.get(r.id))
      const avgAngle = angles.reduce((a, b) => a + b, 0) / angles.length
      angle = avgAngle
    }

    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius
    countryPositions.set(country.id, { x, y, angle })
  })

  // Create force simulation
  const simulation = d3
    .forceSimulation(allNodes)
    .force(
      'link',
      d3
        .forceLink(edges)
        .id(d => d.id)
        .distance(d => {
          return d.source.type === 'rebel' && d.target.type === 'country' ? 180 : 100
        })
    )
    .force('charge', d3.forceManyBody().strength(-300))
    .force('x', d3.forceX(d => {
      // Keep rebels at center, countries at calculated positions
      if (d.type === 'rebel') {
        return centerX
      } else {
        return countryPositions.get(d.id).x
      }
    }).strength(0.2))
    .force('y', d3.forceY(d => {
      if (d.type === 'rebel') {
        return centerY
      } else {
        return countryPositions.get(d.id).y
      }
    }).strength(0.2))
    .force('collide', d3.forceCollide(d => {
      return d.type === 'rebel' ? Math.sqrt(d.totalEvents) + 20 : (countryDegree.get(d.id) * 8 + 15)
    }))

  // Draw edges (links)
  const link = gContainer
    .selectAll('.link')
    .data(edges)
    .enter()
    .append('line')
    .attr('class', 'link')
    .attr('stroke', d => getFatalityColor(d.fatalities))
    .attr('stroke-width', 4)
    .attr('opacity', 0.6)

  // Draw nodes
  const node = gContainer
    .selectAll('.node')
    .data(allNodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .call(drag(simulation))

  // Render node circles
  node.each(function (d) {
    const g = d3.select(this)

    if (d.type === 'rebel') {
      // Rebel groups: size by total events
      const radius = Math.sqrt(d.totalEvents / Math.PI) + 5
      d.baseRadius = radius
      g.append('circle')
        .attr('class', 'node-circle')
        .attr('r', radius)
        .attr('fill', '#c4b5fd')

      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', '15px')
        .attr('font-weight', '600')
        .attr('fill', '#000')
        .text(d.label)
        .style('pointer-events', 'none')
    } else {
      // Countries: size by degree (number of connected rebels)
      const degree = countryDegree.get(d.id)
      const countryRadius = Math.max(16, degree * 10)
      d.baseRadius = countryRadius
      g.append('circle')
        .attr('class', 'node-circle')
        .attr('r', countryRadius)
        .attr('fill', '#4ecdc4')
        .attr('opacity', 0.8)

      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', '12px')
        .attr('fill', '#333')
        .text(d.label)
        .style('pointer-events', 'none')
    }
  })

  // Add interactivity
  node.on('mouseenter', function (event, d) {
    d3.select(this).select('.node-circle').transition().attr('r', d.baseRadius + 5)

    // Highlight connected links and nodes
    link.attr('opacity', l => {
      return l.source.id === d.id || l.target.id === d.id ? 1 : 0.2
    })

    node.attr('opacity', n => {
      return n.id === d.id || edges.some(e => (e.source.id === d.id && e.target.id === n.id) || (e.target.id === d.id && e.source.id === n.id)) ? 1 : 0.3
    })
  }).on('mouseleave', function (event, d) {
    d3.select(this).select('.node-circle').transition().attr('r', d.baseRadius)
    node.attr('opacity', 1)
    link.attr('opacity', 0.6)
  })

  // Tooltip
  const tooltip = d3
    .select('body')
    .append('div')
    .attr('class', 'network-tooltip')
    .style('position', 'absolute')
    .style('padding', '8px 12px')
    .style('background', 'rgba(0,0,0,0.85)')
    .style('color', '#fff')
    .style('font-size', '11px')
    .style('border-radius', '4px')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', '1000')

  node.on('mouseover', function (event, d) {
    if (d.type === 'rebel') {
    tooltip
      .style('opacity', 1)
      .html(`<strong>${d.label}</strong><br/>Total Events: ${d.totalEvents}`)
      .style('left', event.pageX + 10 + 'px')
      .style('top', event.pageY - 10 + 'px')
    }
  }).on('mousemove', function (event) {
    tooltip
      .style('left', event.pageX + 10 + 'px')
      .style('top', event.pageY - 10 + 'px')
  }).on('mouseout', function () {
    tooltip.style('opacity', 0)
  })

  link.on('mouseover', function (event, d) {
    tooltip
      .style('opacity', 1)
      .html(`${d.source.label} → ${d.target.label}<br/>Events: ${d.events}<br/>Fatalities: ${d.fatalities}`)
      .style('left', event.pageX + 10 + 'px')
      .style('top', event.pageY - 10 + 'px')
  }).on('mousemove', function (event) {
    tooltip
      .style('left', event.pageX + 10 + 'px')
      .style('top', event.pageY - 10 + 'px')
  }).on('mouseout', function () {
    tooltip.style('opacity', 0)
  })

  // Update positions on simulation tick
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    node.attr('transform', d => `translate(${d.x}, ${d.y})`)
  })

  // Zoom & pan
  const zoom = d3.zoom().scaleExtent([0.5, 5]).on('zoom', (event) => {
    gContainer.attr('transform', event.transform)
  })

  svg.call(zoom)
  // Set initial zoom transform to show whole layout (zoomed out)
  const initialScale = 0.7
  const translateX = (width - width * initialScale) / 3
  const translateY = (height - height * initialScale) / 2
  const initialTransform = d3.zoomIdentity.translate(translateX, translateY).scale(initialScale)
  svg.call(zoom.transform, initialTransform)

  // Add gradient legend
  const legendWidth = 110
  const legend1Height = 370

  // Legend positioning and styling
  const legendPadding = 20
  const legendBgColor = '#ffffff'
  const legendBgOpacity = 0.95
  const legendBorder = '#e2e8f0'

  // Right side legends vertical layout
  const rightX = width - 140
  let currentY = 30

  // LEGEND 1: Edge Color (Fatalities)
  const defs = svg.append('defs')
  const gradient = defs.append('linearGradient')
    .attr('id', 'fatality-gradient-bipartite')
    // make gradient vertical
    .attr('x1', '0%')
    .attr('x2', '0%')
    .attr('y1', '0%')
    .attr('y2', '100%')

  const stops = [0, 0.25, 0.5, 0.75, 1]
  stops.forEach(stop => {
    gradient.append('stop')
      .attr('offset', `${stop * 100}%`)
      .attr('stop-color', getFatalityColor(Math.pow(10, stop * Math.log10(100000))))
  })

  svg.append('rect')
    .attr('x', rightX - legendPadding)
    .attr('y', currentY - legendPadding)
    .attr('width', legendWidth + legendPadding + 20)
    .attr('height', legend1Height + 170)
    .attr('fill', legendBgColor)
    .attr('stroke', legendBorder)
    .attr('stroke-width', 1)
    .attr('rx', 4)
    .attr('opacity', legendBgOpacity)

  // Legend title
  svg.append('text')
    .attr('x', rightX + 5)
    .attr('y', currentY + 5)
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .attr('fill', '#475569')
    .text('Edge Color: Fatalities')

  // Legend gradient rectangle (vertical)
  const barWidth = 18
  const barHeight = 140
  const barX = rightX + 5
  const barY = currentY + 18

  svg.append('rect')
    .attr('x', barX)
    .attr('y', barY)
    .attr('width', barWidth)
    .attr('height', barHeight)
    .attr('fill', 'url(#fatality-gradient-bipartite)')
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 1)

  // Tick marks and labels
  const maxLogFatalities = Math.log10(100000)
  const logTickValues = [0, 10, 100, 1000, 10000, 100000]

  logTickValues.forEach((value) => {
    const logValue = value === 0 ? 0 : Math.log10(value + 1)
    // vertical position: higher fatalities at top
    const t = logValue / maxLogFatalities
    const yPos = barY + (1 - t) * barHeight

    svg.append('line')
      .attr('x1', barX + barWidth + 6)
      .attr('x2', barX + barWidth + 12)
      .attr('y1', yPos)
      .attr('y2', yPos)
      .attr('stroke', '#64748b')
      .attr('stroke-width', 1)

    let label = value === 0 ? '0' : value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value.toString()

    svg.append('text')
      .attr('x', barX + barWidth + 16)
      .attr('y', yPos + 3)
      .attr('font-size', '9px')
      .attr('fill', '#64748b')
      .attr('text-anchor', 'start')
      .text(label)
  })


  // LEGEND 2: Rebel Node Size
  currentY += legend1Height - 200 + legendPadding
  svg.append('text')
    .attr('x', rightX + 5)
    .attr('y', currentY)
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .attr('fill', '#666')
    .text('Rebel Groups Size')

  svg.append('text')
    .attr('x', rightX + 5)
    .attr('y', currentY + 15)
    .attr('font-size', '9px')
    .attr('fill', '#666')
    .text('(Total Events)')

  const rebelSizeExamples = [100, 500, 1000]
  rebelSizeExamples.forEach((events, i) => {
    const radius = Math.sqrt(events / Math.PI) + 5
    const y = currentY + 35 + i * (radius + 15)

    svg.append('circle')
      .attr('cx', rightX + 25)
      .attr('cy', y )
      .attr('r', radius)
      .attr('fill', '#c4b5fd')
      .attr('stroke', '#e9d5ff')
      .attr('stroke-width', 1)

    svg.append('text')
      .attr('x', rightX + 60)
      .attr('y', y + 2)
      .attr('font-size', '9px')
      .attr('fill', '#333')
      .text(`${events} events`)
  })

  // LEGEND 3: Country Node Size (by connected rebel groups)
  currentY += legend1Height - 220 + legendPadding
  svg.append('text')
    .attr('x', rightX + 5)
    .attr('y', currentY)
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .attr('fill', '#475569')
    .text('Countries Size')

  svg.append('text')
    .attr('x', rightX + 5)
    .attr('y', currentY + 15)
    .attr('font-size', '9px')
    .attr('fill', '#666')
    .text('(Connected Groups)')

  const countrySizeExamples = [1, 3]
  countrySizeExamples.forEach((groups, i) => {
    const radius = Math.max(16, groups * 10)
    const y = currentY + 35 + i * (radius + 20)

    svg.append('circle')
      .attr('cx', rightX + 25)
      .attr('cy', y)
      .attr('r', radius)
      .attr('fill', '#4ecdc4')
      .attr('opacity', 0.8)
      .attr('stroke', '#2dd4d4')
      .attr('stroke-width', 1)

    svg.append('text')
      .attr('x', rightX + 60)
      .attr('y', y + 2)
      .attr('font-size', '9px')
      .attr('fill', '#333')
      .text(`${groups} group${groups > 1 ? 's' : ''}`)
  })
}

const drag = simulation => {
  const dragStarted = event => {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  const dragged = event => {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  const dragEnded = event => {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }

  return d3
    .drag()
    .on('start', dragStarted)
    .on('drag', dragged)
    .on('end', dragEnded)
}

onMounted(() => {
  buildNetwork()
})
</script>

<template>
  <div class="bipartite-container">
    <h4>Rebel Groups & Active Countries Network</h4>
    <div ref="svgContainer" class="network-svg"></div>
  </div>
</template>
