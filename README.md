# MoodTunes — Emotion-Based Music Recommendation System

An intelligent music recommendation system that detects emotions 
from text and emoji input and suggests matching songs with 
YouTube and Spotify previews.

## Features
- Detects 8 emotions from text, emoji, or mixed input
- TF-IDF + LinearSVC (SVM) model — 85% accuracy
- Active learning pipeline — improved 12% after 500 interactions
- Cosine similarity for music matching
- YouTube & Spotify API integration
- English + Bollywood music support
- Rule-based emoji detection

## Tech Stack
- Python, FastAPI, Uvicorn
- scikit-learn (LinearSVC), NLTK, TF-IDF
- YouTube Data API v3, Spotify Web API
- Pandas, NumPy, FuzzyWuzzy
- HTML, CSS, JavaScript

## Dataset
- 10,000+ text-emotion pairs (8 emotions)
- 2,000+ songs tagged with emotion metadata

## Setup
```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

## Results
- Emotion detection accuracy: 85%
- Avg recommendation time: 2-3 seconds
- Active learning improvement: 12% after 500 interactions

## Academic
Submitted as Semester VII project — K.S. School of Business 
Management, M.Sc. (CA & IT), 2025
