# This module defines the Flask Blueprint for social media data collection and cleaning endpoints.
from flask import Blueprint, jsonify, request

from config import Config
from services.data_cleaner_service import data_cleaner_service
from services.raw_data_manager import raw_data_manager
from services.social_collector_service import social_collector_service


social_bp = Blueprint('social', __name__)

@social_bp.route('/health', methods=['GET'])
def health():
    return jsonify(
        {
            'status': 'healthy',
            'provider_default': Config.SOCIAL_PROVIDER,
            'brightdata_configured': bool(Config.BRIGHTDATA_API_TOKEN and Config.BRIGHTDATA_COLLECTOR_URL),
            'apify_configured': bool(Config.APIFY_API_TOKEN and Config.APIFY_ACTOR_ID),
            'twikit_configured': bool(
                (Config.TWIKIT_USERNAME and Config.TWIKIT_PASSWORD)
                or Config.TWIKIT_COOKIES_PATH
            )
        }
    )

@social_bp.route('/collect', methods=['POST'])
def collect():
    try:
        payload = request.get_json() or {}
        provider = payload.get('provider')
        query = payload.get('query')
        seed_entity = payload.get('seed_entity')
        focus_terms = payload.get('focus_terms')
        actor_input = payload.get('actor_input')
        max_results = payload.get('max_results', 20)
        input_items = payload.get('input')
        request_params = payload.get('request_params') or {}

        if input_items is not None and not isinstance(input_items, list):
            return jsonify({'error': 'input must be a list when provided'}), 400
        if not isinstance(request_params, dict):
            return jsonify({'error': 'request_params must be an object when provided'}), 400
        if focus_terms is not None and not isinstance(focus_terms, list):
            return jsonify({'error': 'focus_terms must be a list when provided'}), 400
        if actor_input is not None and not isinstance(actor_input, dict):
            return jsonify({'error': 'actor_input must be an object when provided'}), 400

        collected = social_collector_service.collect_posts(
            provider=provider,
            query=query,
            max_results=max_results,
            input_items=input_items,
            extra_params=request_params,
            seed_entity=seed_entity,
            focus_terms=focus_terms,
            actor_input=actor_input
        )

        log_entry = raw_data_manager.save_raw_batch(
            source='x',
            query=collected.get('query', ''),
            records=collected.get('records', []),
            run_meta=collected.get('meta', {})
        )

        records = collected.get('records', [])
        preview = []
        for record in records[:5]:
            preview.append(
                {
                    'source_post_id': record.get('source_post_id', ''),
                    'author_username': record.get('author_username', ''),
                    'created_at_utc': record.get('created_at_utc', ''),
                    'post_url': record.get('post_url', ''),
                    'text_raw': (record.get('text_raw', '') or '')[:220],
                    'public_metrics': record.get('public_metrics', {})
                }
            )

        return jsonify(
            {
                'collection_id': log_entry['collection_id'],
                'source': 'x',
                'provider': collected.get('provider', 'brightdata'),
                'query': collected.get('query', ''),
                'count': collected.get('count', 0),
                'raw_file': log_entry['raw_file'],
                'meta': collected.get('meta', {}),
                'records_preview': preview
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
        filter_mode = (payload.get('filter_mode') or 'relaxed').strip().lower()

        if not collection_id:
            return jsonify({'error': 'collection_id is required'}), 400

        if filter_mode not in ('relaxed', 'strict'):
            return jsonify({'error': "filter_mode must be 'relaxed' or 'strict'"}), 400

        entry = raw_data_manager.get_collection(collection_id)
        if not entry:
            return jsonify({'error': 'collection not found'}), 404

        raw_records = raw_data_manager.load_raw_records(entry.get('raw_file', ''))
        cleaned_records, report = data_cleaner_service.clean_records(raw_records, filter_mode=filter_mode)
        saved = raw_data_manager.save_cleaned_batch(collection_id, cleaned_records, report)

        return jsonify(
            {
                'collection_id': collection_id,
                'raw_count': len(raw_records),
                'cleaned_count': saved['count'],
                'filter_mode': filter_mode,
                'cleaned_file': saved['cleaned_file'],
                'report_file': saved['report_file'],
                'report': report
            }
        )
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500