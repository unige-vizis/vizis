<script setup>
import { onMounted, onUnmounted, ref, computed, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal, sankeyLeft } from 'd3-sankey'

// Load data
import sankeyData from '@/assets/data/viz10_actor_sankey.json'

const chartRef = ref(null)
const containerWidth = ref(0)
const selectedActor = ref(null)
const searchQuery = ref('')
const showActorMenu = ref(false)

// Extract actor types and actors from data
const actorTypes = computed(() => sankeyData.actor_types)

// Filter actors based on search
const filteredActorTypes = computed(() => {
  if (!searchQuery.value) return actorTypes.value

  const query = searchQuery.value.toLowerCase()
  const filtered = {}

  for (const [type, actors] of Object.entries(actorTypes.value)) {
    const matchingActors = actors.filter(actor =>
      actor.toLowerCase().includes(query)
    )
    if (matchingActors.length > 0) {
      filtered[type] = matchingActors
    }
  }

  return filtered
})

// Get flows for selected actor
const actorFlows = computed(() => {
  if (!selectedActor.value) return []
  return sankeyData.flows.filter(f => f.actor === selectedActor.value)
})

// Get actor stats for display in dropdown
const actorStats = computed(() => {
  const stats = {}
  for (const flow of sankeyData.flows) {
    if (!stats[flow.actor]) {
      stats[flow.actor] = { events: 0, fatalities: 0, countries: new Set() }
    }
    stats[flow.actor].events += flow.events
    stats[flow.actor].fatalities += flow.fatalities
    stats[flow.actor].countries.add(flow.country)
  }
  // Convert Sets to counts
  for (const actor in stats) {
    stats[actor].countries = stats[actor].countries.size
  }
  return stats
})

// Sort actors within each type by event count (descending)
const sortedActorTypes = computed(() => {
  const sorted = {}
  for (const [type, actors] of Object.entries(actorTypes.value)) {
    sorted[type] = [...actors].sort((a, b) => {
      const eventsA = actorStats.value[a]?.events || 0
      const eventsB = actorStats.value[b]?.events || 0
      return eventsB - eventsA
    })
  }
  return sorted
})

// Chart dimensions
const margin = { top: 85, right: 200, bottom: 40, left: 20 }
const height = 600

// Fatality color scale (Yellow to Orange to Red) - keeps most values yellow, only highest go red
const maxLogFatalities = Math.log10(sankeyData.metadata.fatality_stats.max + 1)
const fatalityColorScale = d3.scaleSequential()
  .domain([0, maxLogFatalities])
  .interpolator(t => d3.interpolateYlOrRd(Math.pow(t, 2.5) * 0.75 + 0.1))

function getFlowColor(fatalities) {
  if (fatalities === 0) return '#fee8c8'
  return fatalityColorScale(Math.log10(fatalities + 1))
}

// Transform data for D3 sankey
function transformToSankeyData(flows) {
  if (!flows || flows.length === 0) return { nodes: [], links: [] }

  const nodesMap = new Map()
  const links = []

  // Add actor node (Level 1)
  const actorId = `actor_${selectedActor.value}`
  nodesMap.set(actorId, {
    id: actorId,
    name: selectedActor.value,
    category: 'actor',
    depth: 0
  })

  // Process flows to create country and event type nodes
  for (const flow of flows) {
    const countryId = `country_${flow.country}`
    const eventTypeId = `event_${flow.event_type}`

    // Add country node (Level 2)
    if (!nodesMap.has(countryId)) {
      nodesMap.set(countryId, {
        id: countryId,
        name: flow.country,
        category: 'country',
        depth: 1
      })
    }

    // Add event type node (Level 3)
    if (!nodesMap.has(eventTypeId)) {
      nodesMap.set(eventTypeId, {
        id: eventTypeId,
        name: flow.event_type,
        category: 'event_type',
        depth: 2
      })
    }

    // Create link: Actor -> Country
    const actorCountryKey = `${actorId}->${countryId}`
    let actorCountryLink = links.find(l => l.key === actorCountryKey)
    if (!actorCountryLink) {
      actorCountryLink = {
        key: actorCountryKey,
        source: actorId,
        target: countryId,
        value: 0,
        fatalities: 0,
        flows: []
      }
      links.push(actorCountryLink)
    }
    actorCountryLink.value += flow.events
    actorCountryLink.fatalities += flow.fatalities
    actorCountryLink.flows.push(flow)

    // Create link: Country -> Event Type
    const countryEventKey = `${countryId}->${eventTypeId}`
    let countryEventLink = links.find(l => l.key === countryEventKey)
    if (!countryEventLink) {
      countryEventLink = {
        key: countryEventKey,
        source: countryId,
        target: eventTypeId,
        value: 0,
        fatalities: 0,
        flows: []
      }
      links.push(countryEventLink)
    }
    countryEventLink.value += flow.events
    countryEventLink.fatalities += flow.fatalities
    countryEventLink.flows.push(flow)
  }

  // Convert nodes map to array
  const nodes = Array.from(nodesMap.values())

  // Convert source/target from IDs to indices
  const nodeIndex = new Map(nodes.map((n, i) => [n.id, i]))
  const indexedLinks = links.map(l => ({
    ...l,
    source: nodeIndex.get(l.source),
    target: nodeIndex.get(l.target)
  }))

  return { nodes, links: indexedLinks }
}

