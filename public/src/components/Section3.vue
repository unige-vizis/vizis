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
      <h3>Service Sector Dominates Global Economies</h3>
      <Boxplot />
      <div>
        <p>
          The following boxplot visualizes the distribution of conflict event impacts across different sectors. Each box 
          represents the interquartile range (IQR) of impacts for a sector, with the line inside the box indicating the 
          median impact. The "whiskers" extend from the lower and upper quartiles to the minimum and maximum observed 
          values, showing the full range of data for each sector.
        </p>
        <p>
          The tertiary sector has the highest median value, indicating that most countries have a strong focus on services 
          and tertiary economic activities on average. The primary and secondary sectors both have low medians around 20%, 
          suggesting that agriculture, mining, and manufacturing play a smaller role in the overall economic structure of 
          most countries. It is also striking that the primary sector shows a long upper whisker, reaching a maximum share 
          of 60.86% in Somalia. A few countries still fall within these remarkably high shares for the primary sector, 
          with their economies essentially focused on subsistence. Tourism, on the other hand, remains at a low level 
          overall, with a median of 2.78%. This shows that tourism plays a small part in the overall economy in most 
          countries and does not dominate even in countries often perceived as dependent on tourism. Tourism in this 
          chart is also included within the tertiary sector. 
        </p>
      </div>
    </div>

    <!-- Pyramid Chart -->
    <div class="section__inner">
      <h3>Richer Nations Tend to Rely on Services, Not Industry or Agriculture</h3>
      <PyramidChart />
      <p>
        This pyramid chart compares the distribution of GDP per capita between countries dominated by different economic
        sectors. Countries are categorized into two groups: those where the
        Primary and Secondary sectors (agriculture and manufacturing) together account for more than
        50% of the economy (shown in orange on the left), and those where the
        Tertiary sector (services) dominates with 50% or more (shown in blue on the right). The data
        represents the most recent year available for each country.
      </p>
      <p>
        The visualization reveals a clear pattern: countries dominated by tertiary (service) sectors are not only more 
        numerous but also tend to have higher GDP per capita overall. The tertiary-dominated countries show a broader 
        distribution across all income levels, with significant representation in the higher GDP brackets (20k-80k+ range). 
        In contrast, primary+secondary dominated countries are heavily concentrated in the lower GDP brackets (0-5k range), 
        with only a few, reaching higher income levels. This suggests that
        <ul>
          <li>Economic development and the transition to service-based economies are strongly correlated with higher national income levels.</li>
          <li>The few primary+secondary dominated countries in higher GDP brackets all have economies benefiting from oil and gas exports.</li>
        </ul>
      </p>
    </div>

    <!-- Ridge Chart -->
    <div class="section__inner">
      <h3>Service-Dominated Economies Show Lower, Steadier Inflation but Greater Covid Impact</h3>
      <RidgeChart />
      <p>
        This ridge plot displays the evolution of annual inflation rates from 2015 to 2022 across two economic
        categories. Each year shows two overlapping density curves representing the distribution of inflation rates for
        countries dominated by <strong>Primary+Secondary sectors</strong> (orange) and those dominated by the
        <strong>Tertiary sector</strong> (blue). The density curves illustrate how inflation is distributed across
        countries within each category, with wider areas indicating more countries experiencing that inflation level.
        <strong>Note:</strong> The horizontal axis ranges from 0% to 20% to focus on typical inflation rates; countries
        with extreme inflation above 20% are not shown in the density curves.
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
        This violin plot compares the distribution of national debt per capita between the two economic categories. Each
        violin shape represents the probability density of debt values, with wider sections indicating more countries at
        that debt level. Each bubble represents one country's average debt per capita across all available years (hover
        to see details). <strong>Note:</strong> This visualization includes 72 countries with available central
        government debt data from the World Bank—a subset of the 204 countries analyzed in other sections, as government
        debt reporting is less universally available than GDP data.
      </p>
      <p>
        The visualization reveals a striking difference in debt patterns.
        <strong>Tertiary-dominated countries carry significantly higher debt per capita</strong> than their
        primary+secondary counterparts. The purple violin extends much further upward and shows a broader distribution,
        indicating both higher average debt levels and greater variability among service-based economies. This reflects
        how developed, service-oriented economies typically have better access to international credit markets and
        possess the institutional capacity to manage larger public debts. In contrast, the brown violin for
        primary+secondary dominated countries is concentrated at lower values, suggesting that agriculture and
        manufacturing-based economies either have less access to credit or maintain more conservative fiscal policies
        due to revenue constraints and economic volatility.
      </p>
    </div>
  </section>
</template>
