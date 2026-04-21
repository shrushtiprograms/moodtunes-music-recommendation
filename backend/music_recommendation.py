import pandas as pd
import os
import logging
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import json
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

# Import constants
from constants import EMOTION_CATEGORY_MAPPING, EMOTION_TO_MUSIC_MAPPING, EMOTION_SIMILARITY

def create_default_music_data():
    """Create default music dataset if file is missing"""
    data = {
        'title': ["Happy", "Someone Like You", "Don't Worry Be Happy", 
                  "Bohemian Rhapsody", "Clair de Lune", "Love Story", "Despacito"],
        'artist': ["Pharrell Williams", "Adele", "Bobby McFerrin", 
                   "Queen", "Debussy", "Taylor Swift", "Luis Fonsi & Daddy Yankee"],
        'emotion': ["happy", "sad", "happy", "mixed", "calm", "love", "happy"],
        'lyrics': ["Cause I'm happy clap along...", "I heard that you're settled down...", 
                   "In every life we have some trouble...", "Is this the real life...", 
                   "Instrumental calm melody...", "We were both young when I first saw you...", 
                   "Despacito quiero respirar..."],
        'category': ["English", "English", "English", "English", "English", "English", "English"]
    }
    return pd.DataFrame(data)

def get_emotion_fallback(emotion):
    """Get fallback emotions for better recommendation coverage"""
    emotion_fallbacks = {
        'happy': ['excited', 'joyful', 'energetic', 'upbeat'],
        'sad': ['melancholic', 'emotional', 'calm', 'nostalgic'],
        'angry': ['intense', 'powerful', 'energetic', 'aggressive'],
        'calm': ['peaceful', 'relaxing', 'serene', 'soothing'],
        'love': ['romantic', 'passionate', 'intimate', 'affectionate'],
        'excited': ['energetic', 'upbeat', 'happy', 'celebratory'],
        'anxious': ['calm', 'soothing', 'relaxing', 'peaceful'],
        'neutral': ['happy', 'calm', 'balanced', 'general']
    }
    return emotion_fallbacks.get(emotion, ['neutral'])

def normalize_category(category):
    """Normalize category names for consistent filtering"""
    if pd.isna(category):
        return "unknown"
    
    category = str(category).lower().strip()
    
    # Map various category names to standard ones
    category_mapping = {
        'hindi': 'bollywood',
        'indian': 'bollywood',
        'desi': 'bollywood',
        'english': 'english',
        'western': 'english',
        'international': 'english',
        'all': 'all'
    }
    
    return category_mapping.get(category, category)

