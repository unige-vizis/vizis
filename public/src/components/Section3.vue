<script setup>
import Boxplot from './visualizations/Boxplot.vue'
</script>

<template>
  <section>
    <!-- Boxplot -->
    <div class="section__inner">
      <h3>Service Sector Dominates Global Economies</h3>
      <Boxplot />
      <div>
        <p>
          The following Boxplot visualizes the distribution of conflict event impacts across different sectors. Each box
          represents the interquartile range (IQR) of impacts for a sector, with the line inside the box indicating the
          median impact. The "whiskers" extend to the minimum and maximum values within 1.5 times the IQR from the
          quartiles, while any points outside this range are considered outliers.
        </p>
        <p>
          The tertiary sector has the highest median value, indicating that most countries have a strong focus on
          services and tertiary economic activities on average. The primary and secondary sectors both have a low median
          around 20%, suggesting that agriculture, mining, and manufacturing play a smaller role in the overall economic
          structure of most countries. It is also striking that the primary sector shows a large outlier, Somalia with a
          remarkably high share of 60.86%, underscoring the country's heavy dependence on primary industry. Tourism, on
          the other hand, remains at a low level overall, with a median of 2.78%. This shows that tourism makes a small
          part of the overall economy in most countries.
        </p>
      </div>
    </div>
  </section>
</template>
