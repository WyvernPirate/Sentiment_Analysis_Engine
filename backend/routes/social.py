# This module defines the Flask Blueprint for social media data collection and cleaning endpoints.
from flask import Blueprint, jsonify, request

from config import Config
from services.data_cleaner_service import data_cleaner_service
from services.raw_data_manager import raw_data_manager
from services.social_collector_service import social_collector_service


social_bp = Blueprint('social', __name__)

# Health check endpoint for the social blueprint, also indicates if X API credentials are configured
@social_bp.route('/health', methods=['GET'])
def health():
    return jsonify(
        {
            'status': 'healthy',
            'x_bearer_configured': bool(Config.TWITTER_BEARER_TOKEN)
        }
    )

# Endpoint to collect recent posts from X based on a query or default political keywords/hashtags
@social_bp.route('/collect', methods=['POST'])
def collect():
    try:
        payload = request.get_json() or {}
        query = payload.get('query')
        max_results = payload.get('max_results', 20)

        collected = social_collector_service.collect_x_recent_posts(
            query=query,
            max_results=max_results
        )

        log_entry = raw_data_manager.save_raw_batch(
            source='x',
            query=collected.get('query', ''),
            records=collected.get('records', []),
            run_meta=collected.get('meta', {})
        )

        return jsonify(
            {
                'collection_id': log_entry['collection_id'],
                'source': 'x',
                'query': collected.get('query', ''),
                'count': collected.get('count', 0),
                'raw_file': log_entry['raw_file'],
                'meta': collected.get('meta', {})
            }
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

# Endpoint to list recent collections of raw social media data, with pagination support
@social_bp.route('/collections', methods=['GET'])
def collections():
    limit = request.args.get('limit', 20, type=int)
    entries = raw_data_manager.list_collections(limit=max(1, min(limit, 100)))
    return jsonify({'collections': entries, 'count': len(entries)})

# Endpoint to clean a collected batch of raw social media data based on its collection_id, applying normalization and relevance filtering
@social_bp.route('/clean', methods=['POST'])
def clean():
    try:
        payload = request.get_json() or {}
        collection_id = (payload.get('collection_id') or '').strip()

        if not collection_id:
            return jsonify({'error': 'collection_id is required'}), 400

        entry = raw_data_manager.get_collection(collection_id)
        if not entry:
            return jsonify({'error': 'collection not found'}), 404

        raw_records = raw_data_manager.load_raw_records(entry.get('raw_file', ''))
        cleaned_records, report = data_cleaner_service.clean_records(raw_records)
        saved = raw_data_manager.save_cleaned_batch(collection_id, cleaned_records, report)

        return jsonify(
            {
                'collection_id': collection_id,
                'raw_count': len(raw_records),
                'cleaned_count': saved['count'],
                'cleaned_file': saved['cleaned_file'],
                'report_file': saved['report_file'],
                'report': report
            }
        )
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500