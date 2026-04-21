# emotion_detection.py 

import joblib
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import emoji
import logging
import os
from collections import Counter
import numpy as np
from scipy.sparse import csr_matrix
from constants import EMOJI_EMOTION_MAP

logger = logging.getLogger(__name__)

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('punkt')
    nltk.download('stopwords')

class EmotionDetector:

    # updated rule_based_detection method:
    def rule_based_detection(self, text):
        if not text or not isinstance(text, str):
            return "neutral"
    
        text_lower = text.lower()
    
    # DEBUG: Print the input text to see what's being processed
        print(f"DEBUG: Processing text: '{text}'")
    
    # Check if input contains only emojis (with possible whitespace)
        emoji_only = True
        for char in text:
            if char not in EMOJI_EMOTION_MAP and not char.isspace():
                emoji_only = False
                break
    
    # DEBUG: Print if it's emoji only
        print(f"DEBUG: Emoji only: {emoji_only}")
    
    # If input contains only emojis (with possible whitespace)
        if emoji_only:
        # Count emojis by emotion
            emotion_counts = {}
            for char in text:
                if char in EMOJI_EMOTION_MAP:
                    emotion = EMOJI_EMOTION_MAP[char]
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    # DEBUG: Print each emoji and its mapped emotion
                    print(f"DEBUG: Emoji '{char}' -> {emotion}")
        
        # DEBUG: Print emotion counts
            print(f"DEBUG: Emotion counts: {emotion_counts}")
        
        # Return emotion with highest count
            if emotion_counts:
            # If we have multiple emotions, return the one with highest count
                result = max(emotion_counts.items(), key=lambda x: x[1])[0]
                print(f"DEBUG: Selected emotion: {result}")
                return result
            else:
                print("DEBUG: No emotions found, returning neutral")
                return "neutral"
    
    # For mixed text and emoji inputs, prioritize emojis
        emoji_emotions = []
        for char in text:
            if char in EMOJI_EMOTION_MAP:
                emotion = EMOJI_EMOTION_MAP[char]
                emoji_emotions.append(emotion)
                # DEBUG: Print each emoji and its mapped emotion
                print(f"DEBUG: Emoji '{char}' -> {emotion}")

    # If we have emojis in the text, use the most frequent emoji emotion
        if emoji_emotions:
            emotion_counter = Counter(emoji_emotions)
            result = emotion_counter.most_common(1)[0][0]
            print(f"DEBUG: Most common emoji emotion: {result}")
            return result
    
    # If no emojis, use keyword matching
        keywords = {
            'happy': ['happy', 'joy', 'joyful', 'excited', 'good', 'great', 'fun', 'smile', 'laugh', 'enjoy', 'friends', 'celebrate', 'celebration', 'dance', 'party','not sad'],
            'sad': ['sad', 'unhappy', 'cry', 'tears', 'depressed', 'lonely', 'miss', 'alone', 'heartbroken', 'broken', 'upset', 'miserable', 'unfortunate', 'grief', 'sorrow','not happy'],
            'angry': ['angry', 'mad', 'hate', 'furious', 'annoyed', 'frustrated', 'irritated', 'outraged', 'rage', 'fury', 'temper', 'hostile'],
            'calm': ['calm', 'peaceful', 'relax', 'chill', 'quiet', 'serene', 'tranquil', 'peace', 'still', 'composed', 'collected'],
            'love': ['love', 'romantic', 'heart', 'crush', 'adore', 'affection', 'lovely', 'beloved', 'darling', 'sweetheart', 'passion', 'romance', 'cherish'],
            'excited': ['excited', 'thrilled', 'pumped', 'energetic', 'anticipate', 'looking forward', 'eager', 'enthusiastic', 'keen', 'avid'],
            'anxious': ['anxious', 'nervous', 'worried', 'stressed', 'scared', 'afraid', 'tense', 'apprehensive', 'concerned', 'uneasy', 'panic'],
            'neutral': ['ok', 'fine', 'alright', 'normal', 'regular', 'usual', 'ordinary', 'average', 'moderate'],
            'friendly': ['friendly', 'friendship', 'companion', 'buddy', 'pal', 'mate', 'amicable', 'sociable', 'outgoing'],
            'sick': ['sick', 'unwell', 'not well', 'ill', 'fever', 'headache', 'nauseous', 'vomit', 'dizzy', 'pain', 'ache']
        }
    
        for emotion, words in keywords.items():
            for word in words:
                if word in text_lower:
                    print(f"DEBUG: Keyword '{word}' found -> {emotion}")
                    return emotion
    
        print("DEBUG: No keywords found, returning neutral")
        return "neutral"
    
    def __init__(self):
        model_path = os.path.join('models', 'emotion_classifier.pkl')
        vectorizer_path = os.path.join('models', 'tfidf_vectorizer.pkl')
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess(self, text):
        if not text or not isinstance(text, str):
            return ""
    
        # Convert to lowercase
        text = text.lower()
    
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
    
        # Handle common contractions and synonyms
        contractions = {
            "im": "i am", "dont": "do not", "cant": "cannot", "wont": "will not",
            "shouldnt": "should not", "wouldnt": "would not", "couldnt": "could not",
            "isnt": "is not", "arent": "are not", "wasnt": "was not", "werent": "were not",
            "havent": "have not", "hasnt": "has not", "hadnt": "had not", "doesnt": "does not",
            "didnt": "did not", "ill": "i will", "youll": "you will", "theyll": "they will",
            "weve": "we have", "ive": "i have", "youve": "you have", "theyve": "they have",
            "im": "i am", "youre": "you are", "theyre": "they are", "were": "we are",
            "thats": "that is", "whats": "what is", "wheres": "where is", "whos": "who is",
            "hows": "how is", "shes": "she is", "hes": "he is", "its": "it is",
            "feel": "feeling", "feels": "feeling", "felt": "feeling"
        }
    
        words = text.split()
        processed_words = []
        for word in words:
            if word in contractions:
                processed_words.extend(contractions[word].split())
            else:
                processed_words.append(word)

        return ' '.join(processed_words)
    
    def detect(self, text):
        # First try rule-based detection for speed and reliability
        rule_based_result = self.rule_based_detection(text)
    
        # TEMPORARY: Skip model prediction to test rule-based
        return rule_based_result
    
        # If we have a model, try to use it
        if self.model is not None and self.vectorizer is not None:
            try:
                processed = self.preprocess(text)
                if isinstance(processed, str):  # Make sure it's text, not a vector
                    processed_vector = self.vectorizer.transform([processed])
                    model_result = self.model.predict(processed_vector)[0]
                
                    # You can add confidence checking here if needed
                    return model_result
                else:
                    # If somehow we got a vector, fall back to rule-based
                    return rule_based_result
            except Exception as e:
                print(f"Model prediction error: {e}")
                # Fall back to rule-based detection
                return rule_based_result
        else:
            # No model available, use rule-based
            return rule_based_result

