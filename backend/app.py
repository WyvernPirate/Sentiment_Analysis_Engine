from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json

# Import our custom modules
from config import Config
from models import db, SocialMediaPost, SentimentAnalysis, PoliticalTrend
from sentiment_analyzer import analyzer
from data_collector import collect_all_data

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# === CORE SENTIMENT ANALYSIS API ===
@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    """Analyze sentiment of provided text"""
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Use our enhanced analyzer
    result = analyzer.analyze_sentiment(text)
    if not result:
        return jsonify({"error": "Analysis failed"}), 500

    return jsonify(result)

# === DASHBOARD DATA ENDPOINTS ===
@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    """Get dashboard overview statistics"""
    try:
        # Get date range (default: last 7 days)
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total posts collected
        total_posts = SocialMediaPost.query.filter(
            SocialMediaPost.collected_at >= start_date
        ).count()
        
        # Sentiment breakdown
        sentiment_stats = db.session.query(
            SentimentAnalysis.sentiment,
            db.func.count(SentimentAnalysis.id).label('count')
        ).join(SocialMediaPost).filter(
            SocialMediaPost.collected_at >= start_date
        ).group_by(SentimentAnalysis.sentiment).all()
        
        sentiment_breakdown = {stat.sentiment: stat.count for stat in sentiment_stats}
        
        # Language breakdown
        language_stats = db.session.query(
            SentimentAnalysis.detected_language,
            db.func.count(SentimentAnalysis.id).label('count')
        ).join(SocialMediaPost).filter(
            SocialMediaPost.collected_at >= start_date
        ).group_by(SentimentAnalysis.detected_language).all()
        
        language_breakdown = {stat.detected_language: stat.count for stat in language_stats}
        
        # Platform breakdown
        platform_stats = db.session.query(
            SocialMediaPost.platform,
            db.func.count(SocialMediaPost.id).label('count')
        ).filter(
            SocialMediaPost.collected_at >= start_date
        ).group_by(SocialMediaPost.platform).all()
        
        platform_breakdown = {stat.platform: stat.count for stat in platform_stats}
        
        return jsonify({
            'total_posts': total_posts,
            'sentiment_breakdown': sentiment_breakdown,
            'language_breakdown': language_breakdown,
            'platform_breakdown': platform_breakdown,
            'date_range': {
                'start': start_date.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/trends', methods=['GET'])
def dashboard_trends():
    """Get political sentiment trends over time"""
    try:
        days = request.args.get('days', 7, type=int)
        keyword = request.args.get('keyword', None)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query for trends
        query = db.session.query(
            db.func.date(SocialMediaPost.created_at).label('date'),
            SentimentAnalysis.sentiment,
            db.func.count(SentimentAnalysis.id).label('count')
        ).join(SentimentAnalysis).filter(
            SocialMediaPost.created_at >= start_date
        )
        
        # Filter by keyword if provided
        if keyword:
            query = query.filter(
                SentimentAnalysis.political_keywords.contains(keyword)
            )
        
        trends = query.group_by(
            db.func.date(SocialMediaPost.created_at),
            SentimentAnalysis.sentiment
        ).order_by(db.func.date(SocialMediaPost.created_at)).all()
        
        # Format trends data
        trends_data = {}
        for trend in trends:
            date_str = trend.date.isoformat()
            if date_str not in trends_data:
                trends_data[date_str] = {'positive': 0, 'negative': 0, 'neutral': 0}
            trends_data[date_str][trend.sentiment] = trend.count
        
        return jsonify({
            'trends': trends_data,
            'keyword': keyword,
            'date_range': {
                'start': start_date.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/posts', methods=['GET'])
def dashboard_posts():
    """Get recent social media posts with sentiment analysis"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sentiment_filter = request.args.get('sentiment', None)
        platform_filter = request.args.get('platform', None)
        
        # Build query
        query = db.session.query(SocialMediaPost).join(SentimentAnalysis)
        
        if sentiment_filter:
            query = query.filter(SentimentAnalysis.sentiment == sentiment_filter)
        
        if platform_filter:
            query = query.filter(SocialMediaPost.platform == platform_filter)
        
        # Paginate results
        posts = query.order_by(SocialMediaPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        posts_data = []
        for post in posts.items:
            post_dict = post.to_dict()
            if post.sentiment_analysis:
                post_dict['sentiment_analysis'] = post.sentiment_analysis.to_dict()
            posts_data.append(post_dict)
        
        return jsonify({
            'posts': posts_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === DATA COLLECTION ENDPOINTS ===
@app.route('/api/collect/trigger', methods=['POST'])
def trigger_collection():
    """Manually trigger data collection"""
    try:
        result = collect_all_data()
        return jsonify({
            "message": "Data collection completed",
            "results": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/trigger', methods=['POST'])
def trigger_analysis():
    """Manually trigger sentiment analysis of unprocessed posts"""
    try:
        processed_count = analyzer.analyze_unprocessed_posts()
        return jsonify({
            "message": f"Analyzed {processed_count} posts",
            "processed_count": processed_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === SYSTEM STATUS ENDPOINTS ===
@app.route('/api/health', methods=['GET'])
def health():
    """Comprehensive health check"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check model status
        model_available = os.path.exists(Config.SENTIMENT_MODEL_PATH)
        
        # Get recent collection stats
        recent_posts = SocialMediaPost.query.filter(
            SocialMediaPost.collected_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get unprocessed posts count
        unprocessed_posts = db.session.query(SocialMediaPost)\
            .outerjoin(SentimentAnalysis)\
            .filter(SentimentAnalysis.id.is_(None))\
            .count()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "custom_model_available": model_available,
            "model_path": Config.SENTIMENT_MODEL_PATH,
            "fallback_model": Config.FALLBACK_MODEL,
            "stats": {
                "posts_last_24h": recent_posts,
                "unprocessed_posts": unprocessed_posts
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get public configuration information"""
    return jsonify({
        "political_keywords": Config.POLITICAL_KEYWORDS,
        "political_hashtags": Config.POLITICAL_HASHTAGS,
        "collection_interval": Config.COLLECTION_INTERVAL_MINUTES,
        "max_tweets_per_collection": Config.MAX_TWEETS_PER_COLLECTION
    })

if __name__ == '__main__':
    app.run(debug=True)