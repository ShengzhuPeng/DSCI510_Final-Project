import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns

st.set_page_config(page_title="Music Market Analysis", layout="wide")
tabs = st.tabs(["Home", "Project Overview", "Datasets", "Analysis & Visualization"])

# Home tab
with tabs[0]:
    with open('Home.md', 'r') as file:
        content = file.read()
    st.markdown(content)

# Project Overview tab
with tabs[1]:   
    with open('Project.md', 'r') as file:
        content = file.read()
    st.markdown(content)
    
    
# Datasets tab
with tabs[2]:
    with open('Datasets.md', 'r') as file:
        content = file.read()
    st.markdown(content)
    st.image('Data_Pipeline.jpg', caption='Data Pipeline Visualization')

    st.header("Explore My Database")
    
    conn = sqlite3.connect('project_database.db')
    # Function to get data from a specific table
    def get_table_data(table_name):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        return df
    # Select box for user to choose table
    table_choice = st.selectbox(
        'Choose a table to display:',
        ['None', 'Songs Table', 'Artists Table', 'US Market Table', 'China Market Table']
    )

    # Conditional display of tables based on user selection
    if table_choice == 'Songs Table':
        st.header("Songs Table")
        songs_table = get_table_data('Songs')
        st.dataframe(songs_table)
        st.markdown("""
        - **Popularity_Score:** Reflecting the track's overall plays and recency, ranging from 0 to 100.
        - **Acousticness:** A measure indicating the acoustic nature of the song, on a scale from 0.0 to 1.0.
        - **Danceability:** An assessment of how suitable a track is for dancing, considering tempo, rhythm stability, and beat strength, scaled from 0.0 (least danceable) to 1.0 (most danceable).
        - **Energy:** A perceptual measure of intensity and activity in the track, ranging from 0.0 to 1.0, where higher values signify more energetic tracks.
        - **Instrumentalness:** The extent of instrumental content in the song.
        - **Speechiness:** The presence of spoken words in the track.
        - **Liveness:** Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live.
        - **Valence:** The musical positiveness conveyed by the track.
        """)
    elif table_choice == 'Artists Table':
        st.header("Artists Table")
        artists_table = get_table_data('Artists')
        st.dataframe(artists_table)
    elif table_choice == 'US Market Table':
        st.header("US Market Table")
        us_market_table = get_table_data('US_Market')
        st.dataframe(us_market_table)
    elif table_choice == 'China Market Table':
        st.header("China Market Table")
        china_market_table = get_table_data('China_Market')
        st.dataframe(china_market_table)

    # Close the database connection
    conn.close()
    