detector = EmotionDetector()

def detect_emotion(text):
    """Main function to detect emotion from text"""
    return detector.detect(text)

# Test function
def test_emotion_detection():
    """Test the emotion detection"""
    test_cases = [
        "I'm so happy today! 😊",
        "Feeling sad and lonely 😢",
        "This makes me angry 😡",
        "So peaceful right now 🧘",
        "I am in love with you ❤️",
        "Excited for the party! 🎉",
        "Frustrated with work 😤",
        "Anxious about tomorrow 😰",
        "Neutral day today 😐",
        "Feeling sleepy 😴",
        "I'm hungry 🍔",
        "Thirsty for some juice 🥤",
        "Feeling sick today 🤒",
        "Bored 😑",
        "OMG! Can't believe it 😲",
        "Confused 🤷",
        "Proud of myself 👏",
        "Jealous 💚",
        "Missing old times 🕰️",
        "Hopeful for the future 🌈"
    ]
    
    print("Testing Emotion Detection:")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        emotion = detect_emotion(text)
        print(f"{i:2d}. '{text}' -> {emotion}")
    
    print("=" * 50)
    print("Test completed successfully!")

# Run test if this file is executed directly
if __name__ == "__main__":
    test_emotion_detection()

# Helper function for external use
def preprocess_text(text):
    """Public preprocessing function for external use"""
    detector = EmotionDetector()
    return detector.preprocess(text)

def get_confidence_score(text):
    """Get confidence score for prediction"""
    try:
        # For emoji-only inputs, return high confidence
        emoji_only = True
        for char in text:
            if char not in EMOJI_EMOTION_MAP and not char.isspace():
                emoji_only = False
                break
        
        if emoji_only:
            return 0.9  # High confidence for emoji-only inputs
        
        processed = preprocess_text(text)
        if not processed:
            return 0.3
        
        # Use the detector's vectorizer
        processed_vector = detector.vectorizer.transform([processed])
        
        # For SVM models, use decision function
        if hasattr(detector.model, 'decision_function'):
            decision_scores = detector.model.decision_function(processed_vector)
            confidence = np.max(decision_scores) - np.min(decision_scores)
            return float(confidence) / 10.0  # Normalize
        
        # For other models, use prediction probabilities
        elif hasattr(detector.model, 'predict_proba'):
            probabilities = detector.model.predict_proba(processed_vector)[0]
            confidence = np.max(probabilities)
            return confidence
        
        else:
            return 0.5
            
    except Exception as e:
        logger.error(f"Error getting confidence score: {e}")
        return 0.3
    
def suggest_emotion(text):
    """Automatically suggest emotion based on keywords"""
    keyword_patterns = {
        'happy': r'\b(happy|joy|fun|smile|laugh|great|good|awesome|yay|😊|😂|🎉)\b',
        'sad': r'\b(sad|unhappy|cry|tears|depressed|lonely|miss|heartbroken|😢|😭|💔)\b',
        'angry': r'\b(angry|mad|hate|furious|annoyed|frustrated|irritated|😡|🤬|💢)\b',
        'love': r'\b(love|romantic|heart|crush|adore|affection|care|beloved|❤️|💕|😍)\b',
        'excited': r'\b(excited|thrilled|pumped|energetic|anticipate|looking forward|🎊|✨|🚀)\b',
        'calm': r'\b(calm|peaceful|relax|chill|quiet|serene|tranquil|😌|🧘|🌿)\b',
        'anxious': r'\b(anxious|nervous|worried|stressed|scared|afraid|panic|😰|😨|😟)\b',
    }
    
    text_lower = text.lower()
    
    for emotion, pattern in keyword_patterns.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return emotion
    
    return None