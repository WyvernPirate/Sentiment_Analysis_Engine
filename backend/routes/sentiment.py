
from flask import Blueprint, request, jsonify
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
    Main sentiment analysis endpoint - Single-path English-only architecture
    
    Request:
    {
      "text": "Text to analyze (English)"
    }
    
    Analysis Steps:
    1. Parse request, validate non-empty text
    2. Refresh lexicon to pick up words added via /api/lexicon/add (dynamic)
    3. Call sentiment service pipeline (transformer or fallback):
       - Stage 1: Political word matching (pre-tokenization)
       - Stage 2: Transformer inference (cardiffnlp model)
       - Stage 3: Extract trigger words (for UI)
       - Stage 4: Extract political entities (hardcoded)
    4. Assemble response with all metadata
    5. Return JSON to frontend
    
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
        
        # English sentiment (transformer or fallback)
        sentiment, confidence, details = sentiment_service.analyze_english_sentiment(text)
        
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