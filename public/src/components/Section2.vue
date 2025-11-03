<script setup>
import BarChart from './visualizations/BarChart.vue'
import GroupedBarChart from './visualizations/GroupedBarChart.vue'
import Heatmap from './visualizations/Heatmap.vue'
import StackedBarChart from './visualizations/StackedBarChart.vue'
import WaffleChart from './visualizations/WaffleChart.vue'
</script>

<template>
  <section>
    <!-- Bar Chart -->
    <div class="section__inner">
      <h3>Top conflict countries</h3>
      <p>Shows the countries with the highest number of conflict events.</p>
    </div>
    <BarChart />
    <div class="section__inner">
      <p>
        <!-- TODO -->
        [Analysis text about the bar chart results will go here. Discuss which countries show the highest
        concentration of religion-related violent events and what this means for civilian populations in those
        regions.]
      </p>
    </div>

    <!-- 100% Stacked Bar Chart -->
    <div class="section__inner">
      <h3>Economic Sector Composition of Highlighted Conflict Countries</h3>
      <p>
        Distribution of economic sectors (Primary, Secondary, Tertiary, Tourism) for the 7 highlighted countries from the bar chart above. Tourism is shown separately but is already part of the Tertiary sector. Shows the economic makeup of each country to understand the relationship between economic structure and conflict patterns.
      </p>
    </div>
    <StackedBarChart />

    <div class="section__inner">
      <p>
        [Analysis text about economic sector composition will go here. Discuss patterns such as whether countries with higher primary sector dependency experience more conflicts, or how service-based economies compare in terms of conflict events.]
      </p>
    </div>

    <!-- Grouped Bar Chart -->
    <div class="section__inner">
      <h3>Event types</h3>
      <p>Comparison of event types for the same 7 highlighted countries. Protests and riots are grouped together for clearer analysis.</p>
    </div>
    <GroupedBarChart />

    <div class="section__inner">
      <p>
        [Analysis text about regional comparison will go here. Explain the trends between Middle East and Sub-Saharan
        Africa, discussing how conflict intensity has evolved and what factors might contribute to these patterns.]
      </p>
    </div>

    <!-- Heatmap -->
    <div class="section__inner">
      <h3>Temporal Distribution of Event Types (2015-2024)</h3>
      <p>
        Dual-metric visualization showing both event frequency (purple, top) and fatalities (red, bottom) for each conflict type and year. The horizontal split reveals whether high event counts correlate with high death tolls or if certain event types are deadlier than others.
      </p>
    </div>
    <Heatmap />

    <div class="section__inner">
      <p>
        [Analysis text about temporal patterns will go here. Identify peak periods and discuss what events or
        conditions might have triggered changes in event type frequencies during those years. Note the relationship between fatalities and event counts.]
      </p>
    </div>

    <!-- Waffle Chart -->
    <div class="section__inner">
      <h3>Scale of Human Impact: Religion-Related Events</h3>
      <p>Visual representation of the proportion and scale of religion-related events globally</p>
    </div>
    <WaffleChart />

    <div class="section__inner">
      <p>
        [Analysis text about the overall scale and impact will go here. Provide context about what these numbers mean
        for human suffering and the global scope of religion-related conflicts.]
      </p>

      <h3>Methodology and Data Sources</h3>
      <p>[Information about data sources (ACLED), methodology, and any limitations of the analysis will go here.]</p>

      <h3>Conclusion</h3>
      <p>
        [Concluding remarks synthesizing the findings from all visualizations and their implications for understanding
        religion's role in geopolitical conflicts and human suffering.]
      </p>
    </div>
  </section>
</template>