function updateChart() {
  const container = chartRef.value
  if (!container || !selectedActor.value) return

  // Clear previous chart
  d3.select(container).selectAll('*').remove()

  const flows = actorFlows.value
  if (flows.length === 0) return

  const width = containerWidth.value - margin.left - margin.right
  const svgHeight = height - margin.top - margin.bottom

  // Transform data
  const { nodes, links } = transformToSankeyData(flows)

  if (nodes.length === 0) return

  // Create SVG
  const svg = d3.select(container)
    .append('svg')
    .attr('width', containerWidth.value)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create sankey generator
  const sankeyGenerator = sankey()
    .nodeWidth(20)
    .nodePadding(15)
    .nodeAlign(sankeyLeft)
    .extent([[0, 0], [width, svgHeight]])

  // Generate layout
  const { nodes: layoutNodes, links: layoutLinks } = sankeyGenerator({
    nodes: nodes.map(d => ({ ...d })),
    links: links.map(d => ({ ...d }))
  })

  // Create tooltip
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'sankey-tooltip')
    .style('opacity', 0)
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.85)')
    .style('color', 'white')
    .style('padding', '12px')
    .style('border-radius', '6px')
    .style('pointer-events', 'none')
    .style('font-size', '13px')
    .style('max-width', '300px')
    .style('z-index', '1000')
    .style('box-shadow', '0 4px 12px rgba(0,0,0,0.3)')

  // Draw link outlines first (underneath)
  const linkOutline = svg.append('g')
    .attr('class', 'link-outlines')
    .attr('fill', 'none')
    .selectAll('path')
    .data(layoutLinks)
    .enter()
    .append('path')
    .attr('d', sankeyLinkHorizontal())
    .attr('stroke', '#00000030')
    .attr('stroke-width', d => Math.max(1, d.width) + 2)
    .attr('opacity', 0.7)

  // Draw links on top
  const link = svg.append('g')
    .attr('class', 'link-fills')
    .attr('fill', 'none')
    .selectAll('path')
    .data(layoutLinks)
    .enter()
    .append('path')
    .attr('d', sankeyLinkHorizontal())
    .attr('stroke', d => getFlowColor(d.fatalities))
    .attr('stroke-width', d => Math.max(1, d.width))
    .attr('opacity', 0.7)
    .style('mix-blend-mode', 'multiply')
    .on('mouseover', function(event, d) {
      d3.select(this)
        .attr('opacity', 1)
        .attr('stroke-width', d => Math.max(2, d.width * 1.1))

      // Also highlight the outline
      linkOutline.filter(l => l === d)
        .attr('stroke-width', d => Math.max(2, d.width * 1.1) + 2)

      // Highlight connected nodes
      svg.selectAll('.node')
        .attr('opacity', n =>
          n.id === d.source.id || n.id === d.target.id ? 1 : 0.3
        )

      // Dim other links
      link.attr('opacity', l => l === d ? 1 : 0.2)
      linkOutline.attr('opacity', l => l === d ? 0.7 : 0.2)

      tooltip
        .style('opacity', 1)
        .html(`
          <strong>${d.source.name} → ${d.target.name}</strong><br/>
          <span style="color: #93c5fd;">Events:</span> ${d.value.toLocaleString()}<br/>
          <span style="color: #fca5a5;">Fatalities:</span> ${d.fatalities.toLocaleString()}
        `)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this)
        .attr('opacity', 0.7)
        .attr('stroke-width', d => Math.max(1, d.width))

      // Reset outline
      linkOutline
        .attr('opacity', 0.7)
        .attr('stroke-width', d => Math.max(1, d.width) + 2)

      svg.selectAll('.node').attr('opacity', 1)
      link.attr('opacity', 0.7)
      tooltip.style('opacity', 0)
    })

  // Draw nodes
  const node = svg.append('g')
    .selectAll('g')
    .data(layoutNodes)
    .enter()
    .append('g')
    .attr('class', 'node')

  // Event type colors
  const eventTypeColors = {
    'Battles': '#2563EB',                      // blue
    'Explosions/Remote violence': '#D97706',   // orange
    'Violence against civilians': '#DC2626',   // red
    'Strategic developments': '#0891b2',       // cyan
    'Protests': '#059669',                     // emerald green
    'Riots': '#7c3aed'                         // violet
  }

  node.append('rect')
    .attr('x', d => d.x0)
    .attr('y', d => d.y0)
    .attr('height', d => Math.max(1, d.y1 - d.y0))
    .attr('width', d => d.x1 - d.x0)
    .attr('fill', d => {
      if (d.category === 'event_type') return eventTypeColors[d.name] || '#64748b'
      if (d.category === 'actor') return '#c4b5fd'  // light purple for actor
      return '#ddd6fe'  // lighter lavender for country
    })
    .attr('stroke', '#333')
    .attr('stroke-width', 1)
    .on('mouseover', function(event, d) {
      d3.select(this).attr('stroke-width', 2)

      // Calculate node totals
      const incomingEvents = d.targetLinks?.reduce((sum, l) => sum + l.value, 0) || 0
      const outgoingEvents = d.sourceLinks?.reduce((sum, l) => sum + l.value, 0) || 0
      const totalEvents = Math.max(incomingEvents, outgoingEvents)

      const incomingFatalities = d.targetLinks?.reduce((sum, l) => sum + l.fatalities, 0) || 0
      const outgoingFatalities = d.sourceLinks?.reduce((sum, l) => sum + l.fatalities, 0) || 0
      const totalFatalities = Math.max(incomingFatalities, outgoingFatalities)

      tooltip
        .style('opacity', 1)
        .html(`
          <strong>${d.name}</strong><br/>
          <span style="color: #a5b4fc;">${d.category.replace('_', ' ')}</span><br/>
          <span style="color: #93c5fd;">Events:</span> ${totalEvents.toLocaleString()}<br/>
          <span style="color: #fca5a5;">Fatalities:</span> ${totalFatalities.toLocaleString()}
        `)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
    })
    .on('mouseout', function() {
      d3.select(this).attr('stroke-width', 1)
      tooltip.style('opacity', 0)
    })

  // Node labels (skip actor nodes - they don't need labels)
  node.filter(d => d.category !== 'actor')
    .append('text')
    .attr('x', d => d.category === 'event_type' ? d.x1 + 6 : d.x0 - 6)
    .attr('y', d => (d.y0 + d.y1) / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', d => d.category === 'event_type' ? 'start' : 'end')
    .attr('font-size', '12px')
    .attr('fill', '#333')
    .text(d => {
      // Truncate long names
      const maxLen = 25
      return d.name.length > maxLen ? d.name.slice(0, maxLen) + '...' : d.name
    })

  // Color legend - centered at top
  const legendWidth = 280
  const legendHeight = 18
  const legendX = (width - legendWidth) / 2
  const legendY = -55

  // Create gradient for legend
  const defs = svg.append('defs')
  const gradient = defs.append('linearGradient')
    .attr('id', 'fatality-gradient')
    .attr('x1', '0%')
    .attr('x2', '100%')

  const stops = [0, 0.25, 0.5, 0.75, 1]
  stops.forEach(stop => {
    gradient.append('stop')
      .attr('offset', `${stop * 100}%`)
      .attr('stop-color', fatalityColorScale(stop * maxLogFatalities))
  })

  // Legend title
  svg.append('text')
    .attr('x', legendX + legendWidth / 2)
    .attr('y', legendY - 8)
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .attr('fill', '#475569')
    .attr('text-anchor', 'middle')
    .text('Fatalities (log scale)')

  // Legend gradient rectangle
  svg.append('rect')
    .attr('x', legendX)
    .attr('y', legendY)
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .attr('fill', 'url(#fatality-gradient)')
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 1)

  // Add reference tick marks and labels - using log scale positions
  const maxFatalities = sankeyData.metadata.fatality_stats.max
  // Create log-spaced tick values: 0, 10, 100, 1000, 10000, etc.
  const logTickValues = [0]
  let power = 1
  while (Math.pow(10, power) <= maxFatalities) {
    logTickValues.push(Math.pow(10, power))
    power++
  }
  if (logTickValues[logTickValues.length - 1] < maxFatalities) {
    logTickValues.push(maxFatalities)
  }

  logTickValues.forEach((value) => {
    // Position based on log scale (matching the color scale domain)
    const logValue = value === 0 ? 0 : Math.log10(value + 1)
    const xPos = legendX + (legendWidth * logValue / maxLogFatalities)

    // Tick mark
    svg.append('line')
      .attr('x1', xPos)
      .attr('x2', xPos)
      .attr('y1', legendY + legendHeight)
      .attr('y2', legendY + legendHeight + 4)
      .attr('stroke', '#64748b')
      .attr('stroke-width', 1)

    // Label - format large numbers compactly
    let label
    if (value === 0) label = '0'
    else if (value >= 1000) label = (value / 1000).toFixed(0) + 'k'
    else label = value.toString()

    svg.append('text')
      .attr('x', xPos)
      .attr('y', legendY + legendHeight + 14)
      .attr('font-size', '9px')
      .attr('fill', '#64748b')
      .attr('text-anchor', 'middle')
      .text(label)
  })
}

