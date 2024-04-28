import requests
from bs4 import BeautifulSoup
import pandas as pd


# The URL of the Billboard Year-End Hot 100 songs chart
url = 'https://www.billboard.com/charts/year-end/hot-100-songs/'

response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    # Find all song entry containers
    for entry in soup.find_all(attrs={'class': 'o-chart-results-list-row-container'}):
        # Extract the track name and artist name
        track_name = entry.find('h3', class_='c-title').get_text(strip=True)
        artist_name = entry.find('h3', class_='c-title').find_next('span', class_='c-label').get_text(strip=True)
        
        data.append({
            'Track_name': track_name,
            'Artist_name': artist_name
        })
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)
    # Save the DataFrame to a CSV file
    csv_file_path = 'billboard_year_end_hot_100.csv' # relative path 
    df.to_csv(csv_file_path, index=False)
    print(f'Data saved to {csv_file_path}')
    
else:
    print(f'Failed to retrieve data: Status code {response.status_code}')
    

#Clean data to normalize artist_name
csv_file_path = 'billboard_year_end_hot_100.csv'
df = pd.read_csv(csv_file_path)

# Define the sanitization function
def sanitize_artist_names(artist_name):
    # Replace various conjunctions and separators with a comma
    artist_name = artist_name.replace(' & ', ', ')
    artist_name = artist_name.replace(' With ', ', ')
    artist_name = artist_name.replace(' Featuring ', ', ')
    artist_name = artist_name.replace(' X ', ', ')
    artist_name = artist_name.replace(' x ', ', ')
    # Strip any leading/trailing whitespace that may have been introduced
    artist_name = artist_name.strip()
    return artist_name

# Apply the sanitization function to the 'Artist_name' column
df['Artist_name'] = df['Artist_name'].apply(sanitize_artist_names)

# Save the cleaned DataFrame to the same CSV file, effectively cleaning it "in place"
df.to_csv(csv_file_path, index=False)








    


