<script setup>
import StreamChart from './visualizations/StreamChart.vue'
</script>

<template>
  <section>
    <div class="container section__inner">
      <h3>Conflict in Mexico and India Throughout the COVID-19 Pandemic</h3>
      <p class="subtitle">Timeline comparison of conflict patterns (2018-2024)</p>

      <StreamChart />

      <div class="two-columns">
        <p>
          When comparing India and Mexico using ACLED raw event-level data, we can see that India’s conflict activity is
          more volatile and protest-driven, while Mexico’s is characterized by persistent violence against civilians and
          relative stability over time.
        </p>
        <p>
          <strong>India</strong> recorded more protests and riots, showing significant fluctuations over time.
          CCoinciding with the outbreak of the COVID-19 pandemic, a significant decline can be observed in March 2020.
          By 2023–2024, India had returned to the same number of events as before COVID-19. Violence against civilians
          and battles remain low compared to protests.
        </p>
        <p>
          <strong>Mexico</strong>, shows a more stable pattern throughout the period, with violence against civilians
          consistently representing the largest share of events. Protests and riots, along with battles, occur at lower
          and steadier levels. Unlike India, Mexico does not display a pronounced dip during the pandemic period.
        </p>
      </div>
    </div>
  </section>
</template>
