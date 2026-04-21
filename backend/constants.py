# constants.py
EMOJI_EMOTION_MAP = {
    # Happy emojis
    '😊': 'happy', '😂': 'happy', '🤣': 'happy', '😃': 'happy', '😄': 'happy',
    '😁': 'happy', '😆': 'happy', '😎': 'happy', '🤠': 'happy', '🥳': 'happy',
    '😇': 'happy', '🙂': 'happy', '😀': 'happy', '😺': 'happy', '😸': 'happy',
    '😹': 'happy', '😻': 'happy', '💃': 'happy', '🕺': 'happy', '🎉': 'happy',
    '🎊': 'happy', '✨': 'happy', '🎈': 'happy', '🥰': 'love',
    
    # Love emojis
    '😍': 'love', '❤️': 'love', '💕': 'love', '💖': 'love', '💞': 'love',
    '💘': 'love', '💓': 'love', '💗': 'love', '💙': 'love', '💚': 'love',
    '💛': 'love', '💜': 'love', '🧡': 'love', '🤍': 'love', '🤎': 'love',
    '💑': 'love', '👩‍❤️‍👨': 'love', '👨‍❤️‍👨': 'love', '👩‍❤️‍👩': 'love', '💏': 'love',
    '👩‍❤️‍💋‍👨': 'love', '👨‍❤️‍💋‍👨': 'love', '👩‍❤️‍💋‍👩': 'love', '🫶': 'love', '💋': 'love',
    
    # Sad emojis
    '😢': 'sad', '😭': 'sad', '😔': 'sad', '😞': 'sad', '😟': 'sad',
    '😕': 'sad', '🙁': 'sad', '☹️': 'sad', '😣': 'sad', '😖': 'sad',
    '😫': 'sad', '😩': 'sad', '🥺': 'sad', '😿': 'sad', '😾': 'sad',
    '💔': 'sad',
    
    # Angry emojis
    '😡': 'angry', '🤬': 'angry', '😠': 'angry', '😤': 'angry', '👿': 'angry',
    '😾': 'angry', '💢': 'angry',
    
    
    # Excited emojis
    '😃': 'excited', '😄': 'excited', '😁': 'excited', '😆': 'excited',
    '🤩': 'excited', '🥳': 'excited', '🎉': 'excited', '🎊': 'excited',
    '🎁': 'excited', '🎂': 'excited', '🎈': 'excited', '✨': 'excited',
    '⚡': 'excited', '🚀': 'excited', '🔥': 'excited', '💫': 'excited',
    
    # Anxious emojis
    '😨': 'anxious', '😰': 'anxious', '😥': 'anxious', '😓': 'anxious',
    '😬': 'anxious', '😳': 'anxious', '🤯': 'anxious', '🥶': 'anxious',
    '😵': 'anxious', '😵‍💫': 'anxious',
    
    # Other emotions
    '😐': 'neutral', '😶': 'neutral', '😑': 'neutral', '🙄': 'neutral',
    '😯': 'surprised', '😲': 'surprised', '🥴': 'confused', '😕': 'confused',
    '🤔': 'confused', '😷': 'sick', '🤒': 'sick', '🤕': 'sick', '🤢': 'disgusted',
    '🤮': 'disgusted', '😈': 'mischievous', '👻': 'playful', '🤡': 'playful',
    '💩': 'playful', '👏': 'proud', '🤝': 'friendly', '🙌': 'excited',
    '👍': 'friendly', '👎': 'angry', '❤️‍🔥': 'love', '❤️‍🩹': 'sad',
    '🤗': 'friendly', '🤲': 'calm', '🙏': 'calm', '✌️': 'happy',
    
    # Additional emojis
    '💬': 'friendly',  # speech bubble
    '💷': 'neutral',   # pound banknote
}

