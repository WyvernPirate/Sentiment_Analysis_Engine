from flask import Blueprint, request, jsonify
from data_storage import data_storage
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
def overview():
    try:
        days = request.args.get('days', 7, type=int)
        stats = data_storage.get_dashboard_overview(days)
        return jsonify({
            'stats': stats,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/trends', methods=['GET'])
def trends():
    try:
        days = request.args.get('days', 7, type=int)
        keyword = request.args.get('keyword')
        trends_data = data_storage.get_sentiment_trends(days)
        return jsonify({'trends': trends_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/posts', methods=['GET'])
def posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sentiment_filter = request.args.get('sentiment')
        posts_data = data_storage.get_recent_posts(page, per_page, sentiment_filter)
        return jsonify(posts_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500