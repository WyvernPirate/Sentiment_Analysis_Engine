from flask import Blueprint, request, jsonify
from training_data_collector import training_collector
from datetime import datetime

training_bp = Blueprint('training', __name__)


@training_bp.route('/stats', methods=['GET'])
def stats():
    try:
        feedback_stats = training_collector.get_feedback_stats()
        performance_analysis = training_collector.analyze_model_performance()
        return jsonify({
            'feedback_stats': feedback_stats,
            'performance_analysis': performance_analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/quick-retrain', methods=['POST'])
def quick_retrain():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_path = f"data/training_data/quick_retrain_{timestamp}.csv"
        export_success = training_collector.export_training_dataset(dataset_path)
        if not export_success:
            return jsonify({"error": "Failed to prepare quick retrain dataset"}), 500

        feedback_stats = training_collector.get_feedback_stats()

        return jsonify({
            'message': 'Quick retrain dataset prepared successfully',
            'dataset_path': dataset_path,
            'training_examples': feedback_stats.get('total_feedback', 0),
            'lexicon_suggestions': feedback_stats.get('new_word_suggestions', 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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