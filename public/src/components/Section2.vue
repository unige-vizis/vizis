<script setup>
import BarChart from './visualizations/BarChart.vue'
import GroupedBarChart from './visualizations/GroupedBarChart.vue'
import Heatmap from './visualizations/Heatmap.vue'
import StackedBarChart from './visualizations/StackedBarChart.vue'
import WaffleChartSectors from './visualizations/WaffleChartSectors.vue'
</script>

<template>
  <section>
    <!-- Bar Chart -->
    <div class="section__inner">
      <h3>Countries with the most recorded conflict events</h3>
      <BarChart />
      <p>
        This chart shows where the most conflict events were recorded over the last 10 years. In addition, we provide a
        normalized version that shows the number of events per 100000 inhabitants, to account for population size
        differences. In the following section we will focus on the seven highlighted countries. These seven countries
        vary a lot in their conflict patterns and will be representative examples to guide further analysis and
        discussion.
      </p>
    </div>

    <!-- 100% Stacked Bar Chart -->
    <div class="section__inner">
      <h3>Economic Sector Composition of Highlighted Conflict Countries</h3>
      <StackedBarChart />
      <p><strong>Note:</strong> Economic sector percentages are calculated from World Bank GDP data</p>
      <ul>
        <li>Primary sector: Agriculture, Hunting, Forestry, Fishing, Mining, Utilities (ISIC A-C+E)</li>
        <li>Secondary sector: Manufacturing, Construction (ISIC D+F)</li>
        <li>Tertiary sector: Wholesale, Gastronomy, Transport, Communication, Other (ISIC G-P)</li>
        <li>
          Tourism data from UN Tourism - sometimes incomplete and from a different source than sector data. Its
          inclusion into the third sector might introduce slight imprecisions
        </li>
      </ul>
      <p>
        Let's first take a look at how the four sectors are represented in each of the seven countries. Almost every
        country dominates in the tertiary sector. Only <strong>Afghanistan and Somalia</strong> have a majority in the
        primary sector, which indicates a more subsistence-based economy. <strong>India</strong> has a more balanced
        distribution, with a significant secondary sector share, indicating a developing industrial economy. Tourism
        plays a notable role in <strong>Mexico and Italy</strong>, which could influence their economic stability and
        conflict dynamics. The <strong>States and Ukraine</strong> have highly developed service economies, which shows
        their advanced economic status.
      </p>
    </div>

    <!-- Grouped Bar Chart -->
    <div class="section__inner">
      <h3>What Conflict Events occur in our Countries of Interest?</h3>
      <GroupedBarChart />
      <p>
        This chart provides insight into the types of conflict events that predominate in each of our seven highlighted
        countries. Protests and riots are grouped together, while strategic developments are excluded because of limited
        data. As you can see, different countries exhibit distinct conflict profiles. For instance,
        <strong>Afghanistan and Somalia</strong> show a high prevalence of battles and explosions/remote violence,
        indicating ongoing armed conflicts and instability. In contrast,
        <strong>India and the United States</strong> have a significant number of protests and riots, reflecting social
        and political unrest. <strong>Ukraine</strong> is characterized by a high number of explosions/ remote violence,
        likely due to the ongoing conflict in the region. <strong>Mexico</strong> displays a mix of violence against
        civilians and protests, highlighting issues related to organized crime and social movements.
      </p>
    </div>

    <div class="section__inner">
      <p>
        Connecting this with our findings from the previous chart we obtain a better idea about our countries' true
        conflict character and start to make note of some trends.
      </p>

      <div class="table">
        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
          <thead>
            <tr>
              <th>Country</th>
              <th>Economy</th>
              <th>Conflict Type</th>
              <th>Fatalities</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Afghanistan</strong></td>
              <td>Traditional rural economy (42% Primary)</td>
              <td>Insurgency warfare (61% Battles)</td>
              <td>202145</td>
            </tr>
            <tr>
              <td><strong>Ukraine</strong></td>
              <td>Modern service economy (70% Tertiary, 19% Primary)</td>
              <td>Modern interstate warfare (64% Explosions/Remote violence)</td>
              <td>137716</td>
            </tr>
            <tr>
              <td><strong>Mexico</strong></td>
              <td>Middle-income service economy with tourism (61% Tertiary, 8.5% tourism)</td>
              <td>Cartel violence (40% Violence against civilians, Protests)</td>
              <td>57520</td>
            </tr>
            <tr>
              <td><strong>Somalia</strong></td>
              <td>Subsistence economy (61% Primary)</td>
              <td>Failed state dynamics (Battles & Violence against civilians)</td>
              <td>~51000</td>
            </tr>
            <tr>
              <td><strong>India</strong></td>
              <td>Developing industry (22% Primary, 23% Secondary, 55% Tertiary)</td>
              <td>Democratic mobilization (76% Protests & Riots)</td>
              <td>12189</td>
            </tr>
            <tr>
              <td><strong>United States</strong></td>
              <td>Advanced post-industrial (81% Tertiary, 4% Primary)</td>
              <td>Slightly violent civil unrest (Protests & Riots)</td>
              <td>440</td>
            </tr>
            <tr>
              <td><strong>Italy</strong></td>
              <td>Advanced industrial economy with tourism (72% Tertiary, 5.7% tourism)</td>
              <td>Mostly peaceful protests.</td>
              <td>2</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>
        <strong>Key Finding:</strong> Specific conditions largely determine each country's conflict character. For
        example, modern warfare in Ukraine, cartel violence in Mexico illustrate different drivers. Nevertheless a
        broader trend emerges: countries with less developed, resource-focused economies (Afghanistan, Somalia)
        experience more violent conflict, while highly developed tertiary-sector economies tend toward peaceful
        protesting. Italy exemplifies this with 24524 conflict events but only 2 recorded fatalities over 10 years.
      </p>
    </div>

    <!-- Heatmap -->
    <div class="section__inner">
      <h3>Temporal Distribution of Event Types (2015-2024)</h3>
      <p class="subtitle">Cumulative data across the highlighted countries.</p>
      <div class="">
        <h4>Event Frequency by Event Type and Year</h4>
        <Heatmap :show="'events'" :y_labels="true" />
        <h4>Fatalities by Event Type and Year</h4>
        <Heatmap :show="'fatalities'" :y_labels="true" />
      </div>
      <p>
        Now let's have a look into the details. These two heatmap show the distribution of event types over time in
        terms of event counts and fatalities. The top heatmap illustrates the frequency of different conflict event
        types from 2015 to 2024, while the bottom heatmap displays the corresponding fatalities associated with each
        event type. Notably, we observe a significant increase in both the number of events and fatalities over the
        years, with a tip in 2022, likely attributable to the escalation of the conflict in Ukraine. The data reveals
        that "Explosions/Remote violence" and "Battles" are the most frequent event types, with "Explosions/Remote
        violence" also accounting for the highest fatalities.
      </p>
      <p>
        With this chart we zoom out a bit to look at the bigger picture. By focusing more on the types of conflicts in
        general and not relating them to specific countries we can illustrate a concern, that many people share:
        conflicts, of all kinds and especially violent ones, are becoming more frequent and more deadly. Especially
        notable is the increase in battle fatalities, violence against civilians and also the drastic increase in
        protests.
      </p>
    </div>

    <!-- Waffle Chart: Economic Sectors by Event Type -->
    <div class="section__inner">
      <h3>Averaged Economic Context by Event Type</h3>
      <WaffleChartSectors />
      <p>
        This small multiple waffle plot depicts the average economic context each event type occurs in. Once again we
        identify the noticeable trend of more violent conflict in less-developed economies, regardless of specific
        countries.
      </p>
    </div>

    <div class="section__inner">
      <h3>Economic Patterns by Event Type</h3>
      <p>
        The data shows a clear gradient connecting economic structure and conflict form. Battles occur mostly in
        primary-sector economies (29.0%), where dependence on agriculture and extraction correlates with higher levels
        of organized violence. Explosions and violence against civilians follow similar patterns. In contrast, protests
        are concentrated in tertiary-sector economies (63.1%), where political disputes tend to manifest through
        collective action rather than warfare. As economies shift from resource-based to service-oriented, conflict
        expression transitions from violent confrontation to civic mobilization.
      </p>

      <h3>Conclusion</h3>
      <p>
        The combined data from ACLED and World Bank sources reveal a clear structural connection between economic
        composition and conflict dynamics. Countries with large primary sectors experience more frequent and deadly
        events, while service-based economies show higher rates of protest but significantly fewer fatalities. This
        gradient, consistent across all visualizations, demonstrates how development level and sector diversification
        influence not only the prevalence but also the form of violence. As economies move from resource dependence
        toward industrial and service diversification, conflict tends to shift from armed confrontation to civic
        mobilization. Visualizing these patterns makes visible how economic structures shape collective stability,
        vulnerability, and the evolving character of global conflict. Religion, in this context, is not an isolated
        cause of violence but one of the many human frameworks through which economic and political realities are
        experienced and contested. Recognizing this interplay allows for a more integrated understanding of geopolitical
        conflict that connects data, structure, and the lived experience of suffering.
      </p>
    </div>
  </section>
</template>
