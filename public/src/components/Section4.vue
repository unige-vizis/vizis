<script setup>
import StreamChart from './visualizations/StreamChart.vue'
</script>

<template>
  <section>
    <div class="container section__inner">
      <h3>Conflict in Mexico and India Throughout the COVID-19 Pandemic</h3>
      <p class="subtitle">Timeline comparison of conflict patterns (2018-2024)</p>

      <StreamChart />

      <div>
        <p>
          When comparing India and Mexico using ACLED raw event-level data, a clear difference appears in both the
          nature of violence before and after the Covid-19 pandemic.
        </p>

        <p>
          <strong>India</strong> recorded much lower levels of political violence before Covid, with unrest
          driven mainly by protests and social tensions. Because India's economy is strongly shaped by a vast tertiary
          sector (services, transport, retail and informal work), the strict nationwide lockdown sharply reduced mobility.
          This led to a temporary collapse of protest activity rather than an escalation of violence. Instead, violence
          shifted toward local enforcement clashes and community tensions, with major protest movements reappearing only
          as the service sector reopened later in 2020 and 2021.
        </p>

        <p>
          <strong>Mexico</strong>, by contrast, shows consistently high levels of political violence throughout the entire period
          (2018-present), driven largely by organized criminal groups, cartel competition and frequent violence against
          civilians. These dynamics continued through Covid: after a short initial decrease due to mobility restrictions,
          violence quickly rebounded as cartels adapted and exploited the economic strain in Mexico's large informal
          tertiary sector.
        </p>

        <p class="main-message">
          Overall, India's violence was episodic and shaped by mobility restrictions in the tertiary sector, leading to
          a temporary decline and later transformation of political unrest, while Mexico's violence remained high and
          criminal-driven throughout the period.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.main-message {
  font-weight: 600;
  background-color: #f0f4f8;
  padding: 1rem;
  border-left: 4px solid #1f77b4;
  margin-top: 1.5rem;
}

.subtitle {
  color: #666;
  font-style: italic;
  margin-bottom: 2rem;
}
</style>
