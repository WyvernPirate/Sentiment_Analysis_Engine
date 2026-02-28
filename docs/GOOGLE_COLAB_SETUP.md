# 🚀 Google Colab Setup Guide - Botswana Political Sentiment Analysis

## 📋 Overview

This guide will help you deploy your Botswana Political Sentiment Analysis engine on Google Colab. Colab is perfect for this project because it provides:

- ✅ **Free GPU/TPU access** for faster ML processing
- ✅ **Pre-installed ML libraries** (transformers, torch, etc.)
- ✅ **Public URL access** via ngrok tunneling
- ✅ **No local setup required** - runs entirely in the cloud
- ✅ **Easy sharing** with collaborators

## 🎯 What You'll Get

- **Full sentiment analysis API** running on Colab
- **Public URL** accessible from anywhere
- **Real-time data collection** from Reddit and other sources
- **Advanced analytics dashboard** with political insights
- **Setswana-English code-switching support**
- **Political entity tracking** (BDP, UDC, Masisi, Boko)

## 🚀 Quick Start (5 Minutes)

### Step 1: Open Google Colab
1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Sign in with your Google account
3. Click **"New notebook"**

### Step 2: Set Up Runtime
1. Go to **Runtime** → **Change runtime type**
2. Select **GPU** (for faster processing)
3. Click **Save**

### Step 3: Install Dependencies
Copy and paste this into the first cell:

```python
# Install required packages
!pip install flask flask-cors transformers torch datasets scikit-learn
!pip install requests beautifulsoup4 lxml pyngrok
!pip install numpy pandas

print("✅ All dependencies installed!")
```

### Step 4: Upload Your Code
Create a new cell and run:

```python
# Create project structure
import os
os.makedirs('botswana_sentiment', exist_ok=True)
os.makedirs('botswana_sentiment/data', exist_ok=True)

print("📁 Project structure created!")
```

### Step 5: Copy Your Engine Code
Create cells for each of your main files:

#### Cell 1: Lexicon Manager
```python
%%writefile botswana_sentiment/lexicon_manager.py
# Copy the entire content of your lexicon_manager.py here
```

#### Cell 2: Data Collector
```python
%%writefile botswana_sentiment/simple_data_collector.py
# Copy the entire content of your simple_data_collector.py here
```

#### Cell 3: Sentiment Analyzer
```python
%%writefile botswana_sentiment/sentiment_analyzer.py
# Copy the entire content of your sentiment_analyzer.py here
```

#### Cell 4: Data Storage
```python
%%writefile botswana_sentiment/data_storage.py
# Copy the entire content of your data_storage.py here
```

