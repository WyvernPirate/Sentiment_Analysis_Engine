from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class SocialMediaPost(db.Model):
    """Store raw social media posts"""
    __tablename__ = 'social_media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # 'twitter', 'facebook'
    post_id = db.Column(db.String(100), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    author_followers = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Engagement metrics
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    
    # Location data (if available)
    location = db.Column(db.String(100))
    
    # Raw metadata
    raw_data = db.Column(db.Text)  # Store original JSON
    
    # Relationships
    sentiment_analysis = db.relationship('SentimentAnalysis', backref='post', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'post_id': self.post_id,
            'text': self.text,
            'author': self.author,
            'created_at': self.created_at.isoformat(),
            'likes': self.likes,
            'shares': self.shares,
            'comments': self.comments,
            'location': self.location
        }

class SentimentAnalysis(db.Model):
    """Store sentiment analysis results"""
    __tablename__ = 'sentiment_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_media_posts.id'), nullable=False)
    
    # Sentiment results
    sentiment = db.Column(db.String(20), nullable=False)  # 'positive', 'negative', 'neutral'
    confidence = db.Column(db.Float, nullable=False)
    
    # Language detection
    detected_language = db.Column(db.String(50))  # 'English', 'Setswana', 'Setswana-English'
    code_switching_detected = db.Column(db.Boolean, default=False)
    
    # Political context
    political_keywords = db.Column(db.Text)  # JSON array of detected keywords
    political_entities = db.Column(db.Text)  # JSON array of detected political entities
    
    # Model information
    model_used = db.Column(db.String(100))
    model_version = db.Column(db.String(50))
    
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sentiment': self.sentiment,
            'confidence': self.confidence,
            'detected_language': self.detected_language,
            'code_switching_detected': self.code_switching_detected,
            'political_keywords': json.loads(self.political_keywords) if self.political_keywords else [],
            'political_entities': json.loads(self.political_entities) if self.political_entities else [],
            'analyzed_at': self.analyzed_at.isoformat()
        }

class PoliticalTrend(db.Model):
    """Store aggregated political sentiment trends"""
    __tablename__ = 'political_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Time period
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer)  # For hourly trends
    
    # Trend data
    keyword = db.Column(db.String(100))  # Political keyword or entity
    sentiment_positive = db.Column(db.Integer, default=0)
    sentiment_negative = db.Column(db.Integer, default=0)
    sentiment_neutral = db.Column(db.Integer, default=0)
    
    total_posts = db.Column(db.Integer, default=0)
    average_confidence = db.Column(db.Float)
    
    # Language breakdown
    english_posts = db.Column(db.Integer, default=0)
    setswana_posts = db.Column(db.Integer, default=0)
    code_switching_posts = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        total = self.sentiment_positive + self.sentiment_negative + self.sentiment_neutral
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'hour': self.hour,
            'keyword': self.keyword,
            'sentiment_breakdown': {
                'positive': self.sentiment_positive,
                'negative': self.sentiment_negative,
                'neutral': self.sentiment_neutral,
                'positive_pct': (self.sentiment_positive / total * 100) if total > 0 else 0,
                'negative_pct': (self.sentiment_negative / total * 100) if total > 0 else 0,
                'neutral_pct': (self.sentiment_neutral / total * 100) if total > 0 else 0
            },
            'total_posts': self.total_posts,
            'average_confidence': self.average_confidence,
            'language_breakdown': {
                'english': self.english_posts,
                'setswana': self.setswana_posts,
                'code_switching': self.code_switching_posts
            }
        }