<script setup>
import SankeyChart from './visualizations/SankeyChart.vue'
</script>

<template>
  <section>
    <div class="container section__inner">
      <div class="visualization-section">
        <h3>What does the activity of the most engaged actors look like?</h3>
        <p class="chart-hint">Select an Actor and hover over flows and Nodes to explore details.</p>
        <SankeyChart />

        <p class="chart-hint">Timeline start dates reflect ACLED's regional coverage expansion (Africa from 1997, Middle East 2016, Americas 2018), not when actors became active.</p>

        <div class="two-columns">
          <p>
            This complex Sankey diagram illustrates the flow of conflict involvement across different actor types,
            regions, and conflict categories. The visualization reveals patterns of how various armed groups,
            state forces, and other actors participate in conflicts across different geographical areas and
            conflict types. Width of flows represents the intensity or frequency of involvement, providing
            insights into which actors are most central to global conflict dynamics.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chart-hint {
  color: #64748b;
  margin: 0.25rem 0 0.5rem 0;
}

.visualization-section {
  margin-bottom: 5rem;
}

.visualization-section:last-child {
  margin-bottom: 0;
}
</style>