"""
Training Management API Routes
"""
from flask import Blueprint, request, jsonify
from training_data_collector import training_collector
from model_trainer import model_trainer

training_bp = Blueprint('training', __name__)

@training_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get training data collection statistics"""
    try:
        feedback_stats = training_collector.get_feedback_stats()
        performance_analysis = training_collector.analyze_model_performance()
        
        return jsonify({
            'feedback_stats': feedback_stats,
            'performance_analysis': performance_analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/prepare-dataset', methods=['POST'])
def prepare_dataset():
    """Prepare training dataset from all sources"""
    try:
        data = request.get_json() or {}
        include_feedback = data.get('include_user_feedback', True)
        
        texts, labels = model_trainer.prepare_training_data(include_feedback)
        dataset_path = model_trainer.save_training_dataset(texts, labels)
        
        return jsonify({
            "message": "Training dataset prepared successfully",
            "dataset_path": dataset_path,
            "total_examples": len(texts),
            "label_distribution": {
                "positive": labels.count(2),
                "neutral": labels.count(1), 
                "negative": labels.count(0)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/train-model', methods=['POST'])
def train_model():
    """Start full model training process"""
    try:
        data = request.json or {}
        include_feedback = data.get('include_user_feedback', True)
        train_transformers = data.get('train_transformers', True)
        
        # Run training pipeline
        results = model_trainer.full_training_pipeline(include_feedback, train_transformers)
        
        return jsonify({
            "message": "Model training completed" if results['success'] else "Model training failed",
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/quick-retrain', methods=['POST'])
def quick_retrain():
    """Quick retrain with current data"""
    try:
        # Prepare minimal dataset
        texts, labels = model_trainer.prepare_training_data(include_user_feedback=True)
        
        # Save dataset
        dataset_path = model_trainer.save_training_dataset(texts, labels)
        
        # Update lexicon suggestions
        suggestions_count = model_trainer.update_lexicon_from_training(texts, labels)
        
        return jsonify({
            "message": "Quick retrain completed",
            "dataset_path": dataset_path,
            "training_examples": len(texts),
            "lexicon_suggestions": suggestions_count,
            "lexicon_updated": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/export', methods=['POST'])
def export_training_data():
    """Export training dataset"""
    try:
        from datetime import datetime
        filename = f"data/training_data/botswana_sentiment_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        success = training_collector.export_training_dataset(filename)
        
        if success:
            return jsonify({
                "message": "Training dataset exported successfully",
                "filename": filename
            })
        else:
            return jsonify({"error": "Failed to export training data"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@training_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on sentiment analysis"""
    try:
        data = request.get_json()
        
        required_fields = ['text', 'predicted_sentiment', 'user_sentiment']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' is required"}), 400
        
        success = training_collector.collect_sentiment_feedback(
            text=data['text'],
            predicted_sentiment=data['predicted_sentiment'],
            predicted_confidence=data.get('predicted_confidence', 0.0),
            user_sentiment=data['user_sentiment'],
            user_confidence=data.get('user_confidence', 1.0),
            user_id=data.get('user_id')
        )
        
        if success:
            return jsonify({
                "message": "Feedback submitted successfully",
                "agreement": data['predicted_sentiment'] == data['user_sentiment']
            })
        else:
            return jsonify({"error": "Failed to submit feedback"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Feedback submission failed: {str(e)}"}), 500