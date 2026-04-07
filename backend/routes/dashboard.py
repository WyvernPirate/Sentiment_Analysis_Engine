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

@dashboard_bp.route('/analytics', methods=['GET'])
def analytics():
    try:
        days = request.args.get('days', 7, type=int)
        analytics_data = data_storage.get_advanced_analytics(days)
        return jsonify({
            'analytics': analytics_data,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/political-entities', methods=['GET'])
def political_entities():
    try:
        days = request.args.get('days', 7, type=int)
        entities = data_storage.get_political_entities(days)
        return jsonify({
            'entities': entities,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/language-breakdown', methods=['GET'])
def language_breakdown():
    try:
        days = request.args.get('days', 7, type=int)
        stats = data_storage.get_dashboard_overview(days)
        return jsonify({
            'languages': stats.get('language_breakdown', {}),
            'code_switching_posts': stats.get('code_switching_posts', 0),
            'code_switching_percentage': stats.get('code_switching_percentage', 0),
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/real-time-stats', methods=['GET'])
def real_time_stats():
    try:
        posts = data_storage.get_stored_data()
        now = datetime.now()
        last_hour_cutoff = now - timedelta(hours=1)
        last_24h_cutoff = now - timedelta(hours=24)

        posts_last_hour = 0
        posts_last_24h = 0
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', post.get('collected_at', now.isoformat())))
                if post_date >= last_hour_cutoff:
                    posts_last_hour += 1
                if post_date >= last_24h_cutoff:
                    posts_last_24h += 1
            except Exception:
                continue

        return jsonify({
            'total_posts': len(posts),
            'posts_last_hour': posts_last_hour,
            'posts_last_24h': posts_last_24h,
            'timestamp': now.isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/refresh', methods=['POST'])
def refresh_data():
    try:
        result = data_storage.collect_and_store_data(force_refresh=True)
        if result.get('success'):
            return jsonify({
                'message': 'Dashboard data refreshed successfully',
                'result': result
            })
        return jsonify({'error': result.get('error', 'Refresh failed')}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500