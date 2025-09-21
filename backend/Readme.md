# Botswana Political Sentiment Analysis Platform

## Overview
A comprehensive real-time political sentiment monitoring platform designed specifically for Botswana's unique linguistic landscape, supporting Setswana-English code-switching in political discourse.

## 🎯 Target Users
- **Political Organizations**: Monitor public opinion on policies and candidates
- **Researchers**: Academic research on political discourse and sentiment
- **Journalists**: Identify story leads and verify public sentiment trends
- **Government**: Transparent public opinion monitoring

## 🚀 Key Features

### Real-time Data Collection
- Twitter API v2 integration for political hashtags and keywords
- Facebook Graph API for public political pages
- Automated collection with Botswana-specific political terms
- Support for both English and Setswana content

### Advanced Sentiment Analysis
- Custom XLM-RoBERTa model trained on Setswana-English code-switching data
- Political context-aware sentiment classification
- Automatic language detection (English, Setswana, Code-switching)
- Political entity and keyword extraction

### Comprehensive Dashboard API
- Real-time sentiment trends visualization
- Political party/candidate sentiment comparison
- Language usage analytics
- Historical trend analysis

## 🛠 Technology Stack
- **Backend**: Flask, SQLAlchemy, Transformers
- **Database**: SQLite (development) / PostgreSQL (production)
- **ML**: XLM-RoBERTa, PyTorch, scikit-learn
- **APIs**: Twitter API v2, Facebook Graph API
- **Background Tasks**: Celery + Redis

## 📋 Setup Instructions

### 1. Environment Setup
```bash
# Clone and navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file with your API credentials:
# - Twitter Bearer Token (required)
# - Facebook Access Token (optional)
# - Database URL (optional, defaults to SQLite)
```

### 3. Initialize Platform
```bash
# Run setup script
python setup.py

# Train sentiment model (optional, uses fallback if skipped)
python train_sentiment_model.py
```

### 4. Start Services
```bash
# Start Flask API
python app.py

# In separate terminal - start data collection (optional)
python -c "from data_collector import collect_all_data; collect_all_data()"
```

## 📡 API Endpoints

### Core Sentiment Analysis
- `POST /api/sentiment` - Analyze text sentiment
- `GET /api/health` - System health check

### Dashboard Data
- `GET /api/dashboard/overview` - Overview statistics
- `GET /api/dashboard/trends` - Sentiment trends over time
- `GET /api/dashboard/posts` - Recent posts with analysis

### Data Management
- `POST /api/collect/trigger` - Trigger data collection
- `POST /api/analyze/trigger` - Trigger sentiment analysis
- `GET /api/config` - Get platform configuration

## 🔧 API Usage Examples

### Analyze Sentiment
```bash
curl -X POST http://localhost:5000/api/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Ke rata mmuso o, o dira sentle thata"}'
```

Response:
```json
{
  "sentiment": "positive",
  "confidence": 0.89,
  "detected_language": "Setswana-English",
  "code_switching_detected": true,
  "political_keywords": ["mmuso"],
  "political_entities": []
}
```

### Get Dashboard Overview
```bash
curl http://localhost:5000/api/dashboard/overview?days=7
```

### Get Sentiment Trends
```bash
curl http://localhost:5000/api/dashboard/trends?days=30&keyword=BDP
```

## 🗃 Database Schema

### SocialMediaPost
- Platform, post ID, text content
- Author information and engagement metrics
- Creation and collection timestamps
- Location data (if available)

### SentimentAnalysis
- Sentiment classification results
- Language detection and code-switching flags
- Political entity and keyword extraction
- Model version and confidence scores

### PoliticalTrend
- Aggregated sentiment trends by date/hour
- Keyword-specific trend analysis
- Language usage breakdowns

## 🎯 Political Context Features

### Supported Political Entities
- **Parties**: BDP, UDC, BCP, AP
- **Leaders**: Masisi, Boko, Saleshando
- **Locations**: Gaborone, Francistown, Maun
- **Institutions**: Parliament, Government

### Monitored Keywords
- English: politics, election, parliament, government
- Setswana: polotiki, kgethololo, palamente, mmuso
- Code-switching combinations

## 🔍 Language Detection

The platform automatically detects:
- **English**: Standard English political discourse
- **Setswana**: Native Setswana political content
- **Code-switching**: Mixed Setswana-English usage (common in Botswana)

## 📊 Model Training

### Custom Setswana Model
```bash
# Train with your dataset
python train_sentiment_model.py

# The model will be saved to ./models/sentiment_model_setswana/
# API automatically uses custom model when available
```

### Training Data Format
```csv
text,label
"I love this policy, it is amazing!",2
"Ke rata pholisi e, e monate thata.",2
"The service was botlhoko.",0
"Mmuso o dira sentle.",2
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production settings
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/botswana_sentiment
SECRET_KEY=your-secure-secret-key

# API Credentials
TWITTER_BEARER_TOKEN=your-token
FACEBOOK_ACCESS_TOKEN=your-token

# Background Tasks
REDIS_URL=redis://localhost:6379/0
```

### Background Data Collection
```bash
# Set up Celery for automated collection
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the health endpoint: `GET /api/health`
2. Review logs in the `logs/` directory
3. Ensure all environment variables are set correctly
4. Verify API credentials are valid

## 🔮 Roadmap

- [ ] Real-time WebSocket updates
- [ ] Geographic sentiment mapping
- [ ] Advanced political entity recognition
- [ ] Multi-language dashboard interface
- [ ] Automated report generation
- [ ] Integration with more social media platforms