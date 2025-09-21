"""
Admin API Routes
"""
from flask import Blueprint, request, jsonify
from training_data_collector import training_collector
from lexicon_manager import lexicon_manager

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/pending-suggestions', methods=['GET'])
def get_pending_suggestions():
    """Get pending word suggestions and corrections for admin review"""
    try:
        limit = request.args.get('limit', 20, type=int)
        suggestions = training_collector.get_pending_word_suggestions(limit)
        corrections = training_collector.get_pending_corrections(limit)
        
        return jsonify({
            'word_suggestions': suggestions,
            'sentiment_corrections': corrections,
            'total_suggestions': len(suggestions),
            'total_corrections': len(corrections)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/approve-word', methods=['POST'])
def approve_word():
    """Approve a word suggestion"""
    try:
        data = request.get_json()
        word = data.get('word', '')
        timestamp = data.get('timestamp', '')
        
        if not word or not timestamp:
            return jsonify({"error": "word and timestamp are required"}), 400
        
        success = training_collector.approve_word_suggestion(word, timestamp)
        
        if success:
            return jsonify({
                "message": f"Word '{word}' approved and added to lexicon",
                "word": word
            })
        else:
            return jsonify({"error": "Failed to approve word suggestion"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/system-stats', methods=['GET'])
def get_system_stats():
    """Get comprehensive system statistics for admin dashboard"""
    try:
        from models import SocialMediaPost, SentimentAnalysis
        from datetime import datetime, timedelta
        
        # Database stats
        total_posts = SocialMediaPost.query.count()
        total_analyses = SentimentAnalysis.query.count()
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_posts = SocialMediaPost.query.filter(
            SocialMediaPost.collected_at >= recent_cutoff
        ).count()
        
        # Lexicon stats
        lexicon_stats = lexicon_manager.get_category_stats()
        total_words = lexicon_manager.count_total_words()
        
        # Training stats
        training_stats = training_collector.get_feedback_stats()
        
        return jsonify({
            'database_stats': {
                'total_posts': total_posts,
                'total_analyses': total_analyses,
                'recent_posts_24h': recent_posts,
                'analysis_coverage': (total_analyses / total_posts * 100) if total_posts > 0 else 0
            },
            'lexicon_stats': {
                'total_words': total_words,
                'categories': lexicon_stats
            },
            'training_stats': training_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/data-collection/trigger', methods=['POST'])
def trigger_data_collection():
    """Manually trigger data collection (admin only)"""
    try:
        from data_collector import collect_all_data
        result = collect_all_data()
        
        return jsonify({
            "message": "Data collection triggered successfully",
            "results": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/analysis/trigger', methods=['POST'])
def trigger_analysis():
    """Manually trigger sentiment analysis of unprocessed posts"""
    try:
        from sentiment_analyzer import analyzer
        processed_count = analyzer.analyze_unprocessed_posts()
        
        return jsonify({
            "message": f"Analysis triggered successfully",
            "processed_count": processed_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/cleanup/old-data', methods=['POST'])
def cleanup_old_data():
    """Clean up old data based on retention policy"""
    try:
        from models import db, SocialMediaPost
        from datetime import datetime, timedelta
        from config import Config
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=Config.DATA_RETENTION_DAYS)
        
        # Count posts to be deleted
        old_posts_count = SocialMediaPost.query.filter(
            SocialMediaPost.collected_at < cutoff_date
        ).count()
        
        # Delete old posts (this will cascade to sentiment analyses)
        SocialMediaPost.query.filter(
            SocialMediaPost.collected_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Cleanup completed",
            "deleted_posts": old_posts_count,
            "cutoff_date": cutoff_date.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500