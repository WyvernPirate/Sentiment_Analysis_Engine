from flask import Blueprint, jsonify, request
from services.lexicon_service import lexicon_service
from lexicon_manager import lexicon_manager

lexicon_bp = Blueprint('lexicon', __name__)

@lexicon_bp.route('/', methods=['GET'])
def get_lexicon():
    return jsonify(lexicon_service.get_stats())


@lexicon_bp.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'category_stats': lexicon_manager.get_category_stats(),
        'metadata': lexicon_manager.lexicon.get('metadata', {}),
        'total_words': lexicon_manager.count_total_words()
    })


@lexicon_bp.route('/search', methods=['GET'])
def search_lexicon():
    query = request.args.get('q', '').strip()
    category = request.args.get('category')
    if not query:
        return jsonify({'results': [], 'count': 0, 'query': query, 'category': category})

    results = lexicon_manager.search_words(query, category)
    return jsonify({'results': results, 'count': len(results), 'query': query, 'category': category})


@lexicon_bp.route('/add', methods=['POST'])
def add_word():
    data = request.get_json() or {}
    word = (data.get('word') or '').strip()
    category = (data.get('category') or '').strip()
    meaning = (data.get('meaning') or '').strip()

    if not word or not category or not meaning:
        return jsonify({'error': 'word, category, and meaning are required'}), 400

    success = lexicon_manager.add_word(
        word=word,
        category=category,
        meaning=meaning,
        context=data.get('context') or data.get('context_sentence', ''),
        intensity=data.get('intensity', 'medium'),
        type=data.get('type', ''),
        source='api'
    )

    if not success:
        return jsonify({'error': 'Failed to add word'}), 500

    lexicon_service.refresh_lexicon()
    return jsonify({'message': f"Word '{word}' added successfully", 'word': word, 'category': category, 'meaning': meaning})

@lexicon_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "lexicon"})