# Analysis & Visualization tab
with tabs[3]:
    with open('Analysis.md', 'r') as file:
        content = file.read()
    st.markdown(content)
    st.divider()
    # Sidebar for selecting the market
    market_choice = st.selectbox("Choose the market to display:", ["China", "United States", "Both"])


    # Function to fetch data from a CSV file - for Graph 1
    def fetch_data(market_csv):
        df = pd.read_csv(market_csv)
        # Function to handle incomplete dates
        def complete_date(date_str):
            try:
                # Try to convert the string to datetime with the full format
                return pd.to_datetime(date_str, format='%Y-%m-%d')
            except ValueError:
                # If there's a ValueError, it means the date string is not complete
                # We'll assume it's just the year and add January 1st to it
                return pd.to_datetime(date_str + '-01-01')
            
        # Apply the complete_date function to the 'release_date' column
        df['release_date'] = df['release_date'].apply(complete_date)
        
        # Extract the year from the release_date and create a 'year' column
        df['year'] = df['release_date'].dt.year
        
        return df
    
    # Function for graph 2
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
    
    audio_features = [
    'danceability', 'energy', 'loudness',
    'speechiness', 'acousticness', 'instrumentalness',
    'liveness', 'valence']

    # Function for graph 5
    conn = sqlite3.connect('project_database.db')
    # count the number of distinct artists in the China market
    artist_diversity_query_china = """
        SELECT COUNT(DISTINCT artist_id) AS distinct_artist_count
        FROM China_Market;
        """
    artist_diversity_result_china = pd.read_sql_query(artist_diversity_query_china, conn)
    artist_diversity_china = artist_diversity_result_china['distinct_artist_count'].iloc[0]

    # count the number of distinct artists in the US market
    artist_diversity_query_us = """
        SELECT COUNT(DISTINCT artist_id) AS distinct_artist_count
        FROM US_Market;
        """
    artist_diversity_result_us = pd.read_sql_query(artist_diversity_query_us, conn)
    artist_diversity_us = artist_diversity_result_us['distinct_artist_count'].iloc[0]
    conn.close()
   

    if market_choice == "United States":
        # Load the data for the United States market
        us_data = fetch_data('us_market_analysis.csv')
        us_year_count = us_data['year'].value_counts().sort_index()

        # Graph 1
        st.header("Distribution of Hit Songs Released Years")
        st.bar_chart(us_year_count)
        st.write("")

        # Add a 'season' column to the DataFrame
        us_data['season'] = us_data['release_date'].dt.month.apply(get_season) 
        # Count the number of songs released in each season
        season_count = us_data['season'].value_counts().sort_index()

        # Graph 2
        st.header("Seasonality Distribution of Hit Song Releases")
        st.bar_chart(season_count)
        
        # Graph 3
        st.header("Distribution of Popularity Scores")
        # Prepare the data by counting the occurrences of each score and sorting by index
        popularity_distribution = us_data['popularity_score'].value_counts().sort_index()
        # Create a DataFrame for the line chart
        popularity_df = pd.DataFrame({
            'Popularity Score': popularity_distribution.index,
            'Number of Songs': popularity_distribution.values
        })
        # Display the line chart using Streamlit's native function
        st.line_chart(popularity_df.set_index('Popularity Score'))

        # Load the data for the United States market
        us_data = pd.read_csv('us_market_analysis.csv')
        # Sidebar for feature selection
        selected_feature = st.selectbox(
            "Which Audio Feature do you want to explore?",
            audio_features
        )
        # Graph 4
        st.title("Audio Feature vs. Popularity Score")
        if selected_feature:
            # Create a scatter plot
            fig = st.scatter_chart(
                us_data, x='popularity_score', y=selected_feature)
            # Display the scatter plot

        # Graph 5
        st.title("Artist Diversity in the US Market")
        conn = sqlite3.connect('project_database.db')
        # SQL query to count distinct artists and songs in the US market
        query = """
        SELECT 
            (SELECT COUNT(DISTINCT artist_id) FROM US_Market) AS distinct_artist_count,
            (SELECT COUNT(DISTINCT song_id) FROM US_Market) AS distinct_song_count;
        """
        result = pd.read_sql_query(query, conn)
        result.columns = ['Number of Distinct Artists', 'Number of Songs']
        conn.close()
        st.table(result)

    elif market_choice == "China":
        china_data = fetch_data('China_market_analysis.csv')
        china_year_count = china_data['year'].value_counts().sort_index()
        #Graph 1
        st.header("Distribution of Hit Songs Released Years")
        st.bar_chart(china_year_count)
        china_data['season'] = china_data['release_date'].dt.month.apply(get_season) 
        season_count = china_data['season'].value_counts().sort_index()

        #Graph 2
        st.header("Seasonality Distribution of Hit Song Releasest")
        st.bar_chart(season_count)

        #Graph 3
        st.header("Distribution of Popularity Scores")
        popularity_distribution = china_data['popularity_score'].value_counts().sort_index()
        popularity_df = pd.DataFrame({
            'Popularity Score': popularity_distribution.index,
            'Number of Songs': popularity_distribution.values
        })
        st.line_chart(popularity_df.set_index('Popularity Score'))

        #Graph 4
        selected_feature = st.selectbox(
            "Which Audio Feature do you want to explore?",
            audio_features
        )

        st.title("Audio Feature vs. Popularity Score")
        if selected_feature:
            fig = st.scatter_chart(
                china_data, x='popularity_score', y=selected_feature)
            
        #Graph 5
        st.title("Artist Diversity in the China Market")
        conn = sqlite3.connect('project_database.db')
        # SQL query to count distinct artists and songs in the US market
        query = """
        SELECT 
            (SELECT COUNT(DISTINCT artist_id) FROM China_Market) AS distinct_artist_count,
            (SELECT COUNT(DISTINCT song_id) FROM China_Market) AS distinct_song_count;
        """
        result = pd.read_sql_query(query, conn)
        result.columns = ['Number of Distinct Artists', 'Number of Songs']
        conn.close()
        st.table(result)


    elif market_choice == "Both":
        # Load the data for both markets
        us_data = fetch_data('us_market_analysis.csv')
        china_data = fetch_data('china_market_analysis.csv')

        # Combine the dataframes and differentiate by market
        us_data['market'] = 'US'
        china_data['market'] = 'China'
        combined_data = pd.concat([us_data, china_data])
        
        #Graph 1
        st.header("Distribution of Hit Songs Released Years")
        release_years_combined = combined_data.groupby(['year', 'market']).size().unstack(fill_value=0)
        st.bar_chart(release_years_combined)
        st.write("""The majority of hit songs in both markets are recent releases from 2022 and 2023.
                 US market demonstrates a broader range, with enduring popularity for songs dating back to 1957 and 1964. 
                 This pattern reflects a receptiveness to older classics alongside contemporary hits, 
                 in contrast to the Chinese market's focus on more recent releases   
                 """)
       

        #Graph 2
        combined_data['season'] = combined_data['release_date'].dt.month.apply(get_season)
        st.header("Seasonality Distribution of Hit Song Releases")
        season_count_combined = combined_data.groupby(['season', 'market']).size().unstack(fill_value=0)
        st.bar_chart(season_count_combined)
        st.write ("""A higher number of hit songs were released during the Spring season in the US market and summer in the Chinese market
                 """)

        
        #Graph 3
        st.header("Distribution of Popularity Scores")
        popularity_distribution_combined = combined_data.groupby(['popularity_score', 'market']).size().unstack(fill_value=0)
        st.line_chart(popularity_distribution_combined)
        st.write("""The distribution of popularity scores within the US market shows a noticeable spike within the high score range;
                 The Chinese market's distribution is more uniform across a wide range, 
                 which may be attributed to a substantial proportion of missing data in popularity scores   
                 """)


        #Graph 4
        st.title("Audio Feature vs. Popularity Score - Both Markets")
        selected_feature = st.selectbox(
            "Which Audio Feature do you want to explore?",
            audio_features
        )
        if selected_feature:
            # Create a new DataFrame for US data with popularity score and the selected audio feature
            us_chart_data = us_data[['popularity_score', selected_feature]].rename(
                columns={'popularity_score': 'Popularity Score', selected_feature: 'Audio Feature Value'}
            )
            us_chart_data['Market'] = 'US'  # Add a column for market

            # Create a new DataFrame for China data with popularity score and the selected audio feature
            china_chart_data = china_data[['popularity_score', selected_feature]].rename(
                columns={'popularity_score': 'Popularity Score', selected_feature: 'Audio Feature Value'}
            )
            china_chart_data['Market'] = 'China'  # Add a column for market

            # Concatenate the US and China data
            combined_chart_data = pd.concat([us_chart_data, china_chart_data])
            
            # Create a scatter chart using the combined data
            st.scatter_chart(combined_chart_data, x='Popularity Score', y='Audio Feature Value', color='Market')

        st.write("""The analysis of audio features in relation to popularity scores 
                 in both the US and China markets does not demonstrate a significant correlation, 
                 indicating that the audience's preferences are varied 
                 and not necessarily dependent on any single audio characteristic.  
                 """)
        
        us_audio_data = pd.read_csv('us_market_analysis.csv')
        china_audio_data = pd.read_csv('china_market_analysis.csv')
        # Calculate the average of each audio feature for both markets
        us_averages = us_audio_data[audio_features].mean()
        china_averages = china_audio_data[audio_features].mean()

        # Create a DataFrame to display the averages
        averages_df = pd.DataFrame({
    'Average of loudness': [china_averages['loudness'], us_averages['loudness']],
    'Average of speechiness': [china_averages['speechiness'], us_averages['speechiness']],
    'Average of acousticness': [china_averages['acousticness'], us_averages['acousticness']],
    'Average of instrumentalness': [china_averages['instrumentalness'], us_averages['instrumentalness']],
    'Average of liveness': [china_averages['liveness'], us_averages['liveness']],
    'Average of valence': [china_averages['valence'], us_averages['valence']],
    'Average of danceability': [china_averages['danceability'], us_averages['danceability']],
    'Average of energy': [china_averages['energy'], us_averages['energy']]}, index=['China', 'US'])

        # Display the DataFrame in Streamlit
        st.dataframe(averages_df)
        st.write(""""The comparative analysis of average audio feature values reveals a striking similarity 
                 between the popular songs in both the Chinese and US markets, as illustrated in the table above. 
                 This suggests that despite the cultural differences, there is a convergence in the audio characteristics 
                 of the songs that resonate with audiences in both regions, indicating a shared appeal in the musical elements of these hits."  
                 """)

       # Graph 5
        st.title("Comparing Artist Diversity in two Markets")
        artist_diversity_combined = pd.DataFrame({
            'Market': ['US', 'China'],
            'Distinct Artists': [artist_diversity_us, artist_diversity_china]
        })

        # Plot a pie chart
        fig, ax = plt.subplots(figsize=(3, 4))
        ax.pie(artist_diversity_combined['Distinct Artists'], labels=artist_diversity_combined['Market'], autopct='%1.1f%%', colors = ['#AEC7E8','#1F77B4'],textprops={'fontsize': 6})
        
        
        # Display the pie chart
        st.pyplot(fig)
        st.write("""Despite the dataset containing a slightly larger base for the Chinese market, 
                 with more songs included, the data reveals that the Chinese market has a significant greater diversity of artists. 
                 """)

    













