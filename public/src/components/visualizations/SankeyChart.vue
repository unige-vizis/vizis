<script setup>
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'

// Load data
import sankeyData from '@/assets/data/viz10_actor_sankey.json'

const chartRef = ref(null)
const containerWidth = ref(0)
const selectedActor = ref(null)
const searchQuery = ref('')

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

// Chart dimensions
const margin = { top: 40, right: 200, bottom: 40, left: 20 }
const height = 600

// Fatality color scale (Orange to dark red)
const fatalityColorScale = d3.scaleSequential()
  .domain([0, Math.log10(sankeyData.metadata.fatality_stats.max + 1)])
  .interpolator(d3.interpolateOrRd)

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
    .nodeAlign(d3.sankeyLeft)
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

  // Draw links
  const link = svg.append('g')
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

      // Highlight connected nodes
      svg.selectAll('.node')
        .attr('opacity', n =>
          n.id === d.source.id || n.id === d.target.id ? 1 : 0.3
        )

      // Dim other links
      link.attr('opacity', l => l === d ? 1 : 0.2)

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

  // Node colors by category
  const nodeColorScale = d3.scaleOrdinal()
    .domain(['actor', 'country', 'event_type'])
    .range(['#dc2626', '#2563eb', '#059669'])

  node.append('rect')
    .attr('x', d => d.x0)
    .attr('y', d => d.y0)
    .attr('height', d => Math.max(1, d.y1 - d.y0))
    .attr('width', d => d.x1 - d.x0)
    .attr('fill', d => nodeColorScale(d.category))
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

  // Node labels
  node.append('text')
    .attr('x', d => d.category === 'event_type' ? d.x1 + 6 : d.x0 - 6)
    .attr('y', d => (d.y0 + d.y1) / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', d => d.category === 'event_type' ? 'start' : 'end')
    .attr('font-size', '12px')
    .attr('font-weight', d => d.category === 'actor' ? 'bold' : 'normal')
    .attr('fill', '#333')
    .text(d => {
      // Truncate long names
      const maxLen = d.category === 'actor' ? 40 : 25
      return d.name.length > maxLen ? d.name.slice(0, maxLen) + '...' : d.name
    })

  // Column headers
  const columnLabels = [
    { x: 0, label: 'Actor', color: '#dc2626' },
    { x: width * 0.45, label: 'Countries', color: '#2563eb' },
    { x: width * 0.9, label: 'Event Types', color: '#059669' }
  ]

  svg.selectAll('.column-label')
    .data(columnLabels)
    .enter()
    .append('text')
    .attr('class', 'column-label')
    .attr('x', d => d.x)
    .attr('y', -15)
    .attr('font-size', '14px')
    .attr('font-weight', 'bold')
    .attr('fill', d => d.color)
    .text(d => d.label)

  // Color legend
  const legendWidth = 150
  const legendHeight = 15
  const legendX = width - legendWidth
  const legendY = svgHeight + 25

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
      .attr('stop-color', fatalityColorScale(stop * Math.log10(sankeyData.metadata.fatality_stats.max + 1)))
  })

  svg.append('rect')
    .attr('x', legendX)
    .attr('y', legendY)
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .attr('fill', 'url(#fatality-gradient)')
    .attr('stroke', '#999')

  svg.append('text')
    .attr('x', legendX)
    .attr('y', legendY - 5)
    .attr('font-size', '11px')
    .attr('fill', '#666')
    .text('Fatalities (log scale)')

  svg.append('text')
    .attr('x', legendX)
    .attr('y', legendY + legendHeight + 12)
    .attr('font-size', '10px')
    .attr('fill', '#666')
    .text('0')

  svg.append('text')
    .attr('x', legendX + legendWidth)
    .attr('y', legendY + legendHeight + 12)
    .attr('font-size', '10px')
    .attr('fill', '#666')
    .attr('text-anchor', 'end')
    .text(sankeyData.metadata.fatality_stats.max.toLocaleString())
}

function selectActor(actor) {
  selectedActor.value = actor
  searchQuery.value = ''
}

function handleResize() {
  if (chartRef.value) {
    containerWidth.value = chartRef.value.offsetWidth
  }
}

// Set up resize observer
let resizeObserver

onMounted(() => {
  handleResize()
  resizeObserver = new ResizeObserver(handleResize)
  if (chartRef.value) {
    resizeObserver.observe(chartRef.value)
  }

  // Select first actor by default
  const firstType = Object.keys(actorTypes.value)[0]
  if (firstType && actorTypes.value[firstType].length > 0) {
    selectedActor.value = actorTypes.value[firstType][0]
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  d3.selectAll('.sankey-tooltip').remove()
})

watch([selectedActor, containerWidth], () => {
  if (selectedActor.value && containerWidth.value > 0) {
    updateChart()
  }
})
</script>

<template>
  <div class="sankey-wrapper">
    <!-- Actor Selection Panel -->
    <div class="actor-panel">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search actors..."
          class="search-input"
        />
      </div>

      <div class="actor-list">
        <div
          v-for="(actors, actorType) in filteredActorTypes"
          :key="actorType"
          class="actor-type-group"
        >
          <div class="actor-type-header">{{ actorType }}</div>
          <div
            v-for="actor in actors"
            :key="actor"
            class="actor-item"
            :class="{ selected: selectedActor === actor }"
            @click="selectActor(actor)"
          >
            <span class="actor-name" :title="actor">
              {{ actor.length > 35 ? actor.slice(0, 35) + '...' : actor }}
            </span>
            <span class="actor-stats" v-if="actorStats[actor]">
              {{ actorStats[actor].events.toLocaleString() }} events
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Sankey Chart -->
    <div class="sankey-container">
      <div v-if="!selectedActor" class="placeholder-message">
        Select an actor from the list to view their conflict involvement
      </div>
      <div v-else class="chart-container" ref="chartRef"></div>

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
  </div>
</template>

<style scoped>
.sankey-wrapper {
  display: flex;
  gap: 1.5rem;
  width: 100%;
  min-height: 650px;
}

.actor-panel {
  width: 280px;
  flex-shrink: 0;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.search-box {
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.actor-list {
  flex: 1;
  overflow-y: auto;
  max-height: 580px;
}

.actor-type-group {
  border-bottom: 1px solid #e2e8f0;
}

.actor-type-group:last-child {
  border-bottom: none;
}

.actor-type-header {
  padding: 0.5rem 0.75rem;
  background: #e2e8f0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #475569;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 1;
}

.actor-item {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  border-left: 3px solid transparent;
  transition: all 0.15s;
}

.actor-item:hover {
  background: #f1f5f9;
}

.actor-item.selected {
  background: #dbeafe;
  border-left-color: #3b82f6;
}

.actor-name {
  font-size: 0.8125rem;
  color: #1e293b;
  line-height: 1.3;
}

.actor-stats {
  font-size: 0.6875rem;
  color: #64748b;
}

.sankey-container {
  flex: 1;
  min-width: 0;
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
  .sankey-wrapper {
    flex-direction: column;
  }

  .actor-panel {
    width: 100%;
  }

  .actor-list {
    max-height: 200px;
  }
}
</style>
