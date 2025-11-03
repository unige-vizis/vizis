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
    </div>
    <BarChart />
    <div class="section__inner">
      <p>
       This chart shows where the most conflict events were recorded over the last 10 years. In itself it is not very insightful, hiding a lot of the specifics of these conflicts and even factors like population size, which is why we offer a normalized version of this plot as well. 7 countries are highlighted in yellow, because they vary a lot in their conflict patterns and will be representative examples to guide further analysis and discussion.
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
        <li>Tourism data from UN Tourism - sometimes incomplete and from a different source than sector data.
        Its inclusion into the third sector might introduce slight imprecisions</li>
      </ul>

      <p>
       Our focus is how a country's economic situation influences or at the very least correlates with the types of and frequency of conflict events. This plot shows the previously highlighted countries of interest and their strongly differing economic compositions.
      </p>

    </div>

    <!-- Grouped Bar Chart -->
    <div class="section__inner">
      <h3>What Conflict Events occur in our Countries of Interest?</h3>
      <p>Comparison of event types for the same 7 highlighted countries from the charts above. Protests and riots are grouped together, with Strategic developments being left out for clearer analysis.</p>
    </div>
    <GroupedBarChart />

    <div class="section__inner">
      <p>
        Connecting this with our findings from the previous chart we obtain a better idea about our countries' true conflict character and start to make note of some trends.
      </p>

      <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
        <thead>
          <tr style="border-bottom: 2px solid #ccc;">
            <th style="text-align: left; padding: 0.5rem;">Country</th>
            <th style="text-align: left; padding: 0.5rem;">Economy</th>
            <th style="text-align: left; padding: 0.5rem;">Conflict Type</th>
            <th style="text-align: right; padding: 0.5rem;">Fatalities</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>Somalia</strong></td>
            <td style="padding: 0.5rem;">Subsistence economy (61% Primary)</td>
            <td style="padding: 0.5rem;">Failed state dynamics (Battles & Violence against civilians)</td>
            <td style="text-align: right; padding: 0.5rem;">~51,000</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>Afghanistan</strong></td>
            <td style="padding: 0.5rem;">Traditional rural economy (42% Primary)</td>
            <td style="padding: 0.5rem;">Insurgency warfare (61% Battles)</td>
            <td style="text-align: right; padding: 0.5rem;">202,145</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>India</strong></td>
            <td style="padding: 0.5rem;">Developing industry (22% Primary, 23% Secondary, 55% Tertiary)</td>
            <td style="padding: 0.5rem;">Democratic mobilization (76% Protests & Riots)</td>
            <td style="text-align: right; padding: 0.5rem;">12,189</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>Ukraine</strong></td>
            <td style="padding: 0.5rem;">Modern service economy (70% Tertiary, 19% Primary)</td>
            <td style="padding: 0.5rem;">Modern interstate warfare (64% Explosions/Remote violence)</td>
            <td style="text-align: right; padding: 0.5rem;">137,716</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>Mexico</strong></td>
            <td style="padding: 0.5rem;">Middle-income service economy with tourism (61% Tertiary, 8.5% tourism)</td>
            <td style="padding: 0.5rem;">Cartel violence (40% Violence against civilians, Protests)</td>
            <td style="text-align: right; padding: 0.5rem;">57,520</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;"><strong>United States</strong></td>
            <td style="padding: 0.5rem;">Advanced post-industrial (81% Tertiary, 4% Primary)</td>
            <td style="padding: 0.5rem;">slightly violent civil unrest (Protests & Riots)</td>
            <td style="text-align: right; padding: 0.5rem;">440</td>
          </tr>
          <tr>
            <td style="padding: 0.5rem;"><strong>Italy</strong></td>
            <td style="padding: 0.5rem;">Advanced industrial economy with tourism (72% Tertiary, 5.7% tourism)</td>
            <td style="padding: 0.5rem;">Mostly peaceful protests.</td>
            <td style="text-align: right; padding: 0.5rem;">2</td>
          </tr>
        </tbody>
      </table>

      <p>
        <strong>Key Finding:</strong> It is specific conditions, that drive each country's conflict character for the most part. Modern warfare in Ukraine, cartel violence in Mexico. Nevertheless a broader trend emerges: countries with less developed, resource-focused economies (Afghanistan, Somalia) experience more violent conflict, while highly developed tertiary-sector economies tend toward peaceful protesting. Italy exemplifies this with 24,524 conflict events but only 2 recorded fatalities over 10 years.
      </p>
    </div>

    <!-- Heatmap -->
    <div class="section__inner">
      <h3>Temporal Distribution of Event Types (2015-2024)</h3>
      <p>
        Dual-metric visualization showing both event frequency (purple, top) and fatalities (red, bottom) for each conflict type and year. The horizontal split reveals whether high event counts correlate with high death tolls or if certain event types are deadlier than others.
      </p>
    </div>
    <Heatmap />

    <div class="section__inner">
      <p>
        We zoom out now a bit and focus more on the types of conflicts in general, not relating them to specific countries anymore. This plot confirms a concern that many people share, in that conflicts, of all kinds and especially violent ones are becoming more frequent and more deadly. Especially notable is the increase in Battle Fatalities, Violence against civilians and also the drastic increase in Protests.
      </p>
    </div>

    <!-- Waffle Chart: Economic Sectors by Event Type -->
    <div class="section__inner">
      <h3>Averaged Economic Context by Event Type</h3>
      <p>
         This small multiple waffle plot depicts the average economic context each event type occurs in. Once more we identify the noticeable trend of more violent conflict in lower developed economies irrespective of specific countries.
      </p>
    </div>
    <WaffleChartSectors />

    <div class="section__inner">
      <p>
        [Analysis text about economic patterns by event type will go here. Notable findings from left to right: Battles show the highest Primary sector (29.04%), indicating they occur more in countries dependent on agriculture and natural resources. Protests show the lowest Primary sector (16.21%) and highest Tertiary sector (63.06%), suggesting they occur more in service-based economies. This gradient from primary-heavy to tertiary-heavy economies reveals how economic structure correlates with conflict types.]
      </p>

      <h3>Conclusion</h3>
      <p>
        [Concluding remarks synthesizing the findings from all visualizations and their implications for understanding
        religion's role in geopolitical conflicts and human suffering.]
      </p>
    </div>
  </section>
</template>
