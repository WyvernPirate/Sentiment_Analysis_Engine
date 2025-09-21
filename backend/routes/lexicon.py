"""
Lexicon Management API Routes
"""
from flask import Blueprint, request, jsonify
from lexicon_manager import lexicon_manager
from training_data_collector import training_collector

lexicon_bp = Blueprint('lexicon', __name__)

@lexicon_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get lexicon statistics"""
    try:
        stats = lexicon_manager.get_category_stats()
        metadata = lexicon_manager.lexicon.get('metadata', {})
        
        return jsonify({
            'category_stats': stats,
            'metadata': metadata,
            'total_words': lexicon_manager.count_total_words()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lexicon_bp.route('/search', methods=['GET'])
def search():
    """Search words in lexicon"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', None)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        results = lexicon_manager.search_words(query, category)
        return jsonify({
            'query': query,
            'category': category,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lexicon_bp.route('/add', methods=['POST'])
def add_word():
    """Add a new word to the lexicon"""
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        category = data.get('category', '')
        meaning = data.get('meaning', '')
        
        if not all([word, category, meaning]):
            return jsonify({"error": "word, category, and meaning are required"}), 400
        
        # Add optional fields
        kwargs = {}
        for field in ['context', 'intensity', 'type', 'source']:
            if field in data:
                kwargs[field] = data[field]
        
        success = lexicon_manager.add_word(word, category, meaning, **kwargs)
        
        if success:
            return jsonify({
                "message": f"Word '{word}' added to category '{category}'",
                "word": word,
                "category": category,
                "meaning": meaning
            })
        else:
            return jsonify({"error": "Failed to add word"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lexicon_bp.route('/suggest', methods=['POST'])
def suggest_word():
    """Suggest a new word for the lexicon"""
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        meaning = data.get('meaning', '')
        category = data.get('category', '')
        context_sentence = data.get('context_sentence', '')
        sentiment = data.get('sentiment', None)
        
        if not all([word, meaning, category, context_sentence]):
            return jsonify({"error": "word, meaning, category, and context_sentence are required"}), 400
        
        success = training_collector.suggest_new_word(
            word, meaning, category, context_sentence, sentiment
        )
        
        if success:
            return jsonify({
                "message": f"Word suggestion '{word}' submitted for review",
                "word": word,
                "status": "pending_review"
            })
        else:
            return jsonify({"error": "Failed to submit suggestion"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lexicon_bp.route('/export', methods=['GET'])
def export_lexicon():
    """Export lexicon to CSV"""
    try:
        from datetime import datetime
        filename = f"data/lexicon_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        success = lexicon_manager.export_to_csv(filename)
        
        if success:
            return jsonify({
                "message": "Lexicon exported successfully",
                "filename": filename
            })
        else:
            return jsonify({"error": "Failed to export lexicon"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500