import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///botswana_sentiment.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Social Media API Keys
    TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    
    FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    
    # Model Configuration
    SENTIMENT_MODEL_PATH = './models/sentiment_model_setswana'
    FALLBACK_MODEL = 'cardiffnlp/twitter-xlm-roberta-base-sentiment-latest'
    
    # Data Collection Configuration
    POLITICAL_KEYWORDS = [
        # English political terms
        'botswana politics', 'BDP', 'UDC', 'BCP', 'AP', 'election', 'parliament',
        'masisi', 'boko', 'saleshando', 'gaborone', 'francistown',
        
        # Setswana political terms
        'polotiki', 'kgethololo', 'palamente', 'mmuso', 'setšhaba',
        'dikgethololo', 'boeteledipele', 'puso', 'batho'
    ]
    
    POLITICAL_HASHTAGS = [
        '#BotswanaPolitics', '#BDP2024', '#UDC2024', '#BotswanaElections',
        '#Masisi', '#Boko', '#BotswanaNews', '#BWPolitics'
    ]
    
    # Redis Configuration (for Celery)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Data Collection Settings
    COLLECTION_INTERVAL_MINUTES = 15  # How often to collect new data
    MAX_TWEETS_PER_COLLECTION = 100
    DATA_RETENTION_DAYS = 30  # How long to keep raw social media data