#### Cell 5: Main Flask App
```python
%%writefile botswana_sentiment/colab_app.py

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import re
import json
from datetime import datetime, timedelta
import threading
import time

# Import your modules
from lexicon_manager import lexicon_manager
from simple_data_collector import collect_simple_data
from data_storage import data_storage
from sentiment_analyzer import analyzer

app = Flask(__name__)
CORS(app)

# === CORE SENTIMENT ANALYSIS ===
@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of provided text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Use enhanced analyzer
        result = analyzer.analyze_sentiment(text)
        
        if not result:
            return jsonify({"error": "Analysis failed"}), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# === DASHBOARD ENDPOINTS ===
@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    """Get dashboard overview statistics from real data"""
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
    """Get advanced analytics and insights"""
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

@app.route('/api/collect/web-scraping', methods=['POST'])
def collect_web_data():
    """Collect data using web scraping"""
    try:
        result = data_storage.collect_and_store_data(force_refresh=True)
        
        if result.get('success'):
            return jsonify({
                "message": "Data collection completed",
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

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        stored_posts = data_storage.get_stored_data()
        
        return jsonify({
            "status": "healthy",
            "service": "Botswana Political Sentiment Analysis",
            "version": "1.0.0-colab",
            "total_posts": len(stored_posts),
            "timestamp": datetime.now().isoformat(),
            "platform": "Google Colab"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# === WEB INTERFACE ===
@app.route('/')
def home():
    """Simple web interface for testing"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🇧🇼 Botswana Political Sentiment Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 10px 0; }
            input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: white; padding: 15px; border-radius: 4px; margin: 10px 0; }
            .positive { border-left: 4px solid #28a745; }
            .negative { border-left: 4px solid #dc3545; }
            .neutral { border-left: 4px solid #6c757d; }
        </style>
    </head>
    <body>
        <h1>🇧🇼 Botswana Political Sentiment Analysis</h1>
        <p>Analyze political sentiment with Setswana-English code-switching support</p>
        
        <div class="container">
            <h3>🔍 Sentiment Analysis</h3>
            <textarea id="textInput" placeholder="Enter text in English, Setswana, or mixed..." rows="4"></textarea>
            <button onclick="analyzeSentiment()">Analyze Sentiment</button>
            <div id="result"></div>
        </div>
        
        <div class="container">
            <h3>📊 Quick Actions</h3>
            <button onclick="collectData()">🔄 Collect Fresh Data</button>
            <button onclick="viewHealth()">❤️ Check Health</button>
            <button onclick="viewAnalytics()">📈 View Analytics</button>
        </div>
        
        <div class="container">
            <h3>🧪 Test Examples</h3>
            <button onclick="testExample('BDP\\'s new policy looks promising for Botswana #BDP2024')">English Political</button>
            <button onclick="testExample('Ke dumela gore UDC e tla fetola Botswana #UDC2024')">Setswana Political</button>
            <button onclick="testExample('The mmuso is doing sentle work for batho')">Code-switching</button>
        </div>
        
        <script>
            async function analyzeSentiment() {
                const text = document.getElementById('textInput').value;
                if (!text.trim()) {
                    alert('Please enter some text');
                    return;
                }
                
                try {
                    const response = await fetch('/api/sentiment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    document.getElementById('result').innerHTML = '<div class="result">Error: ' + error.message + '</div>';
                }
            }
            
            function displayResult(result) {
                if (result.error) {
                    document.getElementById('result').innerHTML = '<div class="result">Error: ' + result.error + '</div>';
                    return;
                }
                
                const sentiment = result.sentiment || 'unknown';
                const confidence = Math.round((result.confidence || 0) * 100);
                const language = result.detected_language || 'Unknown';
                
                document.getElementById('result').innerHTML = `
                    <div class="result ${sentiment}">
                        <h4>Analysis Results:</h4>
                        <p><strong>Sentiment:</strong> ${sentiment.toUpperCase()} (${confidence}% confidence)</p>
                        <p><strong>Language:</strong> ${language}</p>
                        ${result.code_switching_detected ? '<p><strong>Code-switching detected!</strong></p>' : ''}
                        ${result.political_context && result.political_context.entities.length > 0 ? 
                          '<p><strong>Political entities:</strong> ' + result.political_context.entities.map(e => e.entity).join(', ') + '</p>' : ''}
                    </div>
                `;
            }
            
            function testExample(text) {
                document.getElementById('textInput').value = text;
                analyzeSentiment();
            }
            
            async function collectData() {
                try {
                    const response = await fetch('/api/collect/web-scraping', { method: 'POST' });
                    const result = await response.json();
                    alert('Data collection: ' + result.message + '\\nCollected: ' + result.total_collected + ' posts');
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function viewHealth() {
                try {
                    const response = await fetch('/api/health');
                    const result = await response.json();
                    alert('Status: ' + result.status + '\\nTotal posts: ' + result.total_posts + '\\nPlatform: ' + result.platform);
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function viewAnalytics() {
                window.open('/api/dashboard/analytics?days=7', '_blank');
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    print("🚀 Starting Botswana Political Sentiment Analysis on Google Colab")
    print("🌐 Web interface available at the public URL")
    print("📡 API endpoints ready for frontend integration")
    
    # Initialize data if none exists
    stored_data = data_storage.get_stored_data()
    if not stored_data:
        print("🔄 Collecting initial data...")
        init_result = data_storage.collect_and_store_data(force_refresh=True)
        if init_result.get('success'):
            print(f"✅ Initialized with {init_result['total_collected']} posts")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Step 6: Start the Server with Public URL
```python
# Install and setup ngrok for public access
!pip install pyngrok

from pyngrok import ngrok
import threading
import time

# Set up ngrok tunnel
public_url = ngrok.connect(5000)
print(f"🌐 Public URL: {public_url}")
print(f"🔗 Access your app at: {public_url}")
print(f"📊 Dashboard API: {public_url}/api/dashboard/analytics")
print(f"🔍 Sentiment API: {public_url}/api/sentiment")

# Change to project directory and start the app
import os
os.chdir('botswana_sentiment')

# Start the Flask app in a separate thread
def run_app():
    exec(open('colab_app.py').read())

app_thread = threading.Thread(target=run_app)
app_thread.daemon = True
app_thread.start()

