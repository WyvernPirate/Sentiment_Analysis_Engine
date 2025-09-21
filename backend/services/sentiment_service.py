"""
Sentiment Analysis Service
Business logic for sentiment analysis operations
"""
from typing import Dict, Optional, Any
from sentiment_analyzer import SetswanaEnglishSentimentAnalyzer
from training_data_collector import training_collector

class SentimentService:
    def __init__(self):
        self.analyzer = SetswanaEnglishSentimentAnalyzer()
    
    def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of text with comprehensive results"""
        try:
            if not text or not text.strip():
                return None
            
            # Use the enhanced analyzer
            result = self.analyzer.analyze_sentiment(text.strip())
            
            if result:
                # Add additional metadata
                result['analysis_timestamp'] = self._get_timestamp()
                result['service_version'] = '1.0'
                
            return result
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return None
    
    def collect_feedback(self, 
                        text: str,
                        predicted_sentiment: str,
                        predicted_confidence: float,
                        user_sentiment: str,
                        user_confidence: float = 1.0,
                        user_id: Optional[str] = None) -> bool:
        """Collect user feedback on sentiment predictions"""
        try:
            return training_collector.collect_sentiment_feedback(
                text=text,
                predicted_sentiment=predicted_sentiment,
                predicted_confidence=predicted_confidence,
                user_sentiment=user_sentiment,
                user_confidence=user_confidence,
                user_id=user_id
            )
        except Exception as e:
            print(f"Error collecting feedback: {e}")
            return False
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        try:
            return training_collector.analyze_model_performance()
        except Exception as e:
            print(f"Error getting performance stats: {e}")
            return {}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global service instance
sentiment_service = SentimentService()