#!/usr/bin/env python3
"""
Google Colab Optimized Flask App
Botswana Political Sentiment Analysis Engine for Colab deployment
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime, timedelta

# Add current directory to Python path for imports
sys.path.append(os.getcwd())

try:
    from lexicon_manager import lexicon_manager
    from simple_data_collector import collect_simple_data
    from data_storage import data_storage
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all Python files are uploaded to Colab")

app = Flask(__name__)
CORS(app)

# === SENTIMENT ANALYSIS API ===
@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """Enhanced sentiment analysis for Colab"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Simple analysis for Colab (avoid complex dependencies)
        result = analyze_text_simple(text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def analyze_text_simple(text):
    """Simplified sentiment analysis for Colab environment"""
    import re
    
    # Get lexicon in simple format
    try:
        lexicon = lexicon_manager.lexicon
        
        # Language detection
        words = re.findall(r'\b\w+\b', text.lower())
        setswana_count = 0
        setswana_words_found = []
        
        for word in words:
            if 'common_words' in lexicon and word in lexicon['common_words']:
                setswana_count += 1
                setswana_words_found.append(word)
            elif 'positive' in lexicon and word in lexicon['positive']:
                setswana_count += 1
                setswana_words_found.append(f"{word} (positive)")
            elif 'negative' in lexicon and word in lexicon['negative']:
                setswana_count += 1
                setswana_words_found.append(f"{word} (negative)")
        
        total_words = len(words)
        setswana_ratio = setswana_count / total_words if total_words > 0 else 0
        
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
        
        # Sentiment analysis
        positive_score = 0
        negative_score = 0
        
        if 'positive' in lexicon:
            for word in words:
                if word in lexicon['positive']:
                    positive_score += 1
        
        if 'negative' in lexicon:
            for word in words:
                if word in lexicon['negative']:
                    negative_score += 1
        
        # English sentiment boost
        english_positive = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'wonderful']
        english_negative = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'disappointing']
        
        for word in words:
            if word in english_positive:
                positive_score += 1
            elif word in english_negative:
                negative_score += 1
        
        # Determine final sentiment
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = min(0.9, 0.6 + (positive_score - negative_score) * 0.1)
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(0.9, 0.6 + (negative_score - positive_score) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        # Political entity detection
        political_entities = []
        text_lower = text.lower()
        
        entities_to_check = {
            'BDP': 'party', 'UDC': 'party', 'BCP': 'party',
            'Masisi': 'leader', 'Boko': 'leader', 'Saleshando': 'leader'
        }
        
        for entity, entity_type in entities_to_check.items():
            if entity.lower() in text_lower:
                political_entities.append({'entity': entity, 'type': entity_type})
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "detected_language": language,
            "code_switching_detected": code_switching,
            "language_analysis": {
                "setswana_words_found": setswana_words_found,
                "setswana_ratio": round(setswana_ratio, 2),
                "total_words": total_words,
                "setswana_word_count": setswana_count
            },
            "political_context": {
                "entities": political_entities,
                "keywords": []
            },
            "model_used": "colab_hybrid",
            "text_length": len(text),
            "word_count": total_words
        }
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "detected_language": "English",
            "code_switching_detected": False,
            "error": str(e)
        }

# === DASHBOARD ENDPOINTS ===
@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    """Dashboard overview with real data"""
    try:
        days = request.args.get('days', 7, type=int)
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

@app.route('/api/dashboard/analytics', methods=['GET'])
def dashboard_analytics():
    """Advanced analytics for Colab"""
    try:
        days = request.args.get('days', 7, type=int)
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