print("✅ Server starting... Wait 10 seconds then click the public URL!")
time.sleep(10)
```

## 🎯 Complete Colab Notebook Template

Here's a ready-to-use notebook structure:

### Cell 1: Setup and Dependencies
```python
# 🚀 Botswana Political Sentiment Analysis - Google Colab Setup
print("🇧🇼 Setting up Botswana Political Sentiment Analysis Engine")

# Install dependencies
!pip install flask flask-cors transformers torch datasets scikit-learn
!pip install requests beautifulsoup4 lxml pyngrok numpy pandas

# Create project structure
import os
os.makedirs('botswana_sentiment', exist_ok=True)
os.makedirs('botswana_sentiment/data', exist_ok=True)

print("✅ Setup complete!")
```

### Cell 2-6: Copy Your Code Files
Use `%%writefile` to create each of your Python files:
- `lexicon_manager.py`
- `simple_data_collector.py` 
- `sentiment_analyzer.py`
- `data_storage.py`
- `colab_app.py`

### Cell 7: Start the Server
```python
# Start the public server
from pyngrok import ngrok
import threading
import time

# Create ngrok tunnel
public_url = ngrok.connect(5000)
print(f"🌐 Your app is live at: {public_url}")

# Start the app
os.chdir('botswana_sentiment')
exec(open('colab_app.py').read())
```

## 🔧 Advanced Colab Features

### GPU Acceleration
```python
# Check if GPU is available
import torch
if torch.cuda.is_available():
    print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
    print(f"📊 GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("⚠️ No GPU available, using CPU")
```

### Persistent Storage
```python
# Mount Google Drive for persistent storage
from google.colab import drive
drive.mount('/content/drive')

# Save data to Drive
import shutil
shutil.copytree('/content/botswana_sentiment/data', '/content/drive/MyDrive/botswana_sentiment_data')
print("💾 Data backed up to Google Drive")
```

### Scheduled Data Collection
```python
# Set up automatic data collection every hour
import schedule
import time
import threading

def collect_data_job():
    print("🔄 Scheduled data collection...")
    result = data_storage.collect_and_store_data(force_refresh=True)
    print(f"✅ Collected {result.get('total_collected', 0)} posts")

# Schedule data collection every hour
schedule.every().hour.do(collect_data_job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in background
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

print("⏰ Automatic data collection scheduled every hour")
```

## 🌐 Frontend Integration

Your frontend can now connect to the Colab-hosted API:

```javascript
// Update your frontend API URL to the ngrok URL
const API_BASE_URL = 'https://your-ngrok-url.ngrok.io';

// Example API calls
fetch(`${API_BASE_URL}/api/sentiment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'Your text here' })
});
```

## 🔒 Security and Best Practices

### Environment Variables
```python
# Set up environment variables in Colab
import os
from google.colab import userdata

# Store sensitive data in Colab secrets
try:
    twitter_token = userdata.get('TWITTER_BEARER_TOKEN')
    os.environ['TWITTER_BEARER_TOKEN'] = twitter_token
    print("✅ Twitter API configured")
except:
    print("⚠️ Twitter API not configured (optional)")
```

### Rate Limiting
```python
# Add rate limiting to prevent abuse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/sentiment', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_sentiment():
    # Your sentiment analysis code
    pass
```

## 📊 Monitoring and Logging

```python
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log API usage
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")

# Monitor performance
import time
from functools import wraps

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return decorated_function
```

## 🚀 Deployment Checklist

- [ ] ✅ Dependencies installed
- [ ] 📁 Project structure created  
- [ ] 📄 All Python files uploaded
- [ ] 🌐 ngrok tunnel established
- [ ] 🔄 Initial data collected
- [ ] 🧪 API endpoints tested
- [ ] 📊 Dashboard accessible
- [ ] 🔒 Security measures in place
- [ ] 📱 Frontend connected (optional)

## 🎯 Next Steps

1. **Test your setup**: Use the web interface to test sentiment analysis
2. **Collect data**: Run the data collection to populate your dashboard
3. **Connect frontend**: Update your React app to use the Colab URL
4. **Monitor performance**: Check logs and API response times
5. **Scale up**: Consider upgrading to Colab Pro for better resources

## 💡 Pro Tips

- **Keep the notebook running**: Colab sessions timeout after inactivity
- **Save regularly**: Use Google Drive integration for persistence
- **Monitor resources**: Check GPU/RAM usage in Colab
- **Use ngrok auth**: Set up ngrok authentication for security
- **Test thoroughly**: Verify all endpoints work before sharing

Your Botswana Political Sentiment Analysis engine is now running on Google Colab with a public URL! 🇧🇼