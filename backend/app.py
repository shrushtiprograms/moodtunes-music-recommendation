from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import logging
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

# Import modules
from emotion_detection import EmotionDetector, get_confidence_score, suggest_emotion
from music_recommendation import initialize_recommender, get_recommendations, search_directly, normalize_category
from active_learning import active_learner
from constants import EMOJI_EMOTION_MAP

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    logger.info("Config loaded successfully")
except FileNotFoundError:
    logger.warning("config.json not found, using environment variables")
    config = {
        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),
        "SPOTIFY_CLIENT_ID": os.getenv("SPOTIFY_CLIENT_ID", ""),
        "SPOTIFY_CLIENT_SECRET": os.getenv("SPOTIFY_CLIENT_SECRET", "")
    }

# Initialize components
try:
    initialize_recommender(config)
    detector = EmotionDetector()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {e}")

# Create FastAPI app
app = FastAPI(
    title="MoodTunes API", 
    description="Emotion-Based Music Recommendation System",
    version="1.0.0"
)

# Get current directory and set correct paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go one level up to project root

# Define paths for static files and templates
static_dir = os.path.join(project_root, "frontend", "static")
templates_dir = os.path.join(project_root, "frontend", "templates")

# Create directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

logger.info(f"Static directory: {static_dir}")
logger.info(f"Templates directory: {templates_dir}")

# Mount static files and templates
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")

if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    logger.warning(f"Templates directory not found: {templates_dir}")
    # Create a simple template response as fallback
    templates = None

# In-memory storage for session data
search_history = []

# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    text: str
    category: str = "All"
    sort: str = "default"

class RecommendationRequest(BaseModel):
    emotion: str
    category: str = "All"
    limit: int = 10

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

# Helper functions
def detect_search_type(text: str) -> str:
    """Detect if user wants emotion-based or direct search"""
    text_lower = text.lower()
    
    # Keywords that indicate direct song/artist search
    direct_search_keywords = [
        'play', 'song', 'artist', 'music', 'by', 'search', 'find',
        'gaan', 'gāna', 'गाना', 'संगीत', 'play song', 'play music'
    ]
    
    # Check if text contains direct search keywords
    for keyword in direct_search_keywords:
        if keyword in text_lower:
            return 'direct'
    
    # Check if it's a known artist or song name pattern
    if any(word in text_lower for word in ['arjit', 'arijit', 'kishore', 'lata', 'taylor', 'weeknd']):
        return 'direct'
    
    # Default to emotion detection
    return 'emotion'

def detect_emotion_with_learning(text: str) -> str:
    """Detect emotion with automatic active learning"""
    # First try regular detection
    emotion = detector.detect(text)
    
    # For emoji-only inputs, skip active learning (high confidence)
    emoji_only = True
    for char in text:
        if char not in EMOJI_EMOTION_MAP and not char.isspace():
            emoji_only = False
            break
    
    if emoji_only:
        return emotion

    confidence = get_confidence_score(text)
    
    # If low confidence, use active learning
    if confidence < 0.6:
        # Try to find similar emotion
        similar_emotion, similarity = active_learner.find_similar_emotion(text)
        
        if similar_emotion:
            if similarity >= 0.95:
                emotion = similar_emotion
                logger.info(f"Exact match found: {emotion}")
            else:
                if active_learner.add_to_dataset(text, similar_emotion):
                    logger.info(f"Automatically learned: '{text}' = {similar_emotion}")
                emotion = similar_emotion
        else:
            suggested = suggest_emotion(text)
            if suggested:
                if active_learner.add_to_dataset(text, suggested):
                    logger.info(f"Automatically learned new pattern: '{text}' = {suggested}")
                emotion = suggested
            else:
                emotion = "neutral"
                logger.info("Could not determine emotion, using neutral as default")
    
    return emotion

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main page"""
    if templates and os.path.exists(templates_dir):
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        # Fallback HTML response
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MoodTunes - Emotion-Based Music Recommendation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎵 MoodTunes</h1>
                <p>Frontend files not found. Please check if frontend files are in the correct location.</p>
                <p>API is running correctly. You can test the API endpoints at <a href="/docs">/docs</a></p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.post("/analyze")
async def analyze_emotion(request: AnalyzeRequest):
    """Analyze emotion and get recommendations"""
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Please enter your mood or feeling")
        
        search_type = detect_search_type(text)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if search_type == 'direct':
            recommendations = search_directly(text, 10)
            
            # Apply sorting if needed
            if request.sort == 'asc':
                recommendations.sort(key=lambda x: x['title'])
            elif request.sort == 'desc':
                recommendations.sort(key=lambda x: x['title'], reverse=True)
            
            search_history.append({
                "text": text,
                "emotion": "direct_search",
                "timestamp": current_time,
                "search_type": "direct"
            })
            
            return {
                "emotion": "direct_search",
                "recommendations": recommendations,
                "confidence": 1.0,
                "search_type": "direct"
            }
        else:
            emotion = detect_emotion_with_learning(text)
            confidence = get_confidence_score(text)
            
            recommendations = get_recommendations(emotion, request.category, 10)
            
            # Apply sorting
            if request.sort == 'asc':
                recommendations.sort(key=lambda x: x['title'])
            elif request.sort == 'desc':
                recommendations.sort(key=lambda x: x['title'], reverse=True)
            
            search_history.append({
                "text": text,
                "emotion": emotion,
                "timestamp": current_time,
                "search_type": "emotion",
                "confidence": confidence
            })
            
            return {
                "emotion": emotion,
                "recommendations": recommendations,
                "confidence": confidence,
                "search_type": "emotion"
            }
            
    except Exception as e:
        logger.error(f"Error in emotion analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations")
async def get_emotion_recommendations(request: RecommendationRequest):
    """Get recommendations for a specific emotion"""
    try:
        recommendations = get_recommendations(
            request.emotion,
            request.category,
            request.limit
        )
        
        return {
            "emotion": request.emotion,
            "songs": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def direct_search(request: SearchRequest):
    """Direct search for songs/artists"""
    try:
        recommendations = search_directly(request.query, request.limit)
        return {
            "query": request.query,
            "results": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error in direct search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_search_history(limit: int = 20):
    """Get search history"""
    return {
        "history": search_history[-limit:][::-1]
    }

@app.delete("/api/history")
async def clear_search_history():
    """Clear search history"""
    global search_history
    search_history = []
    return {"message": "Search history cleared"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "emotion_detector": "initialized",
            "music_recommender": "initialized", 
            "active_learning": "initialized"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)