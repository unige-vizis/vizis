<script setup>
import Boxplot from './visualizations/Boxplot.vue'
import PyramidChart from './visualizations/PyramidChart.vue'
import RidgeChart from './visualizations/RidgeChart.vue'
import ViolinPlotDebt from './visualizations/ViolinPlotDebt.vue'
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

    <!-- Pyramid Chart -->
    <div class="section__inner">
      <h3>Richer Nations Tend to Rely on Services, Not Industry or Agriculture</h3>
      <PyramidChart />
      <p>
        This pyramid chart compares the distribution of GDP per capita between countries dominated by different
        economic sectors. Countries are categorized into two groups: those where the <strong>Primary and Secondary
        sectors</strong> (agriculture and manufacturing) together account for more than 50% of the economy (shown in
        orange on the left), and those where the <strong>Tertiary sector</strong> (services) dominates with 50% or
        more (shown in blue on the right). The data represents the most recent year available for each country.
      </p>
      <p>
        The visualization reveals a clear pattern: countries dominated by tertiary (service) sectors tend to have
        higher GDP per capita overall. The tertiary-dominated countries show a broader distribution across all income
        levels, with significant representation in the higher GDP brackets (20k-80k+ range). In contrast,
        primary+secondary dominated countries are heavily concentrated in the lower GDP brackets (0-5k range), with
        only a few reaching higher income levels. This suggests that <strong>economic development and the transition
        to service-based economies are strongly correlated with higher national income levels</strong>. The few
        primary+secondary dominated countries in higher brackets may represent resource-rich nations or specialized
        manufacturing economies.
      </p>
    </div>

    <!-- Ridge Chart -->
    <div class="section__inner">
      <h3>Service-Dominated Economies Show Lower, Steadier Inflation but Greater Covid Impact</h3>
      <RidgeChart />
      <p>
        This ridge plot displays the evolution of annual inflation rates from 2015 to 2022 across two economic
        categories. Each year shows two overlapping density curves representing the distribution of inflation rates
        for countries dominated by <strong>Primary+Secondary sectors</strong> (orange) and those dominated by the
        <strong>Tertiary sector</strong> (blue). The density curves illustrate how inflation is distributed across
        countries within each category, with wider areas indicating more countries experiencing that inflation level.
        <strong>Note:</strong> The horizontal axis ranges from 0% to 20% to focus on typical inflation rates;
        countries with extreme inflation above 20% are not shown in the density curves.
      </p>
      <p>
        The visualization reveals distinct inflation patterns between the two economic categories. Countries dominated
        by <strong>primary and secondary sectors tend to experience higher and more variable inflation</strong> than
        tertiary-dominated economies. The orange curves often extend further to the right and show multiple peaks,
        suggesting that agriculture and manufacturing-based economies face greater price instability. In contrast,
        <strong>tertiary-dominated countries typically maintain lower, more stable inflation rates</strong>, with their
        blue curves concentrated at lower values. This pattern reflects how service-based economies, often more
        developed and with stronger institutional frameworks, tend to have better monetary policy control and more
        stable price environments. The temporal patterns also show spikes in certain years that affect both categories,
        likely reflecting global economic events such as commodity price shocks or pandemic-related disruptions.
      </p>
    </div>

    <!-- Violin Plot - Debt -->
    <div class="section__inner">
      <h3>Only Countries With Developed, Service-Based Economies Go Heavily Into Debt</h3>
      <ViolinPlotDebt />
      <p>
        This violin plot compares the distribution of national debt per capita between the two economic categories.
        Each violin shape represents the probability density of debt values, with wider sections indicating more
        countries at that debt level. Each bubble represents one country's average debt per capita across all available
        years (hover to see details). <strong>Note:</strong> This visualization includes 72 countries with available
        central government debt data from the World Bank—a subset of the 204 countries analyzed in other sections, as
        government debt reporting is less universally available than GDP data.
      </p>
      <p>
        The visualization reveals a striking difference in debt patterns. <strong>Tertiary-dominated countries
        carry significantly higher debt per capita</strong> than their primary+secondary counterparts. The purple
        violin extends much further upward and shows a broader distribution, indicating both higher average debt
        levels and greater variability among service-based economies. This reflects how developed, service-oriented
        economies typically have better access to international credit markets and possess the institutional capacity
        to manage larger public debts. In contrast, the brown violin for primary+secondary dominated countries is
        concentrated at lower values, suggesting that agriculture and manufacturing-based economies either have less
        access to credit or maintain more conservative fiscal policies due to revenue constraints and economic
        volatility.
      </p>
    </div>
  </section>
</template>
