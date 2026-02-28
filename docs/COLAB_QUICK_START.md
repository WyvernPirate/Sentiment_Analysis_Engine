# 🚀 Quick Colab Setup - Copy & Paste Ready

## Step 1: Setup (Copy this to first Colab cell)

```python
# 🇧🇼 Botswana Political Sentiment Analysis - Quick Setup
print("🚀 Setting up Botswana Political Sentiment Analysis...")

# Install all dependencies
!pip install flask flask-cors transformers torch datasets scikit-learn
!pip install requests beautifulsoup4 lxml pyngrok numpy pandas

# Create project structure
import os
os.makedirs('botswana_sentiment', exist_ok=True)
os.makedirs('botswana_sentiment/data', exist_ok=True)

print("✅ Dependencies installed and project structure created!")
```

## Step 2: Copy Your Files (5 separate cells)

### Cell 2A: Lexicon Manager
```python
%%writefile botswana_sentiment/lexicon_manager.py
# COPY THE ENTIRE CONTENT OF YOUR backend/lexicon_manager.py HERE
```

### Cell 2B: Data Collector  
```python
%%writefile botswana_sentiment/simple_data_collector.py
# COPY THE ENTIRE CONTENT OF YOUR backend/simple_data_collector.py HERE
```

### Cell 2C: Sentiment Analyzer
```python
%%writefile botswana_sentiment/sentiment_analyzer.py  
# COPY THE ENTIRE CONTENT OF YOUR backend/sentiment_analyzer.py HERE
```

### Cell 2D: Data Storage
```python
%%writefile botswana_sentiment/data_storage.py
# COPY THE ENTIRE CONTENT OF YOUR backend/data_storage.py HERE
```

### Cell 2E: Colab App
```python
%%writefile botswana_sentiment/colab_app.py
# COPY THE ENTIRE CONTENT OF YOUR backend/colab_app.py HERE
```

## Step 3: Start Server (Final cell)

```python
# 🌐 Start the public server
from pyngrok import ngrok
import threading
import time
import os

# Create ngrok tunnel
public_url = ngrok.connect(5000)
print(f"🌐 Your app is LIVE at: {public_url}")
print(f"🔗 Click this URL to access your app: {public_url}")
print(f"📊 API endpoint: {public_url}/api/sentiment")

# Change to project directory
os.chdir('botswana_sentiment')

# Start the Flask app
print("🚀 Starting Flask server...")
exec(open('colab_app.py').read())
```

---

## 🔧 What to do RIGHT NOW:

1. **Open Google Colab** → [colab.research.google.com](https://colab.research.google.com)
2. **Create new notebook**
3. **Copy Step 1 code** → Paste in first cell → Run it
4. **For each file in Step 2**: 
   - Create new cell
   - Copy the `%%writefile` line
   - Open the corresponding file from your backend folder
   - Copy ALL the content and paste after the `%%writefile` line
   - Run the cell
5. **Copy Step 3 code** → Paste in final cell → Run it
6. **Click the ngrok URL** that appears!

## 🚨 If you get stuck:

**Problem**: "File not found" errors
**Solution**: Make sure you copied ALL the file contents, not just the filename

**Problem**: Import errors  
**Solution**: Check that all 5 files were created successfully

**Problem**: ngrok tunnel fails
**Solution**: Run `!pip install pyngrok` again

**Problem**: Flask won't start
**Solution**: Make sure you're in the `botswana_sentiment` directory

Your app will be live and accessible via the ngrok URL! 🎉