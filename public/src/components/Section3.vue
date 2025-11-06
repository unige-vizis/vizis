<script setup>
import Boxplot from './visualizations/Boxplot.vue'
</script>

<template>
  <section>
    <!-- Boxplot -->
    <div class="section__inner">
      <h3>Distribution of Sectoral Impacts (fatalities per million)</h3>
      <Boxplot />
      <div>
        <p>
          In order to compare human suffering accorss countries fairly, we used the indicator
          <strong>fatalities per million inhabitants</strong>. This figure is calculated by diving the total number of
          conflict-related deaths in a country by its population, then multiplying by one million. Unlike raw death
          counts, this normalized rate elminates the bias toward large-population countries and allows meaningful
          cross-national comparisons. This boxplot will display the distrubution of conflict fatalities for countries
          grouped by their dominant economic sector: primary (agriculture), secondary (industry), tertiary (services) of
          tourism. It helps to reveal whether countries with differen economic compositions face different levels of
          human sufferin in conflict.
          <!-- 
            1. Primary Sector Impact is the Highest
              The Primary_Impact (blue box) has the largest median and spread compared to other sectors.
              This suggests that countries with a higher share of primary industries (agriculture, mining, etc.) tend to have more fatalities per million associated with that sector.
              The whiskers and outliers indicate significant variability—some countries have extremely high values.

            2. Secondary Sector Impact is Minimal
              Secondary_Impact (orange box) is very low overall, with a tight distribution near zero.
              Even the outliers are relatively small compared to primary and tertiary sectors.
              This means manufacturing and industrial sectors contribute proportionally less to fatalities in these countries.

            3. Tertiary Sector Impact is Moderate but Variable
              Tertiary_Impact (green box) has a wider range than secondary but less than primary.
              There are extreme outliers (above 100,000 fatalities per million weighted), suggesting that in some countries, the service sector is disproportionately linked to fatalities.

            4. Tourism Impact is Negligible
              Tourism_Impact (gray box) is almost flat near zero, with only one visible outlier.
              Tourism does not appear to be a significant contributor to fatalities in these countries.

            5. Outliers Matter
              The presence of extreme outliers (especially in tertiary and primary sectors) indicates that a few countries dominate the fatality burden in certain sectors.
              For example, one country likely has a very high tertiary sector share combined with high fatalities. 
            -->
        </p>
      </div>
    </div>
  </section>
</template>
