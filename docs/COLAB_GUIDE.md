# 🚀 Google Colab Setup Guide - Sentiment Analysis Engine

This guide helps you deploy the Botswana Political Sentiment Analysis engine on Google Colab for free GPU access and public API hosting.

## 📋 Quick Start (5 Minutes)

### 1. Open Google Colab
1. Go to [colab.research.google.com](https://colab.research.google.com).
2. Create a **New notebook**.
3. Go to **Runtime** → **Change runtime type** → Select **GPU**.

### 2. Install Dependencies
Run this in the first cell:
```python
!pip install flask flask-cors transformers torch datasets scikit-learn
!pip install requests beautifulsoup4 lxml pyngrok numpy pandas
print("✅ Dependencies installed!")
```

### 3. Setup Project Structure
```python
import os
os.makedirs('botswana_sentiment', exist_ok=True)
os.makedirs('botswana_sentiment/data', exist_ok=True)
print("📁 Project structure created!")
```

### 4. Deploy Core Files
You need to copy the contents of your backend files into the following `%%writefile` cells:

*   **Lexicon Manager**: `%%writefile botswana_sentiment/lexicon_manager.py` (Paste `lexicon_manager.py` content)
*   **Sentiment Analyzer**: `%%writefile botswana_sentiment/sentiment_analyzer.py` (Paste `sentiment_analyzer.py` content)
*   **Data Storage**: `%%writefile botswana_sentiment/data_storage.py` (Paste `data_storage.py` content)
*   **Main App**: `%%writefile botswana_sentiment/app.py` (Paste `app.py` content)

### 5. Start the Server
```python
from pyngrok import ngrok
import os

# Connect to 5000
public_url = ngrok.connect(5000)
print(f"🌐 Public API URL: {public_url}")

# Run app
os.chdir('botswana_sentiment')
!python app.py
```

## 🔧 Features
- **Setswana-English Support**: Custom lexicon for Botswana political discourse.
- **Real-time Analytics**: Dashboard endpoints for sentiment trends.
- **Transformer-based**: Powered by XLM-RoBERTa for multilingual analysis.

---
**🇧🇼 Built for Botswana's unique political and linguistic landscape**
