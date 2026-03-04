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
                self.pipeline_type = 'hf'
                return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            else:
                logger.info(f"Custom model not found, using fallback: {self.fallback_model}")
                self.pipeline_type = 'hf'
                return pipeline("sentiment-analysis", model=self.fallback_model)
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Using default sentiment analysis pipeline")
            # Try to load a lightweight baseline model (scikit-learn) if available
            try:
                import joblib
                baseline_path = getattr(Config, 'BASELINE_MODEL_PATH', './models/baseline_sentiment_model.joblib')
                if os.path.exists(baseline_path):
                    logger.info(f"Loading baseline sklearn model from {baseline_path}")
                    model = joblib.load(baseline_path)
                    self.pipeline_type = 'sklearn'
                    return model
                else:
                    logger.warning(f"Baseline model not found at {baseline_path}")
            except Exception as ie:
                logger.error(f"Error loading baseline model: {ie}")

            # As a last resort, attempt HF default pipeline (may fail if transformers missing)
            try:
                self.pipeline_type = 'hf'
                return pipeline("sentiment-analysis")
            except Exception as final_e:
                logger.error(f"Final fallback failed: {final_e}")
                return None
    
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
            # Run sentiment analysis depending on pipeline type
            label = None
            confidence = 0.0

            if getattr(self, 'pipeline_type', None) == 'sklearn':
                # sklearn pipeline: predict returns integer labels
                try:
                    pred = self.sentiment_pipeline.predict([text])
                    label_idx = int(pred[0])
                    # Try to get probability if available
                    if hasattr(self.sentiment_pipeline, 'predict_proba'):
                        probs = self.sentiment_pipeline.predict_proba([text])[0]
                        confidence = float(max(probs))
                    else:
                        confidence = 0.8

                    # Map numeric labels to text
                    label_mapping_idx = {0: 'label_0', 1: 'label_1', 2: 'label_2'}
                    label = label_mapping_idx.get(label_idx, str(label_idx))
                except Exception as e:
                    logger.error(f"Error running sklearn pipeline: {e}")
                    return None
            elif getattr(self, 'pipeline_type', None) == 'hf':
                result = self.sentiment_pipeline(text)
                # Extract results
                label = result[0]['label'].lower()
                confidence = float(result[0]['score'])
            else:
                logger.error("No sentiment pipeline available")
                return None
            
            # Map model outputs to consistent format
            sentiment_mapping = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'label_0': 'negative',  # CardiffNLP/Twitter-RoBERTa 0: Negative
                'label_1': 'neutral',   # CardiffNLP/Twitter-RoBERTa 1: Neutral
                'label_2': 'positive',  # CardiffNLP/Twitter-RoBERTa 2: Positive
                'negative': 'negative',
                'neutral': 'neutral',
                'positive': 'positive'
            }
            
            # For some models, the label might be uppercase
            sentiment = sentiment_mapping.get(label.lower(), label.lower())
            
            # Detect language and code-switching and extract political context
            # Only perform these when the feature toggle is enabled. For the
            # baseline deliverable we keep code-switching/lexicon logic optional.
            if getattr(Config, 'USE_CODE_SWITCHING', False):
                detected_language, code_switching = self.detect_language_and_code_switching(text)
                political_entities, political_keywords = self.extract_political_entities(text)
            else:
                # Default to English-only analysis for baseline
                detected_language, code_switching = 'English', False
                political_entities, political_keywords = [], []
            
            # Determine model_used string
            if getattr(self, 'pipeline_type', None) == 'sklearn':
                model_used = 'baseline'
            else:
                try:
                    model_used = 'custom' if 'custom' in str(self.sentiment_pipeline.model) else 'fallback'
                except Exception:
                    model_used = 'fallback'

            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'detected_language': detected_language,
                'code_switching_detected': code_switching,
                'political_entities': political_entities,
                'political_keywords': political_keywords,
                'model_used': model_used
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