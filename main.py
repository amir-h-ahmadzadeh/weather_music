from dotenv import load_dotenv
import os
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def get_weather_info(location):
    # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
    api_key = os.getenv('WEATHER_API_KEY')
    # OpenWeatherMap API endpoint for 5-day forecast by city name
    api_url = f'https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}'

    try:
        # Make the API request
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            weather_data = response.json()

            # Extract relevant data for the next 5 days
            forecast = weather_data['list']

            # Initialize lists to store data for each day
            dates = []
            temperatures = []
            rains = []

            # Extract temperature and rain information for each day
            for item in forecast:
                timestamp = item['dt']
                date = datetime.utcfromtimestamp(timestamp).date()
                if date not in dates:
                    dates.append(date)
                    temperatures.append(item['main']['temp'] - 273.15)  # Convert to Celsius
                    if 'rain' in item:
                        rains.append(item['rain']['3h'])
                    else:
                        rains.append(0)

            # Create a bar graph to display temperature and rain for each day
            plt.figure(figsize=(10, 6))
            plt.bar(dates, temperatures, label='Temperature (°C)')
            plt.bar(dates, rains, label='Rain (mm)', alpha=0.5)
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.title(f'5-Day Weather Forecast for {location}')
            plt.legend()
            plt.show()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_weather_recommendation(location):
    # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
    api_key = os.getenv('WEATHER_API_KEY')

    # OpenWeatherMap API endpoint for current weather data by city name
    api_url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}'

    try:
        # Make the API request
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            weather_data = response.json()

            # Extract relevant weather data
            temperature_celsius = weather_data['main']['temp'] - 273.15  # Convert to Celsius
            wind_speed = weather_data['wind']['speed']
            rain = weather_data.get('rain', {}).get('1h', 0)  # Rain in the last hour (mm)
            feels_like_celsius = weather_data['main']['feels_like'] - 273.15  # Convert to Celsius
            humidity = weather_data['main']['humidity']
            is_sunny = 'clear' in weather_data['weather'][0]['description'].lower()

            print(f"Weather details for {location}:")
            print(f"Temperature: {temperature_celsius:.2f}°C")
            print(f"Wind Speed: {wind_speed} m/s")
            print(f"Rain (last hour): {rain} mm")
            print(f"Feels Like: {feels_like_celsius:.2f}°C")
            print(f"Humidity: {humidity}%")
            print(f"Sunny: {'Yes' if is_sunny else 'No'}")

            if is_sunny:
                if temperature_celsius > 25:
                    print("Recommendation: Wear light and breathable clothing, sunglasses, and sunscreen.")
                elif temperature_celsius > 18:
                    print("Recommendation: Bring along a light jacket and don't forget your sunglasses.")
                else:
                    print("Recommendation: Wear layers and bring a jacket.")
            elif rain > 0:
                print("Recommendation: Get dressed for a rainy day! Don't forget your umbrella and waterproof jacket.")
            else:
                print("Recommendation: Dress comfortably for the day.")

        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def recommend_music(mood, location):
    # Customize your music recommendation logic based on mood and location
    # You can search for specific playlists, tracks, or artists on Spotify
    # I chose playlists related to mood but up for discussion

    # Define keywords for different moods (wecan customize these)
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    # Create a Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    mood_keywords = {
        "happy": "happy music",
        "upbeat": "upbeat music",
        "mellow": "mellow music",
        "rainy": "rainy day music",
        "neutral": "chill music"
    }

    # Search for playlists based on mood
    mood_keyword = mood_keywords[mood]  # I chose "chill music" if mood is not recognized. Again up for discussion.
    #results = sp.search(q=mood_keyword, type='playlist', limit=5)  # Limit to 5 playlists. Up for discussion group
    results = sp.search(q=mood_keyword, type='playlist')

    if results and 'playlists' in results:
        playlists = results['playlists']['items']
        if playlists:
            print(f"Here are some {mood} playlists you might like in {location}:")

            for playlist in playlists:
                print(f"{playlist['name']}: {playlist['external_urls']['spotify']}")

        else:
            print(f"No {mood} playlists found.")
    else:
        print("An error occurred while searching for music.")

def get_top_songs_by_location(location):
    # Load Spotify API credentials from environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for playlists related to the user's location
    query = f"top songs in {location}"
    playlists = sp.search(q=query, type='playlist', limit=1)

    if not playlists['playlists']['items']:
        return None  # No playlists found for the location

    # Get the URI of the top playlist
    top_playlist_uri = playlists['playlists']['items'][0]['uri']

    # Get the tracks from the playlist
    tracks = sp.playlist_tracks(top_playlist_uri, limit=50)

    # Extract track information (name and artist)
    top_songs = []
    for track in tracks['items']:
        track_info = {
            'Song Name': track['track']['name'],
            'Artist': ', '.join([artist['name'] for artist in track['track']['artists']])
        }
        top_songs.append(track_info)

    return top_songs, top_playlist_uri


def main():
    load_dotenv()
    # Prompt the user for their desired location
    loc = input("Where is your desired location: ")
    location = TextBlob(loc).correct()

    # Get weather information and provide recommendations
    get_weather_info(location)

    # Ask if the user wants detailed weather information
    choice = input(f"Do you want detailed weather information for {location}? (yes/no): ").lower()

    if choice == 'yes':
        # Get detailed weather information and provide recommendations
        get_weather_recommendation(location)
    #else:
    #    # Ask the user about their mood
    #    mood = input("How are you feeling today (happy/upbeat/mellow/rainy/neutral)? ").lower()
    exit = True
    while exit:

        recom_choice = input("we can also sugguest some song based on the location or the weather. What is your choice?(weather/location)?[for exit type 'exit']: ")
        recom_choice = TextBlob(recom_choice).correct()
            # Recommend music based on mood and location
        if recom_choice ==  'weather':
            mood = input("How are you feeling today (happy/upbeat/mellow/rainy/neutral)? ").lower()
            recommend_music(mood, location)
        elif recom_choice == 'location':
            top_songs, playlist_uri = get_top_songs_by_location(location)
            if top_songs:
                df = pd.DataFrame(top_songs)
                print(f"Top 50 Songs in {location}:")
                print(df)

                # Ask the user if they want the link to the playlist
                choice = input("Would you like the link to the suggested playlist? (yes/no): ")
                if choice.lower() == "yes":
                    playlist_url = f"https://open.spotify.com/playlist/{playlist_uri.split(':')[-1]}"
                    print(f"Playlist Link: {playlist_url}")
        elif recom_choice == 'exit':
            exit = False
        else:
            print('I did not catch that. Try again.')


    print(f"Have a great time in {location}!")

if __name__ == "__main__":
    main()