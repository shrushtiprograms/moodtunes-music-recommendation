"""Train the emotion classification model."""
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report
import os
from typing import Tuple, Dict, Any
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_default_dataset() -> pd.DataFrame:
    """Create default emotion dataset if needed."""
    data = {
        'text': [
            "I feel great today! 😄", 
            "This makes me so angry 😠",
            "I'm devastated by the news 😢",
            "Such a peaceful evening 🌙",
            "I'm deeply in love ❤️",
            "Feeling excited about the trip 🎉",
            "This situation is frustrating 😣",
            "I feel anxious and worried 😟",
            "What a beautiful day 🌞",
            "Heartbroken after the breakup 💔",
            "Smile :) 😊",
            "Pleading Face 🥺",
            "Rolling on the Floor Laughing 🤣",
            "Smiling Face with Heart-Eyes 😍",
            "Folded Hands 🙏",
            "I love listening to thunder by Imagine Dragons 🎵",
            "Sad love songs 😢",
            "Golden ages old songs 🎻",
            "Feel like I'm about to get explosive emotions 💥",
            "So much inner healing 🌿"
        ],
        'emotion': [
            'happy', 'angry', 'sad', 'calm', 'love', 
            'excited', 'frustrated', 'anxious', 'happy', 'sad',
            'happy', 'sad', 'happy', 'love', 'calm',
            'happy', 'sad', 'calm', 'angry', 'calm'
        ]
    }
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=['text'], inplace=True)
    return df

def load_dataset() -> pd.DataFrame:
    """Load dataset from CSV file in data folder."""
    csv_paths = [
        'data/emotion_dataset.csv',
        'emotion_dataset.csv',
        'dataset/emotion_dataset.csv'
    ]
    
    for path in csv_paths:
        try:
            if os.path.exists(path):
                df = pd.read_csv(path)
                logger.info(f"Loaded dataset from {path} with {len(df)} rows")
                
                # Check required columns
                if 'text' in df.columns and 'emotion' in df.columns:
                    return df
                else:
                    logger.warning(f"CSV file {path} missing required columns 'text' or 'emotion'")
                    # Try to use first two columns if standard names not found
                    if len(df.columns) >= 2:
                        df = df.rename(columns={df.columns[0]: 'text', df.columns[1]: 'emotion'})
                        return df
                    
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
    
    # If no CSV found, create default dataset
    logger.info("No CSV file found. Creating default dataset.")
    df = create_default_dataset()
    
    # Save the default dataset
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/emotion_dataset.csv', index=False)
    
    return df

def load_music_dataset() -> pd.DataFrame:
    """Load music dataset from CSV file in data folder."""
    csv_paths = [
        'data/music_dataset.csv',
        'music_dataset.csv',
        'dataset/music_dataset.csv'
    ]
    
    for path in csv_paths:
        try:
            if os.path.exists(path):
                music_df = pd.read_csv(path)
                logger.info(f"Loaded music dataset from {path} with {len(music_df)} rows")
                return music_df
        except Exception as e:
            logger.warning(f"Failed to load music dataset from {path}: {e}")
    
    logger.info("No music dataset found. Continuing without it.")
    return pd.DataFrame()

def train_and_save_model() -> Tuple[bool, str]:
    """Train and save the model with evaluation."""
    try:
        # Load emotion dataset
        df = load_dataset()
        
        # Load music dataset
        music_df = load_music_dataset()
        
        # Display dataset info
        logger.info(f"Training dataset shape: {df.shape}")
        logger.info(f"Dataset columns: {df.columns.tolist()}")
        logger.info(f"Emotions distribution:\n{df['emotion'].value_counts()}")
        
        if not music_df.empty:
            logger.info(f"Music dataset shape: {music_df.shape}")
            logger.info(f"Music dataset columns: {music_df.columns.tolist()}")
        
        # FIX: Filter out emotions with only 1 sample
        emotion_counts = df['emotion'].value_counts()
        valid_emotions = emotion_counts[emotion_counts >= 2].index
        df_filtered = df[df['emotion'].isin(valid_emotions)]
        
        logger.info(f"Original dataset: {len(df)} samples, {len(df['emotion'].unique())} emotions")
        logger.info(f"Filtered dataset: {len(df_filtered)} samples, {len(df_filtered['emotion'].unique())} emotions")
        logger.info(f"Removed {len(df) - len(df_filtered)} samples from rare emotions")
        
        # Check if we have enough data to train
        if len(df_filtered) < 5:
            error_msg = f"Not enough data to train model. Only {len(df_filtered)} samples available."
            logger.error(error_msg)
            return False, error_msg
        
        # Use filtered dataset
        X = df_filtered['text']
        y = df_filtered['emotion']
        
        # Split for validation - now stratify will work
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))),
            ('clf', LinearSVC(dual='auto', C=1.0, random_state=42))
        ])
        
        # Cross-validation
        scores = cross_val_score(model, X_train, y_train, cv=min(5, len(X_train)))
        logger.info(f"CV Accuracy: {scores.mean():.2f} (+/- {scores.std() * 2:.2f})")
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        logger.info("Validation Report:\n" + classification_report(y_val, y_pred))
        
        # Save model
        os.makedirs('models', exist_ok=True)
        model_path = 'models/emotion_classifier.pkl'
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Also save the vectorizer separately for easier access
        vectorizer_path = 'models/tfidf_vectorizer.pkl'
        joblib.dump(model.named_steps['tfidf'], vectorizer_path)
        logger.info(f"Vectorizer saved to {vectorizer_path}")
        
        # Test the model with some examples
        test_texts = [
            "I feel amazing today!",
            "This is so frustrating",
            "I'm feeling peaceful",
            "I love this song"
        ]
        
        predictions = model.predict(test_texts)
        for text, emotion in zip(test_texts, predictions):
            logger.info(f"Text: '{text}' -> Emotion: {emotion}")
        
        return True, "Model trained successfully"
        
    except Exception as e:
        error_msg = f"Error training model: {e}"
        logger.error(error_msg)
        return False, error_msg
        
def retrain_model() -> Tuple[bool, str]:
    """Retrain with current dataset."""
    try:
        success, message = train_and_save_model()
        if success:
            logger.info("Model retrained successfully")
            return True, "Model retrained successfully"
        else:
            logger.error(f"Retrain failed: {message}")
            return False, message
    except Exception as e:
        error_msg = f"Retrain error: {e}"
        logger.error(error_msg)
        return False, error_msg

def get_model_info() -> Dict[str, Any]:
    """Get information about the current model"""
    try:
        model_path = 'models/emotion_classifier.pkl'
        vectorizer_path = 'models/tfidf_vectorizer.pkl'
        
        model_exists = os.path.exists(model_path)
        vectorizer_exists = os.path.exists(vectorizer_path)
        
        # Load dataset info
        df = load_dataset()
        
        return {
            "model_exists": model_exists,
            "vectorizer_exists": vectorizer_exists,
            "dataset_size": len(df),
            "emotions_count": len(df['emotion'].unique()),
            "emotions_distribution": df['emotion'].value_counts().to_dict(),
            "last_trained": None  # You can add timestamp tracking if needed
        }
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return {
            "model_exists": False,
            "vectorizer_exists": False,
            "dataset_size": 0,
            "emotions_count": 0,
            "emotions_distribution": {},
            "error": str(e)
        }

if __name__ == "__main__":
    success, message = train_and_save_model()
    if success:
        print("✅ " + message)
    else:
        print("❌ " + message)