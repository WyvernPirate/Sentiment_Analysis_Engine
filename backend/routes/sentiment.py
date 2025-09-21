"""
Sentiment Analysis API Routes
"""
from flask import Blueprint, request, jsonify
from services.sentiment_service import sentiment_service
from utils.validators import validate_text_input

sentiment_bp = Blueprint('sentiment', __name__)

@sentiment_bp.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of provided text"""
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = validate_text_input(data)
        if not validation_result['valid']:
            return jsonify({"error": validation_result['message']}), 400
        
        text = data.get('text', '').strip()
        
        # Analyze sentiment
        result = sentiment_service.analyze_text(text)
        
        if not result:
            return jsonify({"error": "Analysis failed"}), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@sentiment_bp.route('/batch', methods=['POST'])
def analyze_batch():
    """Analyze sentiment for multiple texts"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({"error": "texts array is required"}), 400
        
        if len(texts) > 100:  # Limit batch size
            return jsonify({"error": "Maximum 100 texts per batch"}), 400
        
        results = []
        for i, text in enumerate(texts):
            if not text or not isinstance(text, str):
                results.append({"error": f"Invalid text at index {i}"})
                continue
                
            result = sentiment_service.analyze_text(text.strip())
            results.append(result if result else {"error": "Analysis failed"})
        
        return jsonify({
            "results": results,
            "total": len(texts),
            "successful": len([r for r in results if 'error' not in r])
        })
        
    except Exception as e:
        return jsonify({"error": f"Batch analysis failed: {str(e)}"}), 500

@sentiment_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on sentiment analysis"""
    try:
        data = request.get_json()
        
        required_fields = ['text', 'predicted_sentiment', 'user_sentiment']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' is required"}), 400
        
        result = sentiment_service.collect_feedback(
            text=data['text'],
            predicted_sentiment=data['predicted_sentiment'],
            predicted_confidence=data.get('predicted_confidence', 0.0),
            user_sentiment=data['user_sentiment'],
            user_confidence=data.get('user_confidence', 1.0),
            user_id=data.get('user_id')
        )
        
        if result:
            return jsonify({"message": "Feedback submitted successfully"})
        else:
            return jsonify({"error": "Failed to submit feedback"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Feedback submission failed: {str(e)}"}), 500