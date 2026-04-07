"""
Database Models - Sentiment Analysis Engine
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class SocialMediaPost(db.Model):
    
    __tablename__ = 'social_media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.String(100), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    author_followers = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    
    location = db.Column(db.String(100))
    raw_data = db.Column(db.Text)


class SentimentAnalysis(db.Model):
    __tablename__ = 'sentiment_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_media_posts.id'), nullable=False)
    
    sentiment = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    
    detected_language = db.Column(db.String(50))
    code_switching_detected = db.Column(db.Boolean, default=False)
    
    political_keywords = db.Column(db.Text)
    political_entities = db.Column(db.Text)
    
    model_used = db.Column(db.String(100))
    model_version = db.Column(db.String(50))
    
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)


class PoliticalTrend(db.Model):
    __tablename__ = 'political_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer)
    
    keyword = db.Column(db.String(100))
    sentiment_positive = db.Column(db.Integer, default=0)
    sentiment_negative = db.Column(db.Integer, default=0)
    sentiment_neutral = db.Column(db.Integer, default=0)
    
    total_posts = db.Column(db.Integer, default=0)
    average_confidence = db.Column(db.Float)
    
    english_posts = db.Column(db.Integer, default=0)
    setswana_posts = db.Column(db.Integer, default=0)
    code_switching_posts = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)