function selectActor(actor) {
  selectedActor.value = actor
  searchQuery.value = ''
  showActorMenu.value = false
}

function openActorMenu() {
  showActorMenu.value = true
}

function closeActorMenu() {
  showActorMenu.value = false
  searchQuery.value = ''
}

function handleResize() {
  if (chartRef.value) {
    containerWidth.value = chartRef.value.offsetWidth
  }
}

// Set up resize observer
let resizeObserver

onMounted(async () => {
  await nextTick()

  handleResize()
  resizeObserver = new ResizeObserver(handleResize)
  if (chartRef.value) {
    resizeObserver.observe(chartRef.value)
  }

  // Select JNIM as default actor
  selectedActor.value = 'JNIM: Group for Support of Islam and Muslims'
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  d3.selectAll('.sankey-tooltip').remove()
})

watch(selectedActor, async () => {
  if (selectedActor.value) {
    await nextTick()
    handleResize()
    if (containerWidth.value > 0) {
      updateChart()
    }
  }
})

watch(containerWidth, () => {
  if (selectedActor.value && containerWidth.value > 0) {
    updateChart()
  }
})
</script>

<template>
  <div class="sankey-wrapper">
    <!-- Sankey Chart -->
    <div class="sankey-container">
      <div v-if="!selectedActor" class="placeholder-message">
        Click the button to select an actor
      </div>
      <div class="chart-area">
        <div class="chart-container" ref="chartRef"></div>
        <!-- Actor Selector Button - overlaid on actor block -->
        <div class="actor-selector-btn" @click="openActorMenu">
          <span class="btn-label">Select Actor</span>
          <span class="btn-actor-name" v-if="selectedActor">
            {{ selectedActor }}
          </span>
          <span class="btn-actor-name placeholder" v-else>Click here...</span>
          <span class="btn-dropdown">↓</span>
        </div>
      </div>

      <!-- Actor Summary -->
      <div v-if="selectedActor && actorStats[selectedActor]" class="actor-summary">
        <h4>{{ selectedActor }}</h4>
        <div class="summary-stats">
          <span><strong>{{ actorStats[selectedActor].events.toLocaleString() }}</strong> events</span>
          <span><strong>{{ actorStats[selectedActor].fatalities.toLocaleString() }}</strong> fatalities</span>
          <span><strong>{{ actorStats[selectedActor].countries }}</strong> countries</span>
        </div>
      </div>
    </div>

    <!-- Actor Selection Modal Overlay -->
    <div v-if="showActorMenu" class="modal-overlay" @click.self="closeActorMenu">
      <div class="actor-modal">
        <div class="modal-header">
          <h3>Select an Actor</h3>
          <button class="close-btn" @click="closeActorMenu">&times;</button>
        </div>

        <div class="actor-grid">
          <div
            v-for="(actors, actorType) in sortedActorTypes"
            :key="actorType"
            class="actor-type-cell"
          >
            <div class="actor-type-header">{{ actorType }}</div>
            <div class="actor-list">
              <div
                v-for="actor in actors"
                :key="actor"
                class="actor-item"
                :class="{ selected: selectedActor === actor }"
                @click="selectActor(actor)"
                :title="actor + ' (' + (actorStats[actor]?.events.toLocaleString() || 0) + ' events, ' + (actorStats[actor]?.countries || 0) + ' countries)'"
              >
                <span class="actor-events">{{ actorStats[actor]?.events || 0 }}</span>
                <span class="actor-name">{{ actor }}</span>
                <span class="actor-countries">{{ actorStats[actor]?.countries || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sankey-wrapper {
  position: relative;
  width: 100%;
  min-height: 650px;
}

/* Chart Area - relative container for overlay positioning */
.chart-area {
  position: relative;
  width: 100%;
  overflow: visible;
}

/* Actor Selector Button - centered above actor column */
.actor-selector-btn {
  position: absolute;
  top: -25px;
  left: 30px;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.4rem 0.5rem 0.3rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  font-size: 0.8rem;
  text-align: center;
  width: 130px;
  z-index: 10;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.actor-selector-btn:hover {
  border-color: #94a3b8;
  background: #f1f5f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}

.actor-selector-btn:hover .btn-dropdown {
  background: #3b82f6;
  border-color: #2563eb;
}

.btn-label {
  font-weight: 600;
  color: #475569;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.btn-actor-name {
  color: #1e293b;
  font-weight: 500;
  font-size: 0.75rem;
  line-height: 1.25;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
}

.btn-actor-name.placeholder {
  color: #94a3b8;
  font-weight: 400;
}

.btn-dropdown {
  display: inline-block;
  margin-top: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: #64748b;
  color: white;
  font-size: 0.65rem;
  font-weight: 500;
  border-radius: 3px;
  border: 1px solid #475569;
  transition: all 0.15s;
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.actor-modal {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 1100px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px !important;
  margin: 0 !important;
  background: #f8fafc;
}

.modal-header h3 {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 1rem;
  color: #1e293b;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #1e293b;
}

.actor-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  align-items: start;
  gap: 2px !important;
  padding: 4px !important;
  margin: 0 !important;
}

.actor-type-cell {
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 !important;
  padding: 0 !important;
}

.actor-type-header {
  padding: 4px 8px !important;
  margin: 0 !important;
  background: #475569;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  letter-spacing: 0.02em;
  line-height: 1.3;
}

.actor-list {
  margin: 0 !important;
  padding: 0 !important;
}

.actor-item {
  margin: 0 !important;
  padding: 2px 0 !important;
  cursor: pointer;
  font-size: 0.9rem;
  color: #334155;
  line-height: 1.3;
  transition: background 0.1s;
  display: flex;
  align-items: center;
  gap: 0;
}

.actor-events {
  width: 38px;
  min-width: 38px;
  padding: 1px 4px;
  font-size: 0.7rem;
  color: #64748b;
  text-align: right;
  background: #f1f5f9;
  border-right: 1px solid #e2e8f0;
}

.actor-name {
  flex: 1;
  padding: 1px 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actor-countries {
  width: 20px;
  min-width: 20px;
  padding: 1px 4px;
  font-size: 0.7rem;
  color: #64748b;
  text-align: center;
  background: #f1f5f9;
  border-left: 1px solid #e2e8f0;
}

.actor-item:hover {
  background: #dbeafe;
}

.actor-item:hover .actor-events,
.actor-item:hover .actor-countries {
  background: #bfdbfe;
}

.actor-item.selected {
  background: #3b82f6;
  color: #fff;
}

.actor-item.selected .actor-events,
.actor-item.selected .actor-countries {
  background: #2563eb;
  color: #dbeafe;
  border-color: #1d4ed8;
}

/* Sankey Container */
.sankey-container {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.placeholder-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #64748b;
  font-size: 1rem;
  text-align: center;
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
}

.chart-container {
  width: 100%;
  min-height: 600px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.actor-summary {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.actor-summary h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #1e293b;
}

.summary-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: #475569;
}

.summary-stats span strong {
  color: #1e293b;
}

/* Responsive adjustments */
@media (max-width: 900px) {
  .actor-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .actor-selector-btn {
    width: 110px;
    left: 30px;
    padding: 0.3rem 0.4rem;
  }

  .btn-actor-name {
    font-size: 0.7rem;
  }

  .actor-modal {
    max-width: 95vw;
  }

  .actor-grid {
    grid-template-columns: 1fr;
  }

  .summary-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
