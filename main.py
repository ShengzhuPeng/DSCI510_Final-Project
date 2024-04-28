# This script serves as the main module for interacting with the Spotify API.
# It is responsible for fetching and processing data from Spotify, such as 
# retrieving track IDs, artist IDs, and additional track details 
# The script also handles the creation and maintenance of the data model, 
# ensuring that all fetched data is systematically stored in the project's 
# database, facilitating easy access and analysis for future processes.

from dotenv import load_dotenv
import os
import base64
import requests
import json
import pandas as pd
import sqlite3

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#Get Token Function
def get_token(client_id, client_secret):
    auth_string = client_id + ":" + client_secret

    # Encode the authentication string to bytes, then to Base64
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    # The endpoint for requesting an access token
    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    # Making the POST request
    result = requests.post(url, headers=headers, data=data)

    # Load the result content into a dictionary
    json_result = json.loads(result.content)

    # Extract the access token from the JSON response
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}



#Create a database and Artists table
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Artists (
        artist_id TEXT PRIMARY KEY,
        artist_name TEXT NOT NULL
    )
    ''')
conn.commit()
conn.close()



#Get Artist_id using single artist_name
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    else:
        artist_id = json_result[0]['id']
        #print(f"Artist '{artist_name}' has the ID: {artist_id}")
        return artist_id

#Get Artist_id using csv file   
def get_artist_ids_from_csv(csv_file_path, db_file_path):
  # Read the CSV and make sure 'Artist_name' is treated as a string
    df = pd.read_csv(csv_file_path, dtype={'Artist_name': str})
    
    # Establish a connection to the database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
 
    # Split artist names by comma and create a set to avoid duplicate searches
    unique_artists = set()
    for artists in df['Artist_name'].dropna():  # Drop rows where 'Artist_name' is NaN
        # Check for non-empty strings after stripping whitespace
        if isinstance(artists, str) and artists.strip():
            for artist_name in artists.split(','):
                # Add the stripped artist name to the set
                unique_artists.add(artist_name.strip())

    # Search for each unique artist and get their ID
    for artist_name in unique_artists:
        # Skip empty artist names
        if artist_name:
            artist_id = search_for_artist(token, artist_name)
            if artist_id:
                # Insert the artist into the database, or ignore if it already exists
                cursor.execute('''
                INSERT OR IGNORE INTO Artists (artist_id, artist_name)
                VALUES (?, ?)
                ''', (artist_id, artist_name))
    conn.commit()
    conn.close()  


token = get_token(client_id, client_secret)
csv_file_path = 'billboard_year_end_hot_100.csv'
db_file_path = 'project_database.db'
get_artist_ids_from_csv(csv_file_path, db_file_path)

#Create Songs table
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute(''' CREATE TABLE IF NOT EXISTS songs (
                                        song_id TEXT PRIMARY KEY,
                                        track_name TEXT NOT NULL
                                    ); ''')
conn.commit()
conn.close()


# Get track_id using single track_name
def get_track_id(token, track_name):
    # Base URL for Spotify search API
    url = "https://api.spotify.com/v1/search"
    # Query parameters: track name (and artist if provided)
    query = f"track:{track_name}"
    # Construct the full query URL
    query_url = f"{url}?q={query}&type=track&limit=1"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(query_url, headers=headers)
    response_json = response.json()
    
    # Extract track ID from the response
    items = response_json.get('tracks', {}).get('items', [])
    if items:
        # Assuming the first track is the one we want
        track_id = items[0].get('id')
        return track_id
    else:
        return None
    
# Get track_id using csv
def get_track_ids_from_csv(csv_file_path, db_file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Authenticate with Spotify
    token = get_token(client_id, client_secret)
    
    # Connect to SQLite database
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        # Iterate over unique track names and insert them into the database
        for track_name in df['Track_name'].unique():
            track_id = get_track_id(token, track_name)
            if track_id:
                cursor.execute('INSERT OR IGNORE INTO songs (song_id, track_name) VALUES (?, ?)', (track_id, track_name))
        
        conn.commit()
        print(f"Inserted {cursor.rowcount} records to the songs table.")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

token = get_token(client_id, client_secret)
csv_file_path = 'billboard_year_end_hot_100.csv'
db_file_path = 'project_database.db'
get_track_ids_from_csv(csv_file_path, db_file_path)


#Create US Market Table
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS US_Market (
    us_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES Songs(song_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);
""")
conn.commit()
conn.close()



def insert_song_artist_relationship_US(csv_file_path, db_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        track_name = row['Track_name']
        artist_names = row['Artist_name'].split(',')

        # Find the song_id from the Songs table using track_name
        cursor.execute("SELECT song_id FROM Songs WHERE track_name = ?", (track_name,))
        song_result = cursor.fetchone()
        if song_result:
            song_id = song_result[0]

            # For each artist, find the artist_id from the Artists table
            for artist_name in artist_names:
                artist_name = artist_name.strip()
                cursor.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
                artist_result = cursor.fetchone()
                
                # If both song_id and artist_id are found, insert the relationship into US_Market table
                if artist_result:
                    artist_id = artist_result[0]
                    cursor.execute("INSERT INTO US_Market (song_id, artist_id) VALUES (?, ?)", (song_id, artist_id))
        else:
            print(f"Song '{track_name}' not found in the Songs table.")

    conn.commit()
    conn.close()

csv_file_path = 'billboard_year_end_hot_100.csv'
db_file_path = 'project_database.db'
insert_song_artist_relationship_US(csv_file_path, db_file_path)

#Add new fields to Songs table: album_id, release_date, popuarity_score 
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute("ALTER TABLE Songs ADD COLUMN album_id TEXT")
cursor.execute("ALTER TABLE Songs ADD COLUMN release_date TEXT")
cursor.execute("ALTER TABLE Songs ADD COLUMN popularity_score INTEGER")
conn.commit()
conn.close()

def get_track_info(token, song_id):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"

    headers = get_auth_header(token)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        track_data = response.json()
        album_id = track_data['album']['id']
        release_date = track_data['album']['release_date']
        popularity_score = track_data['popularity']
        return album_id, release_date, popularity_score
    else:
        return None, None, None


def get_track_info_db(db_file_path, token):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    
    cursor.execute('''SELECT song_id FROM Songs WHERE album_id IS NULL''')
    songs_to_update = cursor.fetchall()
    
    for song_id in songs_to_update:
        song_id = song_id[0]  # Extract the ID from the tuple
        album_id, release_date, popularity_score = get_track_info(token, song_id)
        if album_id and release_date and popularity_score is not None:
            cursor.execute('''UPDATE Songs SET album_id = ?, release_date = ?, popularity_score = ? WHERE song_id = ?''',
                           (album_id, release_date, popularity_score, song_id))
    
    conn.commit()
    conn.close()

token = get_token(client_id, client_secret)
db_file_path = 'project_database.db'
get_track_info_db(db_file_path, token)

#Add new fields to Songs table: track audio features
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute("ALTER TABLE Songs ADD COLUMN danceability REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN energy REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN loudness REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN speechiness REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN acousticness REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN instrumentalness REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN liveness REAL;")
cursor.execute("ALTER TABLE Songs ADD COLUMN valence REAL;")
conn.commit()
conn.close()

# Function to get audio features for a single track
def get_track_audio_features(token, song_id):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        # If the response was not ok, print the error and return none
        print(f"Error fetching track audio features: {response.json()}")
        return None

    # If the response is ok, we parse it and return the audio features
    audio_features = response.json()
    return audio_features

# token = get_token(client_id, client_secret)
# song_id = '7K3BhSpAxZBznislvUMVtn'
# audio_features = get_track_audio_features(token, song_id)
# print(audio_features)


def get_track_audio_features_db(db_file_path, token):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        # Select songs where audio features are not yet fetched
        cursor.execute("SELECT song_id FROM Songs WHERE danceability IS NULL")
        songs_to_update = cursor.fetchall()

        for song_id in songs_to_update:
            song_id = song_id[0]  # Unpack tuple
            audio_features = get_track_audio_features(token, song_id)

            if audio_features:
                # Extract audio features
                # Update the song record with the new data
                # Make sure to handle potential None values for each feature with a fallback
                cursor.execute("""
                    UPDATE Songs
                    SET danceability = ?, energy = ?, loudness = ?, speechiness = ?, acousticness = ?, instrumentalness = ?, liveness = ?, valence = ?
                    WHERE song_id = ?
                """, (
                    audio_features.get('danceability', 0),
                    audio_features.get('energy', 0),
                    audio_features.get('loudness', 0),
                    audio_features.get('speechiness', 0),
                    audio_features.get('acousticness', 0),
                    audio_features.get('instrumentalness', 0),
                    audio_features.get('liveness', 0),
                    audio_features.get('valence', 0),
                    song_id
                ))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


token = get_token(client_id, client_secret)
db_file_path = 'project_database.db'
get_track_audio_features_db(db_file_path, token)

# All Billboard songs'data has added to database
# Then, Import Netease Data
# Import Data into Artists Table
token = get_token(client_id, client_secret)
csv_file_path = 'netease_music_toplist.csv'
db_file_path = 'project_database.db'
get_artist_ids_from_csv(csv_file_path, db_file_path)

#Import Data into Songs Table
token = get_token(client_id, client_secret)
csv_file_path = 'netease_music_toplist.csv'
db_file_path = 'project_database.db'
get_track_ids_from_csv(csv_file_path, db_file_path)

# Create China_Market table
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS China_Market (
    CHN_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES Songs(song_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id)
);
""")
conn.commit()
conn.close()


def insert_song_artist_relationship_CHI(csv_file_path, db_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        track_name = row['Track_name']
        artist_names = row['Artist_name'].split(',')

        # Find the song_id from the Songs table using track_name
        cursor.execute("SELECT song_id FROM Songs WHERE track_name = ?", (track_name,))
        song_result = cursor.fetchone()
        if song_result:
            song_id = song_result[0]

            # For each artist, find the artist_id from the Artists table
            for artist_name in artist_names:
                artist_name = artist_name.strip()
                cursor.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
                artist_result = cursor.fetchone()
                
                # If both song_id and artist_id are found, insert the relationship into China_Market table
                if artist_result:
                    artist_id = artist_result[0]
                    cursor.execute("INSERT INTO China_Market (song_id, artist_id) VALUES (?, ?)", (song_id, artist_id))
        else:
            print(f"Song '{track_name}' not found in the Songs table.")

    conn.commit()
    conn.close()


#Import Data into China Market table
csv_file_path = 'netease_music_toplist_updated.csv'
db_file_path = 'project_database.db'
insert_song_artist_relationship_CHI(csv_file_path, db_file_path)

#Import track_info data
token = get_token(client_id, client_secret)
db_file_path = 'project_database.db'
get_track_info_db(db_file_path, token)


#Import track_audio feature
token = get_token(client_id, client_secret)
db_file_path = 'project_database.db'
get_track_audio_features_db(db_file_path, token)



# import data as CSV for visualization purpose
# US_market analysis csv
conn = sqlite3.connect('/Users/shengzhupeng/Desktop/DSCI510_FinalProject/project_database.db')
# Define the query to get the necessary data for the US market analysis
us_market_query = """
SELECT  
    s.track_name, 
    s.popularity_score, 
    s.release_date, 
    s.danceability, 
    s.energy, 
    s.loudness, 
    s.speechiness, 
    s.acousticness, 
    s.instrumentalness, 
    s.liveness, 
    s.valence
FROM 
    Songs s
JOIN 
    US_Market um ON s.song_id = um.song_id
JOIN 
    Artists a ON um.artist_id = a.artist_id
GROUP BY 
    s.song_id;
"""

try:
    # Execute the query and load into a DataFrame
    us_market_df = pd.read_sql_query(us_market_query, conn)
    print("Query executed successfully, DataFrame is populated.")
except Exception as e:
    print(f"An error occurred during the query: {e}")
try:
    us_market_df.to_csv('us_market_analysis.csv', index=False)
    print("CSV file created successfully.")
except Exception as e:
    print(f"An error occurred while writing the CSV file: {e}")

conn.close()

# China_market analysis csv
conn = sqlite3.connect('/Users/shengzhupeng/Desktop/DSCI510_FinalProject/project_database.db')
China_market_query = """
SELECT  
    s.track_name, 
    s.popularity_score, 
    s.release_date, 
    s.danceability, 
    s.energy, 
    s.loudness, 
    s.speechiness, 
    s.acousticness, 
    s.instrumentalness, 
    s.liveness, 
    s.valence
FROM 
    Songs s
JOIN 
    China_Market cm ON s.song_id = cm.song_id
JOIN 
    Artists a ON cm.artist_id = a.artist_id
GROUP BY 
    s.song_id;
"""

try:
    China_market_df = pd.read_sql_query(China_market_query, conn)
    print("Query executed successfully, DataFrame is populated.")
except Exception as e:
    print(f"An error occurred during the query: {e}")
try:
    China_market_df.to_csv('China_market_analysis.csv', index=False)
    print("CSV file created successfully.")
except Exception as e:
    print(f"An error occurred while writing the CSV file: {e}")

conn.close()