# === DATA COLLECTION ===
@app.route('/api/collect/web-scraping', methods=['POST'])
def collect_web_data():
    """Collect data for Colab environment"""
    try:
        result = data_storage.collect_and_store_data(force_refresh=True)
        
        if result.get('success'):
            return jsonify({
                "message": "Data collection completed successfully",
                "success": True,
                "total_collected": result['total_collected'],
                "analyzed_posts": result.get('analyzed', 0),
                "timestamp": result['timestamp']
            })
        else:
            return jsonify({
                "message": "Data collection failed",
                "success": False,
                "error": result.get('error', 'Unknown error')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === HEALTH CHECK ===
@app.route('/api/health', methods=['GET'])
def health():
    """Health check for Colab"""
    try:
        stored_posts = data_storage.get_stored_data()
        
        return jsonify({
            "status": "healthy",
            "service": "Botswana Political Sentiment Analysis",
            "version": "1.0.0-colab",
            "platform": "Google Colab",
            "total_posts": len(stored_posts),
            "timestamp": datetime.now().isoformat(),
            "features": [
                "Setswana-English sentiment analysis",
                "Political entity detection", 
                "Code-switching support",
                "Real-time data collection",
                "Advanced analytics"
            ]
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# === WEB INTERFACE ===
@app.route('/')
def home():
    """Simple web interface for Colab testing"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🇧🇼 Botswana Political Sentiment Analysis</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                background: white; 
                padding: 25px; 
                border-radius: 12px; 
                margin: 15px 0; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                background: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            input, textarea { 
                width: 100%; 
                padding: 12px; 
                margin: 8px 0; 
                border: 2px solid #e9ecef; 
                border-radius: 6px; 
                font-size: 14px;
                box-sizing: border-box;
            }
            button { 
                background: #007bff; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 6px; 
                cursor: pointer; 
                margin: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            button:hover { background: #0056b3; transform: translateY(-1px); }
            button.success { background: #28a745; }
            button.warning { background: #ffc107; color: black; }
            button.info { background: #17a2b8; }
            .result { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 15px 0; 
                border-left: 4px solid #007bff;
            }
            .positive { border-left-color: #28a745; }
            .negative { border-left-color: #dc3545; }
            .neutral { border-left-color: #6c757d; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
            .badge { 
                display: inline-block; 
                padding: 4px 8px; 
                background: #007bff; 
                color: white; 
                border-radius: 12px; 
                font-size: 12px; 
                margin: 2px;
            }
            .status { font-size: 14px; color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🇧🇼 Botswana Political Sentiment Analysis</h1>
            <p>Advanced sentiment analysis with Setswana-English code-switching support</p>
            <div class="status">✅ Running on Google Colab</div>
        </div>
        
        <div class="container">
            <h3>🔍 Sentiment Analysis</h3>
            <textarea id="textInput" placeholder="Enter text in English, Setswana, or mixed (code-switching)..." rows="4"></textarea>
            <button onclick="analyzeSentiment()">🔍 Analyze Sentiment</button>
            <div id="result"></div>
        </div>
        
        <div class="container">
            <h3>🧪 Test Examples</h3>
            <div class="grid">
                <button onclick="testExample('BDP\\'s new policy looks promising for Botswana #BDP2024')">English Political</button>
                <button onclick="testExample('Ke dumela gore UDC e tla fetola Botswana #UDC2024')">Setswana Political</button>
                <button onclick="testExample('The mmuso is doing sentle work for batho')">Code-switching</button>
                <button onclick="testExample('Masisi o dira tiro e molemo for our setšhaba')">Mixed Political</button>
            </div>
        </div>
        
        <div class="container">
            <h3>📊 Data Management</h3>
            <div class="grid">
                <button class="success" onclick="collectData()">🔄 Collect Fresh Data</button>
                <button class="info" onclick="viewHealth()">❤️ System Health</button>
                <button class="warning" onclick="viewAnalytics()">📈 View Analytics</button>
                <button onclick="viewPosts()">📝 Recent Posts</button>
            </div>
        </div>
        
        <div class="container">
            <h3>🌐 API Endpoints</h3>
            <p><strong>Sentiment Analysis:</strong> POST /api/sentiment</p>
            <p><strong>Dashboard Overview:</strong> GET /api/dashboard/overview</p>
            <p><strong>Advanced Analytics:</strong> GET /api/dashboard/analytics</p>
            <p><strong>Data Collection:</strong> POST /api/collect/web-scraping</p>
            <p><strong>Health Check:</strong> GET /api/health</p>
        </div>
        
        <script>
            async function analyzeSentiment() {
                const text = document.getElementById('textInput').value;
                if (!text.trim()) {
                    alert('Please enter some text');
                    return;
                }
                
                document.getElementById('result').innerHTML = '<div class="result">🔄 Analyzing...</div>';
                
                try {
                    const response = await fetch('/api/sentiment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    document.getElementById('result').innerHTML = '<div class="result">❌ Error: ' + error.message + '</div>';
                }
            }
            
            function displayResult(result) {
                if (result.error) {
                    document.getElementById('result').innerHTML = '<div class="result">❌ Error: ' + result.error + '</div>';
                    return;
                }
                
                const sentiment = result.sentiment || 'unknown';
                const confidence = Math.round((result.confidence || 0) * 100);
                const language = result.detected_language || 'Unknown';
                
                let html = `
                    <div class="result ${sentiment}">
                        <h4>📊 Analysis Results:</h4>
                        <p><strong>Sentiment:</strong> <span style="color: ${getSentimentColor(sentiment)}">${sentiment.toUpperCase()}</span> (${confidence}% confidence)</p>
                        <p><strong>Language:</strong> ${language}</p>
                        ${result.code_switching_detected ? '<p><strong>🔄 Code-switching detected!</strong></p>' : ''}
                        <p><strong>Model:</strong> ${result.model_used}</p>
                `;
                
                if (result.language_analysis && result.language_analysis.setswana_words_found.length > 0) {
                    html += '<p><strong>Setswana words:</strong> ';
                    result.language_analysis.setswana_words_found.forEach(word => {
                        html += '<span class="badge">' + word + '</span>';
                    });
                    html += '</p>';
                }
                
                if (result.political_context && result.political_context.entities.length > 0) {
                    html += '<p><strong>Political entities:</strong> ';
                    result.political_context.entities.forEach(entity => {
                        html += '<span class="badge" style="background: #28a745">' + entity.entity + ' (' + entity.type + ')</span>';
                    });
                    html += '</p>';
                }
                
                html += '</div>';
                document.getElementById('result').innerHTML = html;
            }
            
            function getSentimentColor(sentiment) {
                switch(sentiment) {
                    case 'positive': return '#28a745';
                    case 'negative': return '#dc3545';
                    case 'neutral': return '#6c757d';
                    default: return '#000';
                }
            }
            
            function testExample(text) {
                document.getElementById('textInput').value = text;
                analyzeSentiment();
            }
            
            async function collectData() {
                try {
                    const response = await fetch('/api/collect/web-scraping', { method: 'POST' });
                    const result = await response.json();
                    alert('✅ ' + result.message + '\\n📊 Collected: ' + result.total_collected + ' posts\\n🧠 Analyzed: ' + result.analyzed_posts + ' posts');
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
            
            async function viewHealth() {
                try {
                    const response = await fetch('/api/health');
                    const result = await response.json();
                    alert('✅ Status: ' + result.status + '\\n📊 Total posts: ' + result.total_posts + '\\n🖥️ Platform: ' + result.platform + '\\n⏰ Time: ' + new Date(result.timestamp).toLocaleString());
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
            
            async function viewAnalytics() {
                window.open('/api/dashboard/analytics?days=7', '_blank');
            }
            
            async function viewPosts() {
                window.open('/api/dashboard/posts?per_page=10', '_blank');
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    print("🚀 Starting Botswana Political Sentiment Analysis on Google Colab")
    print("=" * 60)
    print("🌐 Web interface will be available at the ngrok URL")
    print("📡 API endpoints ready for integration")
    print("🇧🇼 Optimized for Botswana political content analysis")
    
    # Initialize data if none exists
    try:
        stored_data = data_storage.get_stored_data()
        if not stored_data:
            print("🔄 No existing data found, collecting initial data...")
            init_result = data_storage.collect_and_store_data(force_refresh=True)
            if init_result.get('success'):
                print(f"✅ Initialized with {init_result['total_collected']} posts")
            else:
                print("⚠️ Initial data collection failed, will use empty dashboard")
        else:
            print(f"📊 Found {len(stored_data)} existing posts in storage")
    except Exception as e:
        print(f"⚠️ Data initialization error: {e}")
    
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)