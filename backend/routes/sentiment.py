from flask import Blueprint, request, jsonify
from services.sentiment_service import sentiment_service
from services.lexicon_service import lexicon_service
import re

sentiment_bp = Blueprint('sentiment', __name__)

@sentiment_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        lexicon = lexicon_service.legacy_lexicon
        
        # Language detection
        lang, code_switching, lang_details = sentiment_service.detect_language(text, lexicon)
        
        # Hybrid analysis (simplified for now to match core logic)
        eng_sent, eng_conf, eng_details = sentiment_service.analyze_english_sentiment(text)
        set_sent, set_conf = sentiment_service.analyze_setswana_sentiment(text, lexicon)
        
        # Determine final (simple blend)
        final_sentiment = eng_sent
        final_confidence = eng_conf
        
        if lang == "Setswana":
            final_sentiment = set_sent
            final_confidence = set_conf
        elif code_switching:
            if set_sent != "neutral":
                final_sentiment = set_sent
                final_confidence = (set_conf + eng_conf) / 2
                
        # Political context
        entities, keywords = sentiment_service.extract_political_context(text, lexicon)
        
        return jsonify({
            "sentiment": final_sentiment,
            "confidence": round(final_confidence, 3),
            "detected_language": lang,
            "code_switching_detected": code_switching,
            "language_analysis": lang_details,
            "political_context": {"entities": entities, "keywords": keywords},
            "word_count": len(re.findall(r'\b\w+\b', text))
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500