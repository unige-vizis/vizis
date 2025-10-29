<script setup>
import BarChart from './visualizations/BarChart.vue'
import GroupedBarChart from './visualizations/GroupedBarChart.vue'
import Heatmap from './visualizations/Heatmap.vue'
import StackedBarChart from './visualizations/StackedBarChart.vue'
import WaffleChart from './visualizations/WaffleChart.vue'
</script>

<template>
  <section>
    <div class="container section__inner">
      <h2>How Religion Impacts Geopolitical Events</h2>
    </div>

    <div class="article-container">
      <!-- Introduction -->
      <div class="article-text">
        <p>
          Religion and geopolitics are deeply interwoven. Religious beliefs can unite societies, but they can also trigger conflict, shape political agendas and influence international relations. When religion intersects with geopolitical interests, tensions often escalate and extend far beyond governments or borders.
        </p>
        <p>
          The consequences are not only political but profoundly human. Such conflicts frequently cause violence, displacement, repression, and long lasting insecurity, all of which contribute to human suffering on a large scale. This project examines how religion shapes geopolitical events and explores the ways in which this interaction increases human suffering across different regions of the world.
        </p>
        <p>
          By comparing different countries, regions, and types of conflict events, we aim to reveal both similarities and differences in the role of religion, and to show how these dynamics vary in scale and intensity.
        </p>
      </div>

      <!-- Bar Chart -->
      <div class="visualization-container">
        <h4 class="visualization-title">Countries with the Highest Number of Religion-Related Violent Events</h4>
        <p class="visualization-subtitle">Shows where religion-related violence is most concentrated, indicating where civilians face the greatest risks</p>
        <BarChart />
      </div>

      <div class="article-text">
        <p class="placeholder-text">
          [Analysis text about the bar chart results will go here. Discuss which countries show the highest concentration of religion-related violent events and what this means for civilian populations in those regions.]
        </p>
      </div>

      <!-- Grouped Bar Chart -->
      <div class="visualization-container">
        <h4 class="visualization-title">Regional Comparison: Religion-Related Conflicts Over Time</h4>
        <p class="visualization-subtitle">Comparing Middle East vs. Sub-Saharan Africa (2020 vs 2023) - demonstrates how intensity shifts across regions and time</p>
        <GroupedBarChart />
      </div>

      <div class="article-text">
        <p class="placeholder-text">
          [Analysis text about regional comparison will go here. Explain the trends between Middle East and Sub-Saharan Africa, discussing how conflict intensity has evolved and what factors might contribute to these patterns.]
        </p>
      </div>

      <!-- Heatmap -->
      <div class="visualization-container">
        <h4 class="visualization-title">Monthly Frequency of Religion-Related Protests Across Countries</h4>
        <p class="visualization-subtitle">Highlights temporal patterns, showing peaks when populations experience heightened instability or repression</p>
        <Heatmap />
      </div>

      <div class="article-text">
        <p class="placeholder-text">
          [Analysis text about temporal patterns will go here. Identify peak periods and discuss what events or conditions might have triggered increased protest activity during those times.]
        </p>
      </div>

      <!-- 100% Stacked Bar Chart -->
      <div class="visualization-container">
        <h4 class="visualization-title">Distribution of Event Types in Religion-Related Conflicts</h4>
        <p class="visualization-subtitle">Share of protests, violence against civilians, and battles - showing whether suffering comes more from direct violence, mass protests, or state repression</p>
        <StackedBarChart />
      </div>

      <div class="article-text">
        <p class="placeholder-text">
          [Analysis text about event type distribution will go here. Compare the proportion of different conflict types and discuss what this reveals about the nature of religion-related conflicts in different contexts.]
        </p>
      </div>

      <!-- Waffle Chart -->
      <div class="visualization-container">
        <h4 class="visualization-title">Scale of Human Impact: Religion-Related Events</h4>
        <p class="visualization-subtitle">Visual representation of the proportion and scale of religion-related events globally</p>
        <WaffleChart />
      </div>

      <div class="article-text">
        <p class="placeholder-text">
          [Analysis text about the overall scale and impact will go here. Provide context about what these numbers mean for human suffering and the global scope of religion-related conflicts.]
        </p>

        <h3>Methodology and Data Sources</h3>
        <p class="placeholder-text">
          [Information about data sources (ACLED), methodology, and any limitations of the analysis will go here.]
        </p>

        <h3>Conclusion</h3>
        <p class="placeholder-text">
          [Concluding remarks synthesizing the findings from all visualizations and their implications for understanding religion's role in geopolitical conflicts and human suffering.]
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
section {
  padding-bottom: 4rem;
}
</style>
