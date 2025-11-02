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
      <!-- Bar Chart -->
      <div>
        <h3>Top conflict countries</h3>
        <p>Shows the countries with the highest number of conflict events.</p>
        <BarChart />
      </div>
      <div>
        <p>
          <!-- TODO -->
          [Analysis text about the bar chart results will go here. Discuss which countries show the highest
          concentration of religion-related violent events and what this means for civilian populations in those
          regions.]
        </p>
      </div>

      <!-- Grouped Bar Chart -->
      <div>
        <h3>Event types</h3>
        <p>Comparison of event types grouped by different countreis.</p>
        <GroupedBarChart />
      </div>

      <div>
        <p>
          [Analysis text about regional comparison will go here. Explain the trends between Middle East and Sub-Saharan
          Africa, discussing how conflict intensity has evolved and what factors might contribute to these patterns.]
        </p>
      </div>

      <!-- Heatmap -->
      <div>
        <h3>Monthly Frequency of Religion-Related Protests Across Countries</h3>
        <p>
          Highlights temporal patterns, showing peaks when populations experience heightened instability or repression
        </p>
        <Heatmap />
      </div>

      <div>
        <p>
          [Analysis text about temporal patterns will go here. Identify peak periods and discuss what events or
          conditions might have triggered increased protest activity during those times.]
        </p>
      </div>

      <!-- 100% Stacked Bar Chart -->
      <div>
        <h3>Distribution of Event Types in Religion-Related Conflicts</h3>
        <p>
          Share of protests, violence against civilians, and battles - showing whether suffering comes more from direct
          violence, mass protests, or state repression
        </p>
        <StackedBarChart />
      </div>

      <div>
        <p>
          [Analysis text about event type distribution will go here. Compare the proportion of different conflict types
          and discuss what this reveals about the nature of religion-related conflicts in different contexts.]
        </p>
      </div>

      <!-- Waffle Chart -->
      <div>
        <h3>Scale of Human Impact: Religion-Related Events</h3>
        <p>Visual representation of the proportion and scale of religion-related events globally</p>
        <WaffleChart />
      </div>

      <div>
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
    </div>
  </section>
</template>
