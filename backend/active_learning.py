#active_learning.py

import pandas as pd
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import logging

logger = logging.getLogger(__name__)

def preprocess_text(text):
    """Text preprocessing helper function"""
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    
    # Handle common contractions
    contractions = {
        "im": "i am", "dont": "do not", "cant": "cannot", "wont": "will not",
        "shouldnt": "should not", "wouldnt": "would not", "couldnt": "could not",
        "isnt": "is not", "arent": "are not", "wasnt": "was not", "werent": "were not",
        "havent": "have not", "hasnt": "has not", "hadnt": "had not", "doesnt": "does not",
        "didnt": "did not", "ill": "i will", "youll": "you will", "theyll": "they will",
        "weve": "we have", "ive": "i have", "youve": "you have", "theyve": "they have",
        "im": "i am", "youre": "you are", "theyre": "they are", "were": "we are",
        "thats": "that is", "whats": "what is", "wheres": "where is", "whos": "who is",
        "hows": "how is", "shes": "she is", "hes": "he is", "its": "it is"
    }
    
    for contraction, full in contractions.items():
        text = text.replace(contraction, full)
    
    return text

class ActiveLearningSystem:
    def __init__(self, dataset_path='data/emotion_dataset.csv'):
        self.dataset_path = dataset_path
        self.vectorizer = TfidfVectorizer(max_features=5000)
        
    def text_exists_in_dataset(self, text):
        """Check if text already exists in dataset (case insensitive)"""
        try:
            df = pd.read_csv(self.dataset_path)
            processed_text = preprocess_text(text)
            existing_texts = df['text'].apply(preprocess_text).tolist()
            return processed_text in existing_texts
        except:
            return False
        
    def find_exact_emotion(self, text):
        """Find exact emotion if text exists in dataset"""
        try:
            df = pd.read_csv(self.dataset_path)
            processed_text = preprocess_text(text)
            
            for idx, row in df.iterrows():
                if preprocess_text(row['text']) == processed_text:
                    return row['emotion'], 1.0  # Exact match found
            
            return None, 0.0
        except Exception as e:
            logger.error(f"Error finding exact emotion: {e}")
            return None, 0.0
        
    def find_similar_emotion(self, new_text, threshold=0.3):
        """Find if new text is similar to existing emotions"""
        try:
            # First check for exact match
            exact_emotion, exact_similarity = self.find_exact_emotion(new_text)
            if exact_emotion:
                return exact_emotion, exact_similarity
            
            # Load existing dataset
            df = pd.read_csv(self.dataset_path)
            
            # Preprocess new text
            processed_new = preprocess_text(new_text)
            
            # Vectorize existing data and new text
            all_texts = list(df['text']) + [processed_new]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity with existing emotions
            new_vector = tfidf_matrix[-1]
            existing_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(new_vector, existing_vectors)[0]
            max_similarity = np.max(similarities)
            most_similar_idx = np.argmax(similarities)
            
            if max_similarity > threshold:
                similar_emotion = df.iloc[most_similar_idx]['emotion']
                return similar_emotion, max_similarity
            else:
                return None, max_similarity
                
        except Exception as e:
            logger.error(f"Error finding similar emotion: {e}")
            return None, 0
    
    def add_to_dataset(self, text, emotion):
        """Add new text-emotion pair to dataset ONLY if it doesn't exist"""
        try:
            # Load existing data
            try:
                df = pd.read_csv(self.dataset_path)
            except:
                df = pd.DataFrame(columns=['text', 'emotion'])
            
            # Check if already exists (case insensitive)
            if self.text_exists_in_dataset(text):
                logger.info(f"Text already exists in dataset, not adding: '{text}'")
                return False
                
            # Add new entry
            new_entry = pd.DataFrame({'text': [text], 'emotion': [emotion]})
            df = pd.concat([df, new_entry], ignore_index=True)
            
            # Save updated dataset
            df.to_csv(self.dataset_path, index=False)
            logger.info(f"Added new entry: '{text}' -> {emotion}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to dataset: {e}")
            return False

# Global instance
active_learner = ActiveLearningSystem()