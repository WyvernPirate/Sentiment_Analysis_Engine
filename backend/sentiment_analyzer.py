import torch
import json
import re
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from models import db, SocialMediaPost, SentimentAnalysis
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SetswanaEnglishSentimentAnalyzer:
    def __init__(self):
        self.model_path = Config.SENTIMENT_MODEL_PATH
        self.fallback_model = Config.FALLBACK_MODEL
        self.sentiment_pipeline = self._load_model()
        
        # Setswana language indicators
        self.setswana_words = {
            'ke', 'ga', 'le', 'mo', 'go', 'ba', 'se', 'di', 'bo', 'ma', 'o', 'a',
            'thata', 'sentle', 'botlhoko', 'monate', 'rata', 'sa', 'dire', 'raya',
            'mmuso', 'setšhaba', 'batho', 'polotiki', 'kgethololo', 'palamente'
        }
        
        # Political entities and keywords
        self.political_entities = {
            'parties': ['BDP', 'UDC', 'BCP', 'AP', 'Botswana Democratic Party', 
                       'Umbrella for Democratic Change', 'Botswana Congress Party'],
            'leaders': ['Masisi', 'Boko', 'Saleshando', 'Khama', 'Mogae'],
            'locations': ['Gaborone', 'Francistown', 'Maun', 'Kasane', 'Serowe'],
            'institutions': ['Parliament', 'Palamente', 'Government', 'Mmuso']
        }
        
        # Political keywords for context
        self.political_keywords = Config.POLITICAL_KEYWORDS
    
    def _load_model(self):
        """Load sentiment analysis model"""
        try:
            import os
            if os.path.exists(self.model_path) and os.path.exists(os.path.join(self.model_path, "config.json")):
                logger.info(f"Loading custom Setswana model from {self.model_path}")
                model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
                tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            else:
                logger.info(f"Custom model not found, using fallback: {self.fallback_model}")
                return pipeline("sentiment-analysis", model=self.fallback_model)
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Using default sentiment analysis pipeline")
            return pipeline("sentiment-analysis")
    
    def detect_language_and_code_switching(self, text):
        """Detect language and code-switching in text"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        setswana_count = sum(1 for word in words if word in self.setswana_words)
        total_words = len(words)
        
        if total_words == 0:
            return "unknown", False
        
        setswana_ratio = setswana_count / total_words
        
        if setswana_ratio > 0.6:
            return "Setswana", False
        elif setswana_ratio > 0.1:
            return "Setswana-English", True
        else:
            return "English", False
    
    def extract_political_entities(self, text):
        """Extract political entities and keywords from text"""
        text_lower = text.lower()
        found_entities = []
        found_keywords = []
        
        # Check for political entities
        for category, entities in self.political_entities.items():
            for entity in entities:
                if entity.lower() in text_lower:
                    found_entities.append({
                        'entity': entity,
                        'category': category
                    })
        
        # Check for political keywords
        for keyword in self.political_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_entities, found_keywords
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text with political context"""
        try:
            # Run sentiment analysis
            result = self.sentiment_pipeline(text)
            
            # Extract results
            label = result[0]['label'].lower()
            confidence = float(result[0]['score'])
            
            # Map model outputs to consistent format
            sentiment_mapping = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'label_2': 'positive',  # Custom model mapping
                'label_1': 'neutral',
                'label_0': 'negative'
            }
            
            sentiment = sentiment_mapping.get(label, label)
            
            # Detect language and code-switching
            detected_language, code_switching = self.detect_language_and_code_switching(text)
            
            # Extract political context
            political_entities, political_keywords = self.extract_political_entities(text)
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'detected_language': detected_language,
                'code_switching_detected': code_switching,
                'political_entities': political_entities,
                'political_keywords': political_keywords,
                'model_used': 'custom' if 'custom' in str(self.sentiment_pipeline.model) else 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None
    
    def analyze_post(self, post_id):
        """Analyze sentiment for a specific social media post"""
        try:
            # Get the post
            post = SocialMediaPost.query.get(post_id)
            if not post:
                logger.error(f"Post {post_id} not found")
                return None
            
            # Check if already analyzed
            existing_analysis = SentimentAnalysis.query.filter_by(post_id=post_id).first()
            if existing_analysis:
                logger.info(f"Post {post_id} already analyzed")
                return existing_analysis.to_dict()
            
            # Analyze sentiment
            analysis_result = self.analyze_sentiment(post.text)
            if not analysis_result:
                return None
            
            # Save analysis to database
            sentiment_analysis = SentimentAnalysis(
                post_id=post_id,
                sentiment=analysis_result['sentiment'],
                confidence=analysis_result['confidence'],
                detected_language=analysis_result['detected_language'],
                code_switching_detected=analysis_result['code_switching_detected'],
                political_keywords=json.dumps(analysis_result['political_keywords']),
                political_entities=json.dumps(analysis_result['political_entities']),
                model_used=analysis_result['model_used'],
                model_version='1.0'
            )
            
            db.session.add(sentiment_analysis)
            db.session.commit()
            
            logger.info(f"Successfully analyzed post {post_id}")
            return sentiment_analysis.to_dict()
            
        except Exception as e:
            logger.error(f"Error analyzing post {post_id}: {str(e)}")
            db.session.rollback()
            return None
    
    def analyze_unprocessed_posts(self, batch_size=50):
        """Analyze all unprocessed posts"""
        try:
            # Get unprocessed posts
            unprocessed_posts = db.session.query(SocialMediaPost)\
                .outerjoin(SentimentAnalysis)\
                .filter(SentimentAnalysis.id.is_(None))\
                .limit(batch_size)\
                .all()
            
            logger.info(f"Found {len(unprocessed_posts)} unprocessed posts")
            
            processed_count = 0
            for post in unprocessed_posts:
                result = self.analyze_post(post.id)
                if result:
                    processed_count += 1
            
            logger.info(f"Successfully processed {processed_count} posts")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            return 0

# Global analyzer instance
analyzer = SetswanaEnglishSentimentAnalyzer()

def analyze_all_unprocessed():
    """Function to analyze all unprocessed posts"""
    return analyzer.analyze_unprocessed_posts()