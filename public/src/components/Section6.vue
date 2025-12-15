<script setup>
import SankeyChart from './visualizations/SankeyChart.vue'
import ActorCountryNetwork from './visualizations/ActorCountryNetwork.vue'
</script>

<template>
  <section>
    <div class="section__inner">
      <h3>What does the activity of the most engaged actors look like?</h3>
      <p class="chart-hint">Select an Actor and hover over flows and Nodes to explore details.</p>
      <SankeyChart />

      <p class="chart-hint">
        Timeline start dates reflect ACLED's regional coverage expansion (Africa from 1997, Middle East 2016, Americas
        2018), not when actors became active.
      </p>

      <div class="two-columns">
        <p>
          This complex Sankey diagram illustrates the
          <strong>flow of conflict involvement across different actor types, regions, and conflict categories</strong>.
          The visualization reveals patterns of how various armed groups, state forces, and other actors participate in
          conflicts across different geographical areas and conflict types. Width of flows represents the intensity or
          frequency of involvement, providing insights into which actors are most central to global conflict dynamics.
        </p>
        <p>
          Read it from left to right: the leftmost nodes enumerate <strong>who is engaging</strong> (e.g., state forces,
          non‑state armed groups, militias, other actors), the intermediate columns show <strong>where</strong> those
          engagements occur (regions or countries), and the rightmost nodes show the
          <strong>kinds of conflict events</strong> or categories. The width of each band equals the weight of that flow
          (counts or aggregated intensity), and a node’s total height equals the sum of incoming and outgoing flows
          associated with it.
        </p>
        <p>
          For example the selected actor, <strong>JNIM</strong>, carried out 8,767 violent events across eight West
          African countries between March 2017 and October 2024, resulting in 18,745 fatalities. Most of the activity is
          concentrated in Burkina Faso and Mali, which account for the largest share of incidents and deaths. The
          primary forms of violence include battles and attacks against civilians, followed by explosions and remote
          violence. Fatalities are highest in these categories, as indicated by the darker color flows. The timeline
          reveals a sharp escalation after 2019, peaking around 2022–2023, with sustained high levels of violence
          continuing into 2024, highlighting the persistent and growing threat posed by JNIM in the region.
        </p>
      </div>
    </div>

    <div class="section__inner">
      <h3>Which countries are most affected by the top rebel groups?</h3>
      <ActorCountryNetwork />
      <div class="two-columns">
        <p>
          This network graph visualizes the relationships between the most active rebel groups and the countries they
          impact. Each node represents either a rebel group or a country, with edges connecting groups to the countries
          where they have significant activity. The size of the country nodes indicates the number of rebel groups
          operating within that country, while the size of the rebel group nodes reflects their overall level of events.
          The edges vary in color intensity based on the number of fatalities.
        </p>
        <p>
          By examining this graph, one can identify which rebel groups are most influential and which countries are most
          affected by their actions. For instance, larger nodes signify groups with extensive operations, while thicker
          and darker edges point to countries experiencing higher levels of violence and casualties. This visualization
          provides insights into the geographic spread and intensity of rebel activities, highlighting key areas of
          concern in global conflict dynamics.
        </p>
      </div>
    </div>
  </section>
</template>
