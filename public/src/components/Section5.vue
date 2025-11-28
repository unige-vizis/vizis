<script setup>
import ColorplethMap from './visualizations/ColorplethMap.vue'
import ProportionalSymbolMap from './visualizations/ProportionalSymbolMap.vue'
import InterventionFlowMap from './visualizations/InterventionFlowMap.vue'
</script>

<template>
  <section>
    <div class="container section__inner">
      <div class="map-section">
        <h3>Primary Sector Share (2023)</h3>

        <ColorplethMap />

        <div class="two-columns">
          <p>
            This map visualizes the geographic distribution of primary sector dependence across the globe.
            Countries shaded in darker brown have economies heavily reliant on agriculture, mining, and
            natural resource extraction. Notice how conflict hotspots in Sub-Saharan Africa, Central Asia,
            and parts of the Middle East correlate with higher primary sector shares, supporting our finding
            that resource-dependent economies experience more violent conflict.
          </p>
        </div>
      </div>

      <div class="map-section">
        <h3>Conflict Fatalities by Country (2015-2024)</h3>

        <ProportionalSymbolMap />

        <div class="two-columns">
          <p>
            This proportional symbol map shows the severity of conflict across countries, with circle size
            representing total fatalities recorded between 2015-2024. The stark visual contrast between
            regions highlights the dramatic difference in conflict deadliness. Countries like Syria, Ukraine,
            Afghanistan, and Ethiopia show the largest circles, reflecting the devastating toll of prolonged
            armed conflicts. Meanwhile, service-based economies in Europe and North America show minimal
            conflict fatalities, reinforcing the connection between economic structure and conflict intensity.
          </p>
        </div>
      </div>

      <div class="map-section">
        <h3>Military Interventions in Armed Conflicts</h3>

        <InterventionFlowMap />

        <div class="two-columns">
          <p>
            This flow map reveals which countries intervene militarily in foreign conflicts, with arrows
            connecting intervening nations to conflict zones. Colors indicate intervention blocs: Western
            powers (blue), Russian-aligned states (red), African regional forces (orange), and others
            (purple). Use the slider to explore how intervention patterns shift year by year—note the
            sustained Russia-Iran axis in Syria, Western presence in the Sahel, and the dramatic increase
            in foreign involvement in Sudan and Ethiopia in recent years.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.map-section {
  margin-bottom: 5rem;
}

.map-section:last-child {
  margin-bottom: 0;
}
</style>
