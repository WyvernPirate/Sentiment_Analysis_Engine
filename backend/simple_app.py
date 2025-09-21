#!/usr/bin/env python3
"""
Simple Flask app for testing Setswana sentiment analysis
This version works without database dependencies for initial testing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import json
from datetime import datetime, timedelta
from lexicon_manager import lexicon_manager
from training_data_collector import training_collector
from model_trainer import model_trainer
from simple_data_collector import collect_simple_data
from data_storage import data_storage

app = Flask(__name__)
CORS(app)

# Load dynamic Setswana lexicon
def get_setswana_lexicon():
    """Get the current Setswana lexicon from the lexicon manager"""
    return lexicon_manager.lexicon

# Helper function to convert lexicon format for compatibility
def get_legacy_lexicon_format():
    """Convert new lexicon format to legacy format for existing functions"""
    lexicon = lexicon_manager.lexicon
    
    legacy_format = {
        'common_words': set(),
        'positive': {},
        'negative': {},
        'political': {}
    }
    
    # Convert common words
    if 'common_words' in lexicon:
        legacy_format['common_words'] = set(lexicon['common_words'].keys())
    
    # Convert sentiment words
    for category in ['positive', 'negative', 'political']:
        if category in lexicon:
            legacy_format[category] = {
                word: details.get('meaning', '') 
                for word, details in lexicon[category].items()
            }
    
    # Add Botswana-specific terms to political
    if 'botswana_specific' in lexicon:
        for word, details in lexicon['botswana_specific'].items():
            legacy_format['political'][word] = details.get('meaning', '')
    
    return legacy_format

SETSWANA_LEXICON = get_legacy_lexicon_format()

# Political entities for Botswana
POLITICAL_ENTITIES = {
    'parties': {
        'BDP': 'Botswana Democratic Party',
        'UDC': 'Umbrella for Democratic Change', 
        'BCP': 'Botswana Congress Party',
        'AP': 'Alliance for Progressives'
    },
    'leaders': {
        'Masisi': 'Mokgweetsi Masisi',
        'Boko': 'Duma Boko',
        'Saleshando': 'Dumelang Saleshando',
        'Khama': 'Ian Khama'
    },
    'locations': {
        'Gaborone': 'Capital city',
        'Francistown': 'Second largest city',
        'Maun': 'Tourism hub',
        'Serowe': 'Traditional capital'
    }
}

def detect_language_and_code_switching(text):
    """Enhanced language detection for Setswana-English code-switching"""
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words)
    
    if total_words == 0:
        return "unknown", False, {}
    
    # Count Setswana indicators
    setswana_count = 0
    detected_setswana_words = []
    
    for word in words:
        if word in SETSWANA_LEXICON['common_words']:
            setswana_count += 1
            detected_setswana_words.append(word)
        elif word in SETSWANA_LEXICON['positive']:
            setswana_count += 1
            detected_setswana_words.append(f"{word} (positive)")
        elif word in SETSWANA_LEXICON['negative']:
            setswana_count += 1
            detected_setswana_words.append(f"{word} (negative)")
        elif word in SETSWANA_LEXICON['political']:
            setswana_count += 1
            detected_setswana_words.append(f"{word} (political)")
    
    setswana_ratio = setswana_count / total_words
    
    # Determine language
    if setswana_ratio > 0.6:
        language = "Setswana"
        code_switching = False
    elif setswana_ratio > 0.1:
        language = "Setswana-English"
        code_switching = True
    else:
        language = "English"
        code_switching = False
    
    return language, code_switching, {
        'setswana_words_found': detected_setswana_words,
        'setswana_ratio': round(setswana_ratio, 2),
        'total_words': total_words,
        'setswana_word_count': setswana_count
    }

def analyze_english_sentiment(text):
    """Analyze English sentiment using transformers"""
    try:
        from transformers import pipeline
        
        # Initialize sentiment pipeline (cached after first use)
        if not hasattr(analyze_english_sentiment, 'pipeline'):
            analyze_english_sentiment.pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        
        result = analyze_english_sentiment.pipeline(text)
        
        # Map labels to consistent format
        label_mapping = {
            'LABEL_0': 'negative',
            'LABEL_1': 'neutral', 
            'LABEL_2': 'positive',
            'NEGATIVE': 'negative',
            'NEUTRAL': 'neutral',
            'POSITIVE': 'positive'
        }
        
        sentiment = label_mapping.get(result[0]['label'], result[0]['label'].lower())
        confidence = result[0]['score']
        
        return sentiment, confidence, {'model': 'transformers', 'original_label': result[0]['label']}
        
    except ImportError:
        # Fallback to basic keyword analysis if transformers not available
        return analyze_basic_english_sentiment(text)
    except Exception as e:
        print(f"Transformers model failed: {e}, falling back to basic analysis")
        return analyze_basic_english_sentiment(text)

def analyze_basic_english_sentiment(text):
    """Fallback basic English sentiment analysis"""
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 
        'fantastic', 'awesome', 'brilliant', 'perfect', 'outstanding', 'superb',
        'happy', 'pleased', 'satisfied', 'delighted', 'thrilled', 'excited'
    ]
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'disgusting',
        'disappointing', 'frustrated', 'angry', 'upset', 'sad', 'worried',
        'concerned', 'annoyed', 'irritated', 'furious', 'devastated'
    ]
    
    words = re.findall(r'\b\w+\b', text.lower())
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    
    if pos_count > neg_count:
        sentiment = "positive"
        confidence = min(0.85, 0.6 + (pos_count - neg_count) * 0.05)
    elif neg_count > pos_count:
        sentiment = "negative" 
        confidence = min(0.85, 0.6 + (neg_count - pos_count) * 0.05)
    else:
        sentiment = "neutral"
        confidence = 0.5
    
    found_words = {
        'positive': [w for w in words if w in positive_words],
        'negative': [w for w in words if w in negative_words]
    }
    
    return sentiment, confidence, {'model': 'basic_keywords', 'found_words': found_words}

def analyze_setswana_sentiment(text):
    """Enhanced Setswana sentiment analysis using lexicon"""
    words = re.findall(r'\b\w+\b', text.lower())
    
    positive_score = 0
    negative_score = 0
    found_words = {'positive': [], 'negative': []}
    
    for word in words:
        if word in SETSWANA_LEXICON['positive']:
            positive_score += 1
            found_words['positive'].append(f"{word} ({SETSWANA_LEXICON['positive'][word]})")
        elif word in SETSWANA_LEXICON['negative']:
            negative_score += 1
            found_words['negative'].append(f"{word} ({SETSWANA_LEXICON['negative'][word]})")
    
    # Determine sentiment
    if positive_score > negative_score:
        sentiment = "positive"
        confidence = min(0.9, 0.6 + (positive_score - negative_score) * 0.1)
    elif negative_score > positive_score:
        sentiment = "negative"
        confidence = min(0.9, 0.6 + (negative_score - positive_score) * 0.1)
    else:
        sentiment = "neutral"
        confidence = 0.5 if positive_score == 0 and negative_score == 0 else 0.6
    
    return sentiment, confidence, found_words

def analyze_hybrid_sentiment(text, language, code_switching):
    """Hybrid sentiment analysis combining English and Setswana"""
    
    # Get English sentiment
    eng_sentiment, eng_confidence, eng_details = analyze_english_sentiment(text)
    
    # Get Setswana sentiment
    set_sentiment, set_confidence, set_words = analyze_setswana_sentiment(text)
    
    # Combine results based on language detection
    if language == "English":
        # Primarily English - use English model but boost with Setswana words if found
        final_sentiment = eng_sentiment
        final_confidence = eng_confidence
        
        # Boost confidence if Setswana words support the sentiment
        if set_words['positive'] and eng_sentiment == 'positive':
            final_confidence = min(0.95, final_confidence + 0.1)
        elif set_words['negative'] and eng_sentiment == 'negative':
            final_confidence = min(0.95, final_confidence + 0.1)
            
        model_used = "english_primary"
        
    elif language == "Setswana":
        # Primarily Setswana - use Setswana lexicon but consider English context
        final_sentiment = set_sentiment
        final_confidence = set_confidence
        
        # If no Setswana sentiment words found, fall back to English
        if not set_words['positive'] and not set_words['negative']:
            final_sentiment = eng_sentiment
            final_confidence = eng_confidence * 0.8  # Lower confidence for fallback
            model_used = "setswana_fallback_english"
        else:
            model_used = "setswana_primary"
            
    else:  # Code-switching
        # Weighted combination based on strength of signals
        setswana_signal_strength = len(set_words['positive']) + len(set_words['negative'])
        
        if setswana_signal_strength > 0:
            # Strong Setswana signals - blend the results
            if set_sentiment == eng_sentiment:
                # Both agree - high confidence
                final_sentiment = set_sentiment
                final_confidence = min(0.95, (set_confidence + eng_confidence) / 2 + 0.1)
            else:
                # Disagreement - use higher confidence one
                if set_confidence > eng_confidence:
                    final_sentiment = set_sentiment
                    final_confidence = set_confidence * 0.9
                else:
                    final_sentiment = eng_sentiment
                    final_confidence = eng_confidence * 0.9
            model_used = "hybrid_blend"
        else:
            # No strong Setswana signals - use English
            final_sentiment = eng_sentiment
            final_confidence = eng_confidence
            model_used = "english_dominant"
    
    return final_sentiment, final_confidence, {
        'model_used': model_used,
        'english_analysis': {'sentiment': eng_sentiment, 'confidence': eng_confidence, 'details': eng_details},
        'setswana_analysis': {'sentiment': set_sentiment, 'confidence': set_confidence, 'words': set_words},
        'combination_logic': f"Language: {language}, Code-switching: {code_switching}"
    }

def extract_political_context(text):
    """Extract political entities and keywords"""
    text_lower = text.lower()
    found_entities = []
    found_keywords = []
    
    # Check for political parties
    for party, full_name in POLITICAL_ENTITIES['parties'].items():
        if party.lower() in text_lower or full_name.lower() in text_lower:
            found_entities.append({'entity': party, 'type': 'party', 'full_name': full_name})
    
    # Check for political leaders
    for leader, full_name in POLITICAL_ENTITIES['leaders'].items():
        if leader.lower() in text_lower or full_name.lower() in text_lower:
            found_entities.append({'entity': leader, 'type': 'leader', 'full_name': full_name})
    
    # Check for locations
    for location, description in POLITICAL_ENTITIES['locations'].items():
        if location.lower() in text_lower:
            found_entities.append({'entity': location, 'type': 'location', 'description': description})
    
    # Check for Setswana political terms
    for term, meaning in SETSWANA_LEXICON['political'].items():
        if term in text_lower:
            found_keywords.append({'term': term, 'meaning': meaning, 'language': 'Setswana'})
    
    return found_entities, found_keywords

@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """Enhanced sentiment analysis with Setswana support"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Language detection and code-switching analysis
        language, code_switching, lang_details = detect_language_and_code_switching(text)
        
        # Enhanced hybrid sentiment analysis
        sentiment, confidence, analysis_details = analyze_hybrid_sentiment(text, language, code_switching)
        
        # Extract political context
        political_entities, political_keywords = extract_political_context(text)
        
        # Build comprehensive response
        result = {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "detected_language": language,
            "code_switching_detected": code_switching,
            "model_used": analysis_details['model_used'],
            "language_analysis": lang_details,
            "sentiment_analysis": analysis_details,
            "sentiment_words": analysis_details['setswana_analysis']['words'],
            "political_context": {
                "entities": political_entities,
                "keywords": political_keywords
            },
            "text_length": len(text),
            "word_count": len(re.findall(r'\b\w+\b', text))
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/lexicon', methods=['GET'])
def get_lexicon():
    """Get the Setswana lexicon for reference"""
    return jsonify({
        "setswana_lexicon": SETSWANA_LEXICON,
        "political_entities": POLITICAL_ENTITIES,
        "total_setswana_words": sum(len(category) for category in SETSWANA_LEXICON.values()),
        "total_political_entities": sum(len(category) for category in POLITICAL_ENTITIES.values())
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        "status": "healthy",
        "service": "Botswana Political Sentiment Analysis",
        "version": "1.0.0",
        "features": [
            "Setswana language detection",
            "Code-switching analysis", 
            "Political entity recognition",
            "Lexicon-based sentiment analysis"
        ],
        "lexicon_stats": {
            "setswana_words": len(SETSWANA_LEXICON['common_words']),
            "positive_words": len(SETSWANA_LEXICON['positive']),
            "negative_words": len(SETSWANA_LEXICON['negative']),
            "political_terms": len(SETSWANA_LEXICON['political'])
        }
    })

@app.route('/api/test-examples', methods=['GET'])
def test_examples():
    """Get test examples for different scenarios"""
    return jsonify({
        "examples": [
            {
                "text": "I love the new policy changes",
                "description": "Pure English positive sentiment",
                "expected": "positive sentiment, English language, transformers model"
            },
            {
                "text": "This government is terrible and disappointing",
                "description": "Pure English negative sentiment", 
                "expected": "negative sentiment, English language, transformers model"
            },
            {
                "text": "Ke rata mmuso o, o dira sentle thata",
                "description": "Pure Setswana positive sentiment",
                "expected": "positive sentiment, Setswana language, lexicon model"
            },
            {
                "text": "Mmuso o o botlhoko, ga o dire sepe",
                "description": "Pure Setswana negative sentiment",
                "expected": "negative sentiment, Setswana language, lexicon model"
            },
            {
                "text": "The government is doing botlhoko work",
                "description": "Code-switching: English + negative Setswana",
                "expected": "negative sentiment, code-switching, hybrid analysis"
            },
            {
                "text": "Masisi is doing sentle work for batho",
                "description": "Code-switching: English + positive Setswana",
                "expected": "positive sentiment, code-switching, hybrid analysis"
            },
            {
                "text": "BDP le UDC ba lwantshana, but I think it's good for democracy",
                "description": "Complex code-switching with political entities",
                "expected": "mixed analysis, political entities detected"
            },
            {
                "text": "The palamente should help batho more",
                "description": "Code-switching with political terms",
                "expected": "neutral/positive, political keywords detected"
            }
        ]
    })

# === LEXICON MANAGEMENT ENDPOINTS ===
@app.route('/api/lexicon/stats', methods=['GET'])
def lexicon_stats():
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

@app.route('/api/lexicon/search', methods=['GET'])
def search_lexicon():
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

@app.route('/api/lexicon/add', methods=['POST'])
def add_word_to_lexicon():
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
            # Update the legacy format for immediate use
            global SETSWANA_LEXICON
            SETSWANA_LEXICON = get_legacy_lexicon_format()
            
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

@app.route('/api/lexicon/suggest', methods=['POST'])
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

# === TRAINING DATA COLLECTION ENDPOINTS ===
@app.route('/api/feedback/sentiment', methods=['POST'])
def submit_sentiment_feedback():
    """Submit feedback on sentiment analysis"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        predicted_sentiment = data.get('predicted_sentiment', '')
        predicted_confidence = data.get('predicted_confidence', 0.0)
        user_sentiment = data.get('user_sentiment', '')
        user_confidence = data.get('user_confidence', 1.0)
        
        if not all([text, predicted_sentiment, user_sentiment]):
            return jsonify({"error": "text, predicted_sentiment, and user_sentiment are required"}), 400
        
        success = training_collector.collect_sentiment_feedback(
            text, predicted_sentiment, predicted_confidence, 
            user_sentiment, user_confidence
        )
        
        if success:
            return jsonify({
                "message": "Feedback submitted successfully",
                "agreement": predicted_sentiment == user_sentiment
            })
        else:
            return jsonify({"error": "Failed to submit feedback"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/stats', methods=['GET'])
def training_stats():
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

@app.route('/api/training/export', methods=['POST'])
def export_training_data():
    """Export training dataset"""
    try:
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

@app.route('/api/admin/pending-suggestions', methods=['GET'])
def get_pending_suggestions():
    """Get pending word suggestions for admin review"""
    try:
        limit = request.args.get('limit', 20, type=int)
        suggestions = training_collector.get_pending_word_suggestions(limit)
        corrections = training_collector.get_pending_corrections(limit)
        
        return jsonify({
            'word_suggestions': suggestions,
            'sentiment_corrections': corrections,
            'total_suggestions': len(suggestions),
            'total_corrections': len(corrections)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === DASHBOARD ENDPOINTS (for frontend compatibility) ===
@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    """Get dashboard overview statistics from real collected data"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Get real data from storage
        overview_stats = data_storage.get_dashboard_overview(days)
        
        return jsonify({
            'stats': overview_stats,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/trends', methods=['GET'])
def dashboard_trends():
    """Get sentiment trends over time from real collected data"""
    try:
        days = request.args.get('days', 7, type=int)
        keyword = request.args.get('keyword')
        
        # Get real trend data from storage
        trends = data_storage.get_sentiment_trends(days)
        
        # Apply keyword filter if provided
        if keyword:
            filtered_trends = []
            for trend in trends:
                # This is a simplified keyword filter - in production you'd want more sophisticated filtering
                filtered_trends.append(trend)
            trends = filtered_trends
        
        return jsonify({
            'trends': trends,
            'filters': {
                'days': days,
                'keyword': keyword,
                'granularity': 'daily'
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/posts', methods=['GET'])
def dashboard_posts():
    """Get recent posts from real collected data"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sentiment_filter = request.args.get('sentiment', None)
        
        # Get real posts data from storage
        posts_data = data_storage.get_recent_posts(page, per_page, sentiment_filter)
        
        return jsonify({
            'posts': posts_data['posts'],
            'pagination': posts_data['pagination'],
            'filters': {
                'sentiment': sentiment_filter,
                'platform': None,
                'keyword': None
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/political-entities', methods=['GET'])
def dashboard_political_entities():
    """Get political entity sentiment from real collected data"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Get real political entity data from storage
        entities = data_storage.get_political_entities(days)
        
        return jsonify({
            'entities': entities,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/language-breakdown', methods=['GET'])
def dashboard_language_breakdown():
    """Get language breakdown (mock data for testing)"""
    try:
        days = request.args.get('days', 7, type=int)
        
        mock_breakdown = {
            'language_distribution': {
                'English': {'count': 80, 'percentage': 53.3, 'avg_confidence': 0.85},
                'Setswana': {'count': 45, 'percentage': 30.0, 'avg_confidence': 0.78},
                'Setswana-English': {'count': 25, 'percentage': 16.7, 'avg_confidence': 0.72}
            },
            'code_switching_distribution': {
                'True': 25,
                'False': 125
            },
            'total_posts': 150
        }
        
        return jsonify({
            'language_breakdown': mock_breakdown,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/real-time-stats', methods=['GET'])
def dashboard_real_time_stats():
    """Get real-time stats (mock data for testing)"""
    try:
        return jsonify({
            'posts_last_hour': 12,
            'sentiment_distribution': {
                'positive': 5,
                'negative': 3,
                'neutral': 4
            },
            'top_keywords': [
                {'keyword': 'mmuso', 'count': 8},
                {'keyword': 'BDP', 'count': 6},
                {'keyword': 'kgethololo', 'count': 4}
            ],
            'active_platforms': {
                'twitter': 10,
                'facebook': 2
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === MODEL TRAINING ENDPOINTS ===
@app.route('/api/training/prepare-dataset', methods=['POST'])
def prepare_training_dataset():
    """Prepare training dataset from all sources"""
    try:
        include_feedback = request.json.get('include_user_feedback', True) if request.json else True
        
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

@app.route('/api/training/train-model', methods=['POST'])
def train_model():
    """Start model training process"""
    try:
        data = request.json or {}
        include_feedback = data.get('include_user_feedback', True)
        train_transformers = data.get('train_transformers', True)
        
        # Run training pipeline in background (for production, use Celery)
        results = model_trainer.full_training_pipeline(include_feedback, train_transformers)
        
        return jsonify({
            "message": "Model training completed" if results['success'] else "Model training failed",
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/quick-retrain', methods=['POST'])
def quick_retrain():
    """Quick retrain with current data (lexicon + corrections only)"""
    try:
        # Prepare minimal dataset
        texts, labels = model_trainer.prepare_training_data(include_user_feedback=True)
        
        # Save dataset
        dataset_path = model_trainer.save_training_dataset(texts, labels)
        
        # Update lexicon suggestions
        suggestions_count = model_trainer.update_lexicon_from_training(texts, labels)
        
        # Update the legacy lexicon format
        global SETSWANA_LEXICON
        SETSWANA_LEXICON = get_legacy_lexicon_format()
        
        return jsonify({
            "message": "Quick retrain completed",
            "dataset_path": dataset_path,
            "training_examples": len(texts),
            "lexicon_suggestions": suggestions_count,
            "lexicon_updated": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === WEB SCRAPING DATA COLLECTION ===
@app.route('/api/collect/web-scraping', methods=['POST'])
def collect_web_data():
    """Collect data using web scraping and update dashboard data"""
    try:
        # Collect and store data with sentiment analysis
        result = data_storage.collect_and_store_data(force_refresh=True)
        
        if result.get('success'):
            return jsonify({
                "message": "Web scraping data collection and analysis completed",
                "success": True,
                "total_collected": result['total_collected'],
                "analyzed_posts": result.get('analyzed', 0),
                "timestamp": result['timestamp'],
                "dashboard_updated": True
            })
        else:
            return jsonify({
                "message": "Data collection failed",
                "success": False,
                "error": result.get('error', 'Unknown error'),
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/collect/status', methods=['GET'])
def collection_status():
    """Get status of data collection capabilities"""
    try:
        # Get current data stats
        stored_posts = data_storage.get_stored_data()
        
        return jsonify({
            "available_sources": {
                "reddit_r_botswana": {
                    "status": "active",
                    "description": "Public Reddit API - no authentication required",
                    "data_type": "Political discussions from r/Botswana"
                },
                "mock_social_media": {
                    "status": "active", 
                    "description": "Generated realistic Botswana political content",
                    "data_type": "Sample posts in English and Setswana"
                },
                "news_headlines": {
                    "status": "active",
                    "description": "Botswana political news headlines",
                    "data_type": "Political news and announcements"
                },
                "web_scraping": {
                    "status": "available",
                    "description": "Public website scraping (news sites, forums)",
                    "data_type": "Articles and discussions from public sources"
                }
            },
            "current_data": {
                "total_posts_stored": len(stored_posts),
                "last_collection": data_storage._last_collection.isoformat() if data_storage._last_collection else None,
                "data_sources_in_storage": list(set(post.get('platform', 'unknown') for post in stored_posts))
            },
            "facebook_api_required": False,
            "twitter_api_required": False,
            "target_hashtags": [
                "#BotswanaPolitics", "#BDP2024", "#UDC2024", "#Masisi", 
                "#Boko", "#BotswanaElections", "#BWPolitics"
            ],
            "target_keywords": [
                "Botswana politics", "BDP", "UDC", "BCP", "Masisi", "Boko",
                "mmuso", "polotiki", "kgethololo", "setšhaba", "palamente"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/analytics', methods=['GET'])
def dashboard_analytics():
    """Get advanced analytics and insights"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Get advanced analytics from storage
        analytics = data_storage.get_advanced_analytics(days)
        
        return jsonify({
            'analytics': analytics,
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/refresh', methods=['POST'])
def refresh_dashboard_data():
    """Manually refresh dashboard data"""
    try:
        # Force refresh the stored data
        result = data_storage.collect_and_store_data(force_refresh=True)
        
        if result.get('success'):
            # Get updated overview stats
            overview = data_storage.get_dashboard_overview()
            
            return jsonify({
                "message": "Dashboard data refreshed successfully",
                "success": True,
                "collection_result": result,
                "updated_stats": overview,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "message": "Failed to refresh dashboard data",
                "success": False,
                "error": result.get('error', 'Unknown error')
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize data if none exists
    stored_data = data_storage.get_stored_data()
    if not stored_data:
        print("🔄 No data found, collecting initial data...")
        init_result = data_storage.collect_and_store_data(force_refresh=True)
        if init_result.get('success'):
            print(f"✅ Initialized with {init_result['total_collected']} posts")
        else:
            print("⚠️  Initial data collection failed, dashboard will be empty")
    else:
        print(f"📊 Found {len(stored_data)} existing posts in storage")
    
    print("🚀 Starting Enhanced Botswana Political Sentiment Analysis API")
    print("📍 Available endpoints:")
    print("   POST /api/sentiment - Analyze text sentiment")
    print("   GET  /api/health - Health check")
    print("   GET  /api/lexicon - View Setswana lexicon")
    print("   GET  /api/test-examples - Get test examples")
    print("")
    print("📚 Lexicon Management:")
    print("   GET  /api/lexicon/stats - Lexicon statistics")
    print("   GET  /api/lexicon/search?q=word - Search lexicon")
    print("   POST /api/lexicon/add - Add word to lexicon")
    print("   POST /api/lexicon/suggest - Suggest new word")
    print("")
    print("🎓 Training Data Collection:")
    print("   POST /api/feedback/sentiment - Submit sentiment feedback")
    print("   GET  /api/training/stats - Training statistics")
    print("   POST /api/training/export - Export training dataset")
    print("   GET  /api/admin/pending-suggestions - Admin review")
    print("")
    print("🤖 Model Training:")
    print("   POST /api/training/prepare-dataset - Prepare training data")
    print("   POST /api/training/train-model - Full model training")
    print("   POST /api/training/quick-retrain - Quick lexicon update")
    print("")
    print("📊 Dashboard (Real Data from Web Scraping):")
    print("   GET  /api/dashboard/overview - Overview statistics")
    print("   GET  /api/dashboard/trends - Sentiment trends")
    print("   GET  /api/dashboard/posts - Recent posts")
    print("   GET  /api/dashboard/political-entities - Entity sentiment")
    print("   GET  /api/dashboard/analytics - Advanced analytics & insights")
    print("   GET  /api/dashboard/language-breakdown - Language analysis")
    print("   GET  /api/dashboard/real-time-stats - Real-time stats")
    print("   POST /api/dashboard/refresh - Refresh dashboard data")
    print("")
    print("🕷️  Web Scraping Data Collection (No Facebook API needed):")
    print("   POST /api/collect/web-scraping - Collect from web sources")
    print("   GET  /api/collect/status - Check available data sources")
    print("")
    print("🌐 Frontend should connect to: http://localhost:5000")
    print("✨ Dashboard now shows REAL data from web scraping!")
    print("🎯 Data sources: Reddit r/Botswana + Mock Botswana political content")
    print("🔄 Use POST /api/collect/web-scraping to refresh data")
    
    app.run(debug=True, host='0.0.0.0', port=5000)