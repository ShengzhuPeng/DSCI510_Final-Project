# Objective
The objective of this project is to **explore the differences in preferences for popular Western music between audiences in China and the United States.**

This analysis will utilize the Billboard Top 100 year-end charts (2023) to represent the US market and the Top Western songs on Netease Music for the Chinese market, employing the Spotify API as a unified standard to assess track popularity and audio feature metrics across both markets.

# Findings

- The majority of hit songs in both markets are recent releases from 2022 and 2023. However, **the US market demonstrates a broader range**, with enduring popularity for songs dating back to 1957 and 1964. This pattern reflects a receptiveness to older classics alongside contemporary hits, in contrast to the Chinese market's focus on more recent releases.
- A higher number of hit songs were released during the **Spring season** in the US market and **Summer season** in the Chinese market.
- The distribution of popularity scores within the US market shows **a noticeable spike within the high score range**; The Chinese market's distribution is **more uniform across a wide range**, which may be attributed to a substantial proportion of missing data in popularity scores.
- The analysis of audio features in relation to popularity scores in both the US and China markets **does not demonstrate a significant correlation**, indicating that the audience's preferences are varied and not necessarily dependent on any single audio characteristic.
- In assessing artist diversity within the top song lists, **the Chinese market exhibits a broader array of artists**.

# Reflection
One significant challenge encountered during the project was in the data collection phase. The Netease Music Chart web pages dynamically load content, which rendered conventional scraping methods like Beautiful Soup or Requests ineffective. This issue was overcome by employing Selenium, a tool that emulates browser interactions to render and capture the necessary data.

A second challenge was navigating data visualization. Although a relational database provided a structured and robust data storage solution, it introduced complexity into the visualization query process, often resulting in intricate and unwieldy code. To enhance the efficiency of data analysis and visualization within the web application, I transferred the database content into two separate CSV files— `China_market_analysis.csv` and `us_market_analysis.csv`. This simplification allowed for more straightforward and less code-intensive interactions with the data.

# What’s Next?
To propel this project to its next phase, I have envisioned three ways:
- **Time-dimension Extension:** By augmenting the dataset to include annual top songs from 2000 through 2022, the study could explore evolving trends and shifts in music preferences over time, offering a historical perspective on how tastes have transformed across decades.
- **Market Diversification:** Broadening the scope to incorporate music data from additional markets such as Europe and Korea could provide a more comprehensive global analysis. This would allow the project to identify unique regional musical tastes and compare them against the existing US and Chinese data.
- **Audio Feature Enrichment:** Currently relying on Spotify's API for standardized metrics, the project could benefit from integrating Apple Music's API. This would introduce new features like genre classification and other musical metrics, thereby enriching the audio feature analysis and offering a more layered understanding of the songs' characteristics and their impact on popularity.