class MusicRecommender:
    def __init__(self, config=None):
        self.config = config
        os.makedirs('data', exist_ok=True)
        if not os.path.exists('data/music_dataset.csv'):
            self.df = create_default_music_data()
            self.df.to_csv('data/music_dataset.csv', index=False)
        else:
            self.df = pd.read_csv('data/music_dataset.csv')
        
        # Normalize category names in the dataset
        self.df['category_normalized'] = self.df['category'].apply(normalize_category)
        
        # Preprocess for TF-IDF
        self.df['cleaned_text'] = self.df['title'] + ' ' + self.df['artist'] + ' ' + self.df['lyrics'].fillna('')
        self.tfidf = TfidfVectorizer(max_features=5000)
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['cleaned_text'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        # Initialize API session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def validate_link(self, url):
        """Validate if a URL is accessible with retries"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            logger.error(f"Invalid URL: {url}")
            return False
    
    def extract_youtube_id(self, url):
        """Extract YouTube video ID from URL"""
        pattern = r'(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def update_dataset(self, new_song):
        """Add a new song to the dataset with API-driven links"""
        try:
            required_keys = ['title', 'artist', 'emotion', 'lyrics']
            if not all(key in new_song for key in required_keys):
                raise ValueError("New song missing required fields")
            
            # Fetch live links
            youtube_link = self.get_youtube_link(new_song['title'], new_song['artist'])
            spotify_link = self.get_spotify_link(new_song['title'], new_song['artist'])
            
            if youtube_link == "N/A" or spotify_link == "N/A":
                raise ValueError("Failed to fetch valid links from APIs")
            
            youtube_id = self.extract_youtube_id(youtube_link)
            thumbnail = f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg" if youtube_id else ""
            
            new_song.update({
                'youtube_link': youtube_link,
                'spotify_link': spotify_link,
                'thumbnail': thumbnail
            })
            new_df = pd.DataFrame([new_song])
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.df.to_csv('data/music_dataset.csv', index=False)
            # Update TF-IDF and similarity
            self.df['cleaned_text'] = self.df['title'] + ' ' + self.df['artist'] + ' ' + self.df['lyrics'].fillna('')
            self.tfidf_matrix = self.tfidf.fit_transform(self.df['cleaned_text'])
            self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
            logger.info(f"Added new song: {new_song['title']}")
        except Exception as e:
            logger.error(f"Error updating dataset: {e}")
    
    @lru_cache(maxsize=1000)
    def get_spotify_link(self, title, artist):
        if not self.config:
            return "N/A"
            
        token = self.get_spotify_token(self.config["SPOTIFY_CLIENT_ID"], self.config["SPOTIFY_CLIENT_SECRET"])
        if not token:
            return "N/A"
            
    # Proper URL encoding for Spotify
        query = f"{title} {artist}"
        encoded_query = requests.utils.quote(query)
        url = f"https://api.spotify.com/v1/search?q={encoded_query}&type=track&limit=1"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("tracks", {}).get("items"):
                return data["tracks"]["items"][0]["external_urls"]["spotify"]
            return "N/A"
        except Exception as e:
            logger.error(f"Failed to fetch Spotify link for {title} by {artist}: {str(e)}")
            return "N/A"
    
    def get_spotify_token(self, client_id, client_secret):
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {"grant_type": "client_credentials"}
        auth = (client_id, client_secret)
        
        try:
            response = self.session.post(auth_url, auth=auth, data=auth_data, timeout=30)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logger.error(f"Spotify token request failed: {str(e)}")
            return None
    
    @lru_cache(maxsize=1000)
    def get_youtube_link(self, title, artist):
        if not self.config:
            return "N/A"
            
        # PROPERLY ACCESS THE API KEY
        api_key = self.config.get('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found in config")
            return "N/A"
        
        query = f"{title} {artist} official music video"
        
        # PROPER URL ENCODING
        encoded_query = requests.utils.quote(query)
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={encoded_query}&key={api_key}&type=video&maxResults=1"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("items"):
                video_id = data["items"][0]["id"]["videoId"]
                return f"https://www.youtube.com/watch?v={video_id}"
            return "N/A"
        except Exception as e:
            logger.error(f"Failed to fetch YouTube link for {title} by {artist}: {str(e)}")
            return "N/A"
        
    def get_recommendations(self, emotion, category="All", n=10):
        try:
            emotion = emotion.lower()
            logger.info(f"Detecting recommendations for emotion: {emotion}, category: {category}")
        
            # Normalize the category filter
            category_filter = normalize_category(category)
            logger.info(f"Normalized category filter: {category_filter}")
        
            # Get all related emotions for the detected emotion
            related_emotions = EMOTION_CATEGORY_MAPPING.get(emotion, [emotion])
            logger.info(f"Related emotions for {emotion}: {related_emotions}")
    
            selected_titles = set()
            filtered = pd.DataFrame()
    
            # Get all songs for the exact emotion and related emotions
            available = self.df[self.df['emotion'].str.lower().isin(related_emotions)].dropna(
                subset=['title', 'artist', 'emotion', 'category_normalized', 'lyrics'])
    
            logger.info(f"Available songs for {emotion} and related emotions: {len(available)}")
        
            # Apply category filter
            if category_filter != "all":
                available = available[available['category_normalized'] == category_filter]
                logger.info(f"Available songs after category filtering: {len(available)}")
    
            # Shuffle the available songs to get different recommendations each time
            available = available.sample(frac=1).reset_index(drop=True)
        
            for _, song in available.iterrows():
                if song['title'] not in selected_titles:
                    filtered = pd.concat([filtered, pd.DataFrame([song])], ignore_index=True)
                    selected_titles.add(song['title'])
                    if len(filtered) >= n:
                        break
    
            # If we still don't have enough songs, use fallback emotions
            if len(filtered) < n:
                fallback_emotions = get_emotion_fallback(emotion)
                logger.info(f"Using fallback emotions: {fallback_emotions}")
            
                for fallback_emotion in fallback_emotions:
                    if len(filtered) >= n:
                        break
                    
                    fallback_songs = self.df[self.df['emotion'].str.lower() == fallback_emotion].dropna(
                        subset=['title', 'artist', 'emotion', 'category_normalized', 'lyrics'])
                
                    # Apply category filter to fallback songs
                    if category_filter != "all":
                        fallback_songs = fallback_songs[fallback_songs['category_normalized'] == category_filter]
                
                    # Shuffle fallback songs
                    fallback_songs = fallback_songs.sample(frac=1).reset_index(drop=True)
                
                    for _, song in fallback_songs.iterrows():
                        if song['title'] not in selected_titles:
                            filtered = pd.concat([filtered, pd.DataFrame([song])], ignore_index=True)
                            selected_titles.add(song['title'])
                            if len(filtered) >= n:
                                break
    
            # If we still don't have enough songs, use similarity
            if len(filtered) < n and len(self.df) > 0:
                # Find the most similar emotion in our dataset
                all_emotions = self.df['emotion'].str.lower().unique()
                best_match = emotion
                best_score = 0
        
                for e in all_emotions:
                    score = fuzz.ratio(emotion, e)
                    if score > best_score:
                        best_score = score
                        best_match = e
        
                logger.info(f"Best emotion match: {best_match} with score {best_score}")

                emotion_index = self.df[self.df['emotion'].str.lower() == best_match].index
                if len(emotion_index) > 0:
                    emotion_index = emotion_index[0]
                    sim_scores = list(enumerate(self.cosine_sim[emotion_index]))
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n*2]
                    song_indices = [i[0] for i in sim_scores]
                    similar_songs = self.df.iloc[song_indices].dropna(
                        subset=['title', 'artist', 'emotion', 'category_normalized', 'lyrics'])
                
                    # Apply category filter to similar songs
                    if category_filter != "all":
                        similar_songs = similar_songs[similar_songs['category_normalized'] == category_filter]
                
                    # Shuffle similar songs
                    similar_songs = similar_songs.sample(frac=1).reset_index(drop=True)
            
                    for _, song in similar_songs.iterrows():
                        if song['title'] not in selected_titles:
                            filtered = pd.concat([filtered, pd.DataFrame([song])], ignore_index=True)
                            selected_titles.add(song['title'])
                            if len(filtered) >= n:
                                break
    
            # Fill with random songs if still not enough
            if len(filtered) < n:
                remaining = n - len(filtered)
                available_other = self.df[~self.df['title'].isin(selected_titles)].dropna(
                    subset=['title', 'artist', 'emotion', 'category_normalized', 'lyrics'])
            
                # Apply category filter to random songs
                if category_filter != "all":
                    available_other = available_other[available_other['category_normalized'] == category_filter]
        
                if len(available_other) > 0:
                    # Shuffle available songs
                    available_other = available_other.sample(frac=1).reset_index(drop=True)
                    sampled = available_other.sample(min(remaining, len(available_other)))
                    filtered = pd.concat([filtered, sampled], ignore_index=True)
    
            logger.info(f"Final filtered recommendations: {len(filtered)} songs")

            # Convert to list of dictionaries and add links
            recommendations = []
            for _, song in filtered.iterrows():
                youtube_link = self.get_youtube_link(song['title'], song['artist'])
                spotify_link = self.get_spotify_link(song['title'], song['artist'])
            
                recommendations.append({
                    'title': song['title'],
                    'artist': song['artist'],
                    'emotion': song['emotion'],
                    'category': song['category'],  # Use original category, not normalized
                    'lyrics': song['lyrics'],
                    'youtube_link': youtube_link,
                    'spotify_link': spotify_link
                })
        
            # Shuffle the final recommendations for variety
            import random
            random.shuffle(recommendations)
        
            return recommendations[:n]
    
        except Exception as e:
            logger.error(f"Error in recommendations: {e}")
            # Fallback to random songs
            fallback = self.df.sample(min(n, len(self.df))).to_dict('records')
            for song in fallback:
                song['youtube_link'] = self.get_youtube_link(song['title'], song['artist']) or "N/A"
                song['spotify_link'] = self.get_spotify_link(song['title'], song['artist']) or "N/A"
        
            # Shuffle fallback recommendations
            import random
            random.shuffle(fallback)

            return fallback[:n]

    def search_songs_by_name_or_artist(self, query, n=10):
        """Search songs by title or artist name"""
        try:
            query = query.lower().strip()
            logger.info(f"🔍 Direct search for: {query}")
            
            # Search in title and artist
            title_matches = self.df[self.df['title'].str.lower().str.contains(query, na=False)]
            artist_matches = self.df[self.df['artist'].str.lower().str.contains(query, na=False)]
            
            # Combine results and remove duplicates
            results = pd.concat([title_matches, artist_matches]).drop_duplicates()
            
            logger.info(f"Found {len(results)} direct matches")
            
            # If no direct matches, use fuzzy matching
            if len(results) == 0:
                logger.info("No direct matches, using fuzzy search")
                from fuzzywuzzy import process
                
                # Search in titles
                all_titles = self.df['title'].dropna().tolist()
                title_matches = process.extract(query, all_titles, limit=5)
                
                # Search in artists  
                all_artists = self.df['artist'].dropna().tolist()
                artist_matches = process.extract(query, all_artists, limit=5)
                
                # Get matched songs
                matched_indices = []
                for match, score in title_matches + artist_matches:
                    if score > 60:  # Minimum similarity threshold
                        idx = self.df[(self.df['title'] == match) | (self.df['artist'] == match)].index
                        matched_indices.extend(idx)
                
                results = self.df.iloc[list(set(matched_indices))]
                logger.info(f"Found {len(results)} fuzzy matches")
            
            # Convert to list of dictionaries with links
            recommendations = []
            for _, song in results.head(n).iterrows():
                youtube_link = self.get_youtube_link(song['title'], song['artist'])
                spotify_link = self.get_spotify_link(song['title'], song['artist'])
                
                recommendations.append({
                    'title': song['title'],
                    'artist': song['artist'],
                    'emotion': song.get('emotion', 'unknown'),
                    'category': song.get('category', 'unknown'),
                    'youtube_link': youtube_link,
                    'spotify_link': spotify_link,
                    'search_type': 'direct_search'
                })
            
            logger.info(f"Returning {len(recommendations)} recommendations")
            return recommendations[:n]
            
        except Exception as e:
            logger.error(f"Error in direct search: {e}")
            return []

# Global instance (will be initialized with config in app.py)
recommender = None

def initialize_recommender(config):
    """Initialize the recommender with config"""
    global recommender
    recommender = MusicRecommender(config)

def get_recommendations(emotion, category="All", n=10):
    if recommender is None:
        raise ValueError("Recommender not initialized. Call initialize_recommender() first.")
    return recommender.get_recommendations(emotion, category, n)

def update_dataset(new_song):
    if recommender is None:
        raise ValueError("Recommender not initialized. Call initialize_recommender() first.")
    recommender.update_dataset(new_song)

def search_directly(query, n=10):
    """Public function for direct song/artist search"""
    if recommender is None:
        raise ValueError("Recommender not initialized. Call initialize_recommender() first.")
    return recommender.search_songs_by_name_or_artist(query, n)

# Add this function to your music_recommendation.py file
def fix_dataset_categories():
    """Check and fix category names in the dataset"""
    try:
        df = pd.read_csv('data/music_dataset.csv')
        
        # Check current categories
        print("Current categories in dataset:")
        print(df['category'].value_counts())
        
        # Normalize categories
        df['category'] = df['category'].apply(normalize_category)
        
        # Save fixed dataset
        df.to_csv('data/music_dataset.csv', index=False)
        
        print("Categories after normalization:")
        print(df['category'].value_counts())
        
        return True
    except Exception as e:
        print(f"Error fixing dataset categories: {e}")
        return False

# Add this function to your music_recommendation.py file
def ensure_all_songs_considered():
    """Make sure all songs in the dataset can be recommended"""
    try:
        df = pd.read_csv('data/music_dataset.csv')
        
        # Check if we have songs with missing emotions
        missing_emotion = df[df['emotion'].isna() | (df['emotion'] == '')]
        if len(missing_emotion) > 0:
            print(f"Found {len(missing_emotion)} songs with missing emotions")
            
            # Try to auto-detect emotions for these songs
            from emotion_detection import EmotionDetector
            detector = EmotionDetector()
            
            for idx, row in missing_emotion.iterrows():
                # Use title and lyrics to detect emotion
                text = f"{row['title']} {row['lyrics']}"
                emotion = detector.detect(text)
                
                # Update the emotion
                df.at[idx, 'emotion'] = emotion
                print(f"Set emotion '{emotion}' for song: {row['title']}")
            
            # Save the updated dataset
            df.to_csv('data/music_dataset.csv', index=False)
            print("Updated dataset with missing emotions")
        
        # Check if we have songs with missing categories
        missing_category = df[df['category'].isna() | (df['category'] == '')]
        if len(missing_category) > 0:
            print(f"Found {len(missing_category)} songs with missing categories")
            
            # Set default category based on language detection (simple heuristic)
            for idx, row in missing_category.iterrows():
                # Simple language detection based on title and artist
                text = f"{row['title']} {row['artist']}"
                
                # Check if text contains Hindi characters or common Hindi words
                hindi_pattern = re.compile(r'[\u0900-\u097F]')
                if hindi_pattern.search(text):
                    category = 'Bollywood'
                else:
                    category = 'English'
                
                # Update the category
                df.at[idx, 'category'] = category
                print(f"Set category '{category}' for song: {row['title']}")
            
            # Save the updated dataset
            df.to_csv('data/music_dataset.csv', index=False)
            print("Updated dataset with missing categories")
        
        return True
    except Exception as e:
        print(f"Error ensuring all songs are considered: {e}")
        return False