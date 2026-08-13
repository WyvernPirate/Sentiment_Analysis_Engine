
from flask import Blueprint, request, jsonify
from config import Config
from services.sentiment_service import sentiment_service
from services.lexicon_service import lexicon_service
from services.political_entity_service import political_entity_service
import re
from utils.logger import logger

sentiment_bp = Blueprint('sentiment', __name__)


@sentiment_bp.route('/test-examples', methods=['GET'])
def test_examples():
   
    logger.info("Serving test examples")
    return jsonify({
        "examples": [
            {
                "text": "I support the new policy direction",
                "description": "English positive sentiment",
                "expected": "positive"
            },
            {
                "text": "This reform plan is terrible and weak",
                "description": "English negative sentiment",
                "expected": "negative"
            },
            {
                "text": "Parliament will debate the budget tomorrow",
                "description": "English neutral sentiment with political keywords",
                "expected": "neutral"
            },
            {
                "text": "The party made strong progress this year",
                "description": "English positive sentiment with political keyword",
                "expected": "positive"
            }
        ]
    })


@sentiment_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Main sentiment analysis endpoint - language-aware architecture.

    Request:
    {
      "text": "Text to analyze (English, Setswana, or a mix of both)"
    }

    Analysis Steps:
    1. Parse request, validate non-empty text
    2. Refresh lexicon to pick up words added via /api/lexicon/add (dynamic)
    3. Call sentiment_service.analyze_sentiment, which:
       - Detects language via Setswana-word-ratio against the lexicon
       - English text -> the English-only model
       - Setswana / Setswana-English text -> the multilingual model,
         blended with a lexicon polarity signal
    4. Extract trigger words, matched political words, and political entities
    5. Assemble response with all metadata (including language_detected)
    6. Return JSON to frontend

    Error Handling:
    - 400: No text provided
    - 500: Transformer failure (falls back to basic analysis)
    """
    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        logger.info(f"Analyzing sentiment for text (length: {len(text)})")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        #STEP 1: DYNAMIC LEXICON REFRESH
        # Ensures words added via POST /api/lexicon/add are available immediately
        # without server restart (key requirement for smooth UX)
        lexicon_service.refresh_lexicon()
        lexicon = lexicon_service.legacy_lexicon

        #  STEP 2: ANALYSIS PIPELINE
        # All methods in sentiment_service are stateless, work on per-request basis

        # Language-aware sentiment: detects Setswana/code-switching and routes
        # to the appropriate model (see sentiment_service.analyze_sentiment)
        sentiment, confidence, details = sentiment_service.analyze_sentiment(
            text, lexicon, use_code_switching=Config.USE_CODE_SWITCHING
        )

        # Pre-tokenization political word matching (before transformer tokenizes)
        matched_political_words = sentiment_service.match_political_words(text, lexicon)

        # Post-inference political entity extraction (database-backed)
        political_entities = political_entity_service.extract_entities(text)

        # Trigger word extraction for UI display - passing sentiment for model-aware analysis
        sentiment_words = sentiment_service.extract_sentiment_trigger_words(text, target_sentiment=sentiment)

        # STEP 3: RESPONSE ASSEMBLY
        return jsonify({
            "sentiment": sentiment,
            "confidence": round(confidence, 3),  # Round to 3 decimals
            "model_used": details.get('model', 'unknown'),
            "language_detected": details.get('language_detected', 'unknown'),
            "code_switching": details.get('code_switching', False),
            "word_count": len(re.findall(r'\b\w+\b', text)),
            "matched_political_words": matched_political_words,  # User-curated, dynamic
            "sentiment_words": sentiment_words,  # Hardcoded trigger words
            "political_context": {
                "entities": political_entities,  # Hardcoded parties/leaders/locations
                "keywords": [  # Alias for matched_political_words with extra metadata
                    {
                        "term": word['term'],
                        "meaning": word['meaning'],
                        "language": "Setswana"  # Lexicon is typically Setswana political terms
                    }
                    for word in matched_political_words
                ]
            }
        })

    except Exception as e:
        # Log error, return 500, allows frontend to show
        logger.error(f"Sentiment analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500