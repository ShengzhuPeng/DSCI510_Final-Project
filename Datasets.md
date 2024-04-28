
### 📎 DATA SOURCE 1: Spotify API
**Link to API:** [Spotify Web API](https://developer.spotify.com/documentation/web-api)

**Description:**  
The Spotify Web API enables the creation of applications that can interact with Spotify's streaming service and retrieve metadata from Spotify content. It provides a rich dataset encompassing various aspects of music tracks, artists, albums, and user data. Key features accessible through this API include detailed track information such as genre, popularity scores, and audio features like danceability, energy, acousticness, etc.

### 📎 DATA SOURCE 2: Billboard Hot 100 Year-End Charts
**Link to Website:** [Billboard Hot 100 Year-End Charts](https://www.billboard.com/charts/year-end/hot-100-songs/)

**Description:**  
The Billboard Hot 100 Year-End Charts encapsulate the annual summary of the most popular tracks in the United States, determined by sales, radio play, and online streaming data. It is a well-structured webpage that contains the names of 100 tracks, the names of the artists, and their ranks (1-100). This data source will serve as a crucial dataset for identifying and evaluating the top Western music tracks, providing a US-centric perspective on popular music trends.

### 📎 DATA SOURCE 3: Netease Music - Western Songs Hit Chart
**Link to Website:** [Netease Music - Western Songs Hit Chart](https://music.163.com/#/discover/toplist?id=2809513713)

**Description:**  
Netease Music is one of the most popular music streaming platforms in China, offering a vast collection of songs across various genres to its users. The "Western Songs Hit Chart'' on Netease Music is a weekly updated list showcasing the 200 most popular Western English songs among Chinese audiences. This well-structured web page provides essential information for each track, including the track name, song length, artist name, and rank. Utilizing this data source will allow for an insightful comparison of popular Western music trends between the US and Chinese markets, highlighting differences and similarities in musical preferences across these distinct cultural landscapes. 

> **Note:** Given the limited resources and the restrictions associated with the lack of comprehensive APIs in China, this is the most accessible and reliable source for capturing the preferences of the Chinese market in Western music.

### My Data Pipeline

To acquire and model my data, I performed web scraping on two top-song lists, yielding 300 songs, from which track names and artist names were extracted. These were initially stored in separate CSV files, as detailed in the `billboard.py` and `netease.py` scripts, resulting in two processed files: `billboard_year_end_hot_100.csv` and `netease_music_toplist_updated.csv`.

In the main script, `main.py`, I established communication with the Spotify API to enrich my data model by converting track and artist names into unique Spotify identifiers (song_id and artist_id). This allowed me to retrieve comprehensive track details such as popularity scores, release dates, and other audio features. My data is structured in a relational database model, encompassing tables for songs, artists, and market-specific data for the U.S. and China, all managed using the SQLite library. This setup ensures that new attributes can be seamlessly integrated by adding fields to the existing tables.

