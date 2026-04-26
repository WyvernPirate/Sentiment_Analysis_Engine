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
    
    # Collection provider strategy
    SOCIAL_PROVIDER = os.environ.get('SOCIAL_PROVIDER', 'brightdata')

    # Bright Data collector integration
    BRIGHTDATA_API_TOKEN = os.environ.get('BRIGHTDATA_API_TOKEN')
    BRIGHTDATA_COLLECTOR_URL = os.environ.get('BRIGHTDATA_COLLECTOR_URL')
    BRIGHTDATA_TIMEOUT_SECONDS = int(os.environ.get('BRIGHTDATA_TIMEOUT_SECONDS', '60'))

    # Apify integration (query-based search collection)
    APIFY_API_TOKEN = os.environ.get('APIFY_API_TOKEN')
    APIFY_ACTOR_ID = os.environ.get('APIFY_ACTOR_ID')
    APIFY_TIMEOUT_SECONDS = int(os.environ.get('APIFY_TIMEOUT_SECONDS', '120'))
    APIFY_WAIT_FOR_FINISH_SECONDS = int(os.environ.get('APIFY_WAIT_FOR_FINISH_SECONDS', '120'))

    # Twikit integration (query-based search via authenticated account)
    TWIKIT_USERNAME = os.environ.get('TWIKIT_USERNAME')
    TWIKIT_EMAIL = os.environ.get('TWIKIT_EMAIL')
    TWIKIT_PASSWORD = os.environ.get('TWIKIT_PASSWORD')
    TWIKIT_COOKIES_PATH = os.environ.get('TWIKIT_COOKIES_PATH', 'data/twikit_cookies.json')
    TWIKIT_LANGUAGE = os.environ.get('TWIKIT_LANGUAGE', 'en-US')
    TWIKIT_ENABLE_UI_METRICS = os.environ.get('TWIKIT_ENABLE_UI_METRICS', 'true').lower() == 'true'
    
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

    # Feature toggles
    # Set to True to enable Setswana-English code-switching detection and
    # lexicon-enhanced analysis. Default is False for baseline deliverable.
    USE_CODE_SWITCHING = os.environ.get('USE_CODE_SWITCHING', 'false').lower() == 'true'
    # Baseline model path (scikit-learn pipeline). Used when transformers is not available.
    BASELINE_MODEL_PATH = os.environ.get('BASELINE_MODEL_PATH') or './models/baseline_sentiment_model.joblib'