EMOTION_CATEGORY_MAPPING = {
    'happy': ['happy', 'excited', 'playful', 'joyful'],
    'sad': ['sad', 'disappointed', 'heartbroken', 'lonely'],
    'angry': ['angry', 'frustrated', 'irritated', 'annoyed'],
    'calm': ['calm', 'peaceful', 'relaxed', 'serene'],
    'love': ['love', 'romantic', 'affectionate', 'loving'],
    'excited': ['excited', 'energetic', 'enthusiastic', 'thrilled'],
    'frustrated': ['frustrated', 'annoyed', 'irritated', 'angry'],
    'anxious': ['anxious', 'nervous', 'worried', 'stressed'],
    'neutral': ['neutral', 'normal', 'okay', 'fine'],
    'sleepy': ['sleepy', 'tired', 'exhausted', 'drowsy'],
    'hungry': ['hungry', 'starving', 'famished'],
    'thirsty': ['thirsty', 'parched', 'dehydrated'],
    'sick': ['sick', 'ill', 'unwell', 'feverish'],
    'bored': ['bored', 'uninterested', 'indifferent'],
    'surprised': ['surprised', 'shocked', 'astonished', 'amazed'],
    'confused': ['confused', 'puzzled', 'bewildered', 'perplexed'],
    'proud': ['proud', 'accomplished', 'achieving', 'successful'],
    'jealous': ['jealous', 'envious', 'covetous', 'resentful'],
    'nostalgic': ['nostalgic', 'sentimental', 'remembering', 'reminiscent'],
    'hopeful': ['hopeful', 'optimistic', 'expectant', 'positive'],
    'disgusted': ['disgusted', 'repulsed', 'revolted', 'sickened'],
    'blessed': ['blessed', 'fortunate', 'lucky', 'grateful'],
    'dizzy': ['dizzy', 'lightheaded', 'woozy', 'vertigo'],
    'hot': ['hot', 'warm', 'sweltering', 'overheated'],
    'cold': ['cold', 'chilly', 'freezing', 'frigid'],
    'mischievous': ['mischievous', 'naughty', 'playful', 'misbehaving'],
    'playful': ['playful', 'fun', 'frolicsome', 'frisky'],
    'focused': ['focused', 'concentrated', 'attentive', 'engaged'],
    'loving': ['loving', 'caring', 'affectionate', 'devoted'],
    'friendly': ['friendly', 'sociable', 'amicable', 'companionable']
}

EMOTION_TO_MUSIC_MAPPING = {
    'happy': ['happy', 'upbeat', 'energetic', 'dance', 'party'],
    'sad': ['sad', 'melancholic', 'emotional', 'heartbreak', 'ballad'],
    'angry': ['angry', 'intense', 'aggressive', 'rock', 'metal'],
    'calm': ['calm', 'peaceful', 'relaxing', 'ambient', 'meditation'],
    'love': ['love', 'romantic', 'passionate', 'slow', 'intimate'],
    'excited': ['excited', 'energetic', 'upbeat', 'party', 'celebration'],
    'anxious': ['calm', 'soothing', 'relaxing', 'ambient', 'meditation'],
    'sleepy': ['calm', 'soothing', 'relaxing', 'lullaby', 'sleep'],
    'hungry': ['fun', 'upbeat', 'playful', 'food', 'celebration'],
    'thirsty': ['refreshing', 'cool', 'smooth', 'chill', 'relaxing'],
    'sick': ['comforting', 'soothing', 'healing', 'calm', 'soft'],
    'bored': ['energetic', 'upbeat', 'exciting', 'party', 'dance'],
    'surprised': ['exciting', 'dramatic', 'epic', 'orchestral', 'cinematic'],
    'confused': ['calm', 'soothing', 'clear', 'simple', 'minimal'],
    'proud': ['triumphant', 'victorious', 'inspiring', 'epic', 'motivational'],
    'jealous': ['intense', 'emotional', 'dramatic', 'heartbreak', 'ballad'],
    'nostalgic': ['nostalgic', 'retro', 'oldies', 'memories', 'sentimental'],
    'hopeful': ['inspiring', 'uplifting', 'optimistic', 'positive', 'motivational'],
    'disgusted': ['intense', 'aggressive', 'powerful', 'rock', 'metal'],
    'blessed': ['spiritual', 'inspiring', 'uplifting', 'gospel', 'worship'],
    'dizzy': ['calm', 'steady', 'grounding', 'meditation', 'ambient'],
    'hot': ['cool', 'refreshing', 'chill', 'smooth', 'relaxing'],
    'cold': ['warm', 'cozy', 'comforting', 'soft', 'gentle'],
    'mischievous': ['playful', 'fun', 'quirky', 'funky', 'unexpected'],
    'playful': ['fun', 'upbeat', 'playful', 'happy', 'energetic'],
    'focused': ['concentrated', 'minimal', 'ambient', 'instrumental', 'study'],
    'loving': ['romantic', 'intimate', 'soft', 'passionate', 'slow'],
    'friendly': ['social', 'upbeat', 'happy', 'community', 'together'],
    'neutral': ['neutral', 'balanced', 'varied', 'mixed', 'general']
}

EMOTION_SIMILARITY = {
    'happy': ['excited', 'love', 'happy'],
    'sad': ['frustrated', 'anxious', 'sad'],
    'angry': ['frustrated', 'anxious', 'angry'],
    'calm': ['love', 'calm', 'happy'],
    'love': ['happy', 'love', 'calm'],
    'excited': ['happy', 'excited', 'love'],
    'frustrated': ['angry', 'frustrated', 'sad'],
    'anxious': ['sad', 'anxious', 'frustrated'],
    'neutral': ['happy', 'calm', 'love']
}