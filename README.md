# MoodTunes — Emotion-Based Music Recommendation System

An intelligent music recommendation system that detects emotions from text, emoji, or combined input and recommends matching songs with YouTube and Spotify previews.

## Features

- Detects 8 emotions from text, emoji, or mixed input
- TF-IDF + LinearSVC (SVM) model — 85% accuracy on 10,000+ sample dataset
- Rule-based emoji detection with majority voting for multi-emoji input
- Active learning pipeline — model improved 12% after 500 user interactions
- Cosine similarity for music matching from 2,000+ tagged songs
- YouTube & Spotify API integration with embedded previews
- English and Bollywood music support with category filtering
- Direct search by song name or artist (e.g., "Arijit Singh play")
- Dark/Light mode toggle with multiple color themes

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **ML / NLP:** scikit-learn (LinearSVC), NLTK, TF-IDF, FuzzyWuzzy
- **APIs:** YouTube Data API v3, Spotify Web API
- **Data:** Pandas, NumPy
- **Frontend:** HTML5, CSS3, JavaScript

## Dataset

- 10,000+ text-emotion pairs covering 8 primary emotions
- 2,000+ songs tagged with emotion metadata (English + Bollywood)

## Setup

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

Create `.env` file for API keys:
```
YOUTUBE_API_KEY=your_key
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

> System works without API keys but streaming links will show as N/A.

To retrain the model:
```bash
python backend/train_model.py
```

## API Endpoints

**POST /api/detect-emotion** — Detect emotion from text input

**POST /api/recommendations** — Get songs based on detected emotion

**POST /api/search** — Search by song name or artist

## Project Structure

```
├── backend/
│   ├── app.py                  # FastAPI application
│   ├── emotion_detection.py    # Emotion detection pipeline
│   ├── music_recommendation.py # Recommendation engine
│   ├── active_learning.py      # Auto dataset expansion
│   ├── train_model.py          # Model training script
│   └── constants.py            # Emoji-emotion mappings
├── frontend/
│   ├── templates/index.html    # Main UI
│   └── static/                 # CSS themes + JS
├── data/
│   ├── emotion_dataset.csv     # Training data
│   └── music_dataset.csv       # Music library
├── models/
│   └── emotion_classifier.pkl  # Trained model
└── requirements.txt
```

## Results

- Emotion detection accuracy: 85%
- Average recommendation time: 2–3 seconds
- Active learning improvement: 12% after 500 interactions

## Academic

Submitted as Semester VII project — K.S. School of Business Management  
M.Sc. (CA & IT), 2025  
GitHub: [github.com/shrushtiprograms/moodtunes-music-recommendation](https://github.com/shrushtiprograms/moodtunes-music-recommendation)
