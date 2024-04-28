# This script uses Selenium for web scraping because the target webpage
# contains dynamically loaded content which is not accessible through
# standard requests and static HTML parsing. Selenium automates a browser
# session to retrieve the full content after scripts have run and the 
# page has rendered completely.

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import time
import re
import sqlite3


# Start the Chrome browser
driver = webdriver.Chrome()

# URL to the specific song ranking list
url = "https://music.163.com/#/discover/toplist?id=2809513713"
driver.get(url)
driver.maximize_window()  # Maximize the browser window
time.sleep(2)
print("step1")

# Switch to the iframe that contains the song ranking
iframe = driver.find_element(By.XPATH, "//iframe[@id='g_iframe']")
driver.switch_to.frame(iframe)
time.sleep(2)
print("step2")

# Use Selenium's page source attribute to get the HTML after the iframe has loaded
page_html = driver.page_source

# Parse the HTML with lxml
html = etree.HTML(page_html)
# Define XPath for track names and artist names
track_xpath = "//table[contains(@class,'m-table')]/tbody/tr/td[2]/div/div/div/span/a/b"
artist_xpath = "//table[contains(@class,'m-table')]/tbody/tr/td[4]/div/span/@title"
print("step3")

# Extract track names and artist names
tracks = html.xpath(track_xpath)
artists = html.xpath(artist_xpath)

# Close the browser
driver.quit()

print(artists[0])
# Create a DataFrame with the extracted data
df = pd.DataFrame({
    'Track_name': [track.get('title') for track in tracks],
    'Artist_name': artists
})

# Output the DataFrame to a CSV file
csv_file_path = 'netease_music_toplist.csv'
df.to_csv(csv_file_path, index=False)

print(f'Data saved to {csv_file_path}')


# Clean Track_name
def sanitize_track_names(track_name):
    # Remove non-English characters and specific symbols
    track_name = re.sub(r'[^\x00-\x7F]+', '', track_name)  # Remove non-ASCII characters
    track_name = re.sub(r'¬†', ' ', track_name)  # Replace specific symbol with space
    track_name = re.sub(r'\(.*?\)', '', track_name)  # Remove content within parentheses
    track_name = re.sub(r'\s+', ' ', track_name)  # Replace multiple spaces with a single space
    track_name = re.sub(r'\-$', '', track_name)  # Remove hyphen at the end
    track_name = track_name.strip()  # Remove leading/trailing whitespace
    return track_name

csv_file_path = 'netease_music_toplist.csv'
df = pd.read_csv(csv_file_path)
df['Track'] = df['Track'].apply(sanitize_track_names)
df.to_csv(csv_file_path, index=False)  # Save in place

# Clean artist_name
def sanitize_artist_names(artist_name):
    # Replace slashes with commas and remove non-ASCII characters
    artist_name = artist_name.replace('/', ', ')
    artist_name = re.sub(r'[^\x00-\x7F]+', '', artist_name)
    # Ensure there are no leading/trailing spaces around the artist names
    artist_name = ', '.join(name.strip() for name in artist_name.split(','))
    return artist_name

csv_file_path = 'netease_music_toplist.csv'
df = pd.read_csv(csv_file_path)

df['Artist'] = df['Artist'].apply(sanitize_artist_names)
df.to_csv(csv_file_path, index=False)
df.rename(columns={'Track': 'Track_name', 'Artist': 'Artist_name'}, inplace=True)


# Check for NaN values in 'Artist_name' and replace them with an empty string
df['Artist_name'] = df['Artist_name'].fillna('')
df.to_csv(csv_file_path, index=False)
print('Finish Cleaning')

# After interfacing with the Spotify API, the following codes filters out tracks 
# that are not found on Spotify. The remaining tracks, which have been 
# successfully matched with Spotify's database, are saved to a new CSV file
# Step 1: Connect to SQLite database and fetch song IDs
db_file_path = 'project_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute("SELECT song_id, track_name FROM songs")
fetched_songs = cursor.fetchall()
conn.close()
# Create a dictionary from fetched song data
song_dict = {track_name: song_id for song_id, track_name in fetched_songs}
# Step 2: Load the original CSV into a pandas DataFrame
csv_file_path = 'netease_music_toplist.csv'
df = pd.read_csv(csv_file_path)
# Step 3: Filter the DataFrame based on track names that have a matching song_id
df_filtered = df[df['Track_name'].apply(lambda x: x in song_dict)]
# Step 4: Write the filtered DataFrame to a new CSV file including track_name and artist_name
df_filtered.to_csv('netease_music_toplist_updated.csv', columns=['Track_name', 'Artist_name'], index=False)
print(f"Updated CSV with {len(df_filtered)} songs that matched Spotify's database.")

