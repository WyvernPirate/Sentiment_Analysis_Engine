from flask import Blueprint, request, jsonify
from training_data_collector import training_collector
from datetime import datetime

training_bp = Blueprint('training', __name__)

@training_bp.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        success = training_collector.collect_sentiment_feedback(
            data.get('text'),
            data.get('predicted_sentiment'),
            data.get('predicted_confidence', 0.0),
            data.get('user_sentiment'),
            data.get('user_confidence', 1.0)
        )
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json()
        success = training_collector.suggest_new_word(
            data.get('word'),
            data.get('meaning'),
            data.get('category'),
            data.get('context_sentence'),
            data.get('sentiment')
        )
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/export', methods=['POST'])
def export():
    try:
        filename = f"data/training_data/dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        success = training_collector.export_training_dataset(filename)
        return jsonify({"success": success, "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500