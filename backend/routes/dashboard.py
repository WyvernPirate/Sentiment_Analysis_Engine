"""
Dashboard API Routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, SocialMediaPost, SentimentAnalysis, PoliticalTrend
from services.trend_analysis_service import trend_service

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    """Get dashboard overview statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic stats
        stats = trend_service.get_overview_stats(start_date)
        
        return jsonify({
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get sentiment trends over time"""
    try:
        days = request.args.get('days', 7, type=int)
        keyword = request.args.get('keyword')
        granularity = request.args.get('granularity', 'daily')  # daily, hourly
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        trends = trend_service.get_sentiment_trends(
            start_date=start_date,
            keyword=keyword,
            granularity=granularity
        )
        
        return jsonify({
            'trends': trends,
            'filters': {
                'days': days,
                'keyword': keyword,
                'granularity': granularity
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get recent social media posts with analysis"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sentiment_filter = request.args.get('sentiment')
        platform_filter = request.args.get('platform')
        keyword_filter = request.args.get('keyword')
        
        posts = trend_service.get_posts_with_filters(
            page=page,
            per_page=per_page,
            sentiment_filter=sentiment_filter,
            platform_filter=platform_filter,
            keyword_filter=keyword_filter
        )
        
        return jsonify(posts)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/political-entities', methods=['GET'])
def get_political_entities():
    """Get political entity sentiment breakdown"""
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        entities = trend_service.get_political_entity_sentiment(start_date)
        
        return jsonify({
            'entities': entities,
            'period': {
                'days': days,
                'start_date': start_date.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/language-breakdown', methods=['GET'])
def get_language_breakdown():
    """Get language usage breakdown"""
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        breakdown = trend_service.get_language_breakdown(start_date)
        
        return jsonify({
            'language_breakdown': breakdown,
            'period': {
                'days': days,
                'start_date': start_date.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/real-time-stats', methods=['GET'])
def get_real_time_stats():
    """Get real-time statistics for live dashboard"""
    try:
        # Get stats for the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        stats = {
            'posts_last_hour': SocialMediaPost.query.filter(
                SocialMediaPost.collected_at >= one_hour_ago
            ).count(),
            'sentiment_distribution': trend_service.get_recent_sentiment_distribution(one_hour_ago),
            'top_keywords': trend_service.get_trending_keywords(one_hour_ago),
            'active_platforms': trend_service.get_active_platforms(one_hour_ago),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500