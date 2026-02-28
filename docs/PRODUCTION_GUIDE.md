# 🚀 Botswana Political Sentiment Analysis Platform - Production Guide

## 📋 Project Overview

This is a comprehensive real-time political sentiment monitoring platform designed specifically for Botswana's unique linguistic landscape, supporting Setswana-English code-switching in political discourse.

### 🎯 Target Users
- **Political Organizations**: Monitor public opinion on policies and candidates
- **Researchers**: Academic research on political discourse and sentiment
- **Journalists**: Identify story leads and verify public sentiment trends
- **Government**: Transparent public opinion monitoring

## 🏗️ Architecture Overview

### Backend Structure
```
backend/
├── app_production.py           # Main production Flask API
├── simple_app.py              # Simple testing API (development)
├── config.py                  # Configuration management
├── models.py                  # Database schemas
├── lexicon_manager.py         # Setswana lexicon management
├── training_data_collector.py # Training data collection
├── model_trainer.py           # Model training pipeline
├── sentiment_analyzer.py      # Enhanced sentiment analysis
├── data_collector.py          # Social media data collection
├── routes/                    # API route blueprints
│   ├── sentiment.py          # Sentiment analysis endpoints
│   ├── dashboard.py          # Dashboard data endpoints
│   ├── lexicon.py            # Lexicon management endpoints
│   ├── training.py           # Training endpoints
│   └── admin.py              # Admin endpoints
├── services/                  # Business logic services
│   ├── sentiment_service.py  # Sentiment analysis service
│   └── trend_analysis_service.py # Political trend analysis
└── utils/                     # Utility functions
    └── validators.py          # Input validation
```

### Frontend Structure
```
frontend/src/
├── pages/
│   └── DashboardPage.tsx     # Main dashboard page
├── components/
│   └── LexiconManager.tsx    # Lexicon management interface
├── services/
│   └── api.ts                # API service layer
├── types/
│   └── index.ts              # TypeScript definitions
└── App.tsx                   # Main application component
```

## 🚀 Quick Start

### Development Mode (Simple Testing)
```bash
# Terminal 1: Start simple backend for testing
cd backend
python simple_app.py

# Terminal 2: Start frontend
cd frontend
npm start
```

### Production Mode (Full Platform)
```bash
# Terminal 1: Start production backend
cd backend
python app_production.py

# Terminal 2: Start frontend
cd frontend
npm start
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database Configuration
DATABASE_URL=sqlite:///botswana_sentiment.db
# For production: DATABASE_URL=postgresql://user:pass@localhost/botswana_sentiment

# Twitter API Credentials
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-twitter-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret

# Facebook API Credentials
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Redis Configuration (for background tasks)
REDIS_URL=redis://localhost:6379/0
```

### Frontend Configuration
Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:5000
```

## 📊 API Endpoints

### Production API (`app_production.py`)

#### Sentiment Analysis
- `POST /api/sentiment/analyze` - Analyze text sentiment
- `POST /api/sentiment/batch` - Batch sentiment analysis
- `POST /api/sentiment/feedback` - Submit user feedback

#### Dashboard
- `GET /api/dashboard/overview` - Overview statistics
- `GET /api/dashboard/trends` - Sentiment trends over time
- `GET /api/dashboard/posts` - Recent posts with analysis
- `GET /api/dashboard/political-entities` - Political entity sentiment
- `GET /api/dashboard/language-breakdown` - Language usage analysis
- `GET /api/dashboard/real-time-stats` - Real-time statistics

#### Lexicon Management
- `GET /api/lexicon/stats` - Lexicon statistics
- `POST /api/lexicon/add` - Add new word
- `GET /api/lexicon/search` - Search words
- `POST /api/lexicon/suggest` - Suggest word for review
- `GET /api/lexicon/export` - Export lexicon

#### Training
- `POST /api/training/prepare-dataset` - Prepare training data
- `POST /api/training/train-model` - Train XLM-RoBERTa model
- `POST /api/training/quick-retrain` - Quick lexicon update
- `GET /api/training/stats` - Training statistics
- `POST /api/training/export` - Export training data
- `POST /api/training/feedback` - Submit feedback

#### Admin
- `GET /api/admin/pending-suggestions` - Review suggestions
- `POST /api/admin/approve-word` - Approve word suggestion
- `GET /api/admin/system-stats` - System statistics
- `POST /api/admin/data-collection/trigger` - Trigger data collection
- `POST /api/admin/analysis/trigger` - Trigger analysis
- `POST /api/admin/cleanup/old-data` - Cleanup old data

### Simple API (`simple_app.py`)
- All lexicon management and training endpoints from production
- Simplified sentiment analysis for testing
- Compatible with existing frontend

## 🎯 Key Features

### 1. Real-time Political Sentiment Dashboard
- **Overview Cards**: Total posts, sentiment breakdown, language distribution
- **Trend Visualization**: Sentiment trends over time with interactive charts
- **Political Entity Analysis**: Sentiment breakdown by parties, leaders, locations
- **Language Analytics**: Setswana-English code-switching analysis

### 2. Advanced Sentiment Analysis
- **Hybrid Model**: Combines English transformers with Setswana lexicon
- **Code-switching Detection**: Identifies mixed Setswana-English usage
- **Political Context**: Recognizes Botswana political entities and terms
- **Confidence Scoring**: Provides reliability metrics for predictions

### 3. Dynamic Lexicon Management
- **Expandable Lexicon**: 100+ Setswana words with meanings and contexts
- **Category Management**: Positive, negative, political, Botswana-specific terms
- **User Contributions**: Suggest new words for community review
- **Search & Filter**: Find existing words and meanings

### 4. Model Training Pipeline
- **Data Collection**: Automated social media data gathering
- **User Feedback**: Collect corrections and improvements
- **Incremental Learning**: Continuous model improvement
- **Export Capabilities**: Generate training datasets

### 5. Admin Dashboard
- **System Monitoring**: Health checks and performance metrics
- **Content Moderation**: Review and approve user suggestions
- **Data Management**: Trigger collection and analysis processes
- **Maintenance Tools**: Cleanup and optimization utilities

## 🔄 Workflow

### For Researchers & Journalists
1. **Monitor Dashboard**: View real-time political sentiment trends
2. **Analyze Specific Content**: Use the analyzer for individual texts
3. **Export Data**: Download datasets for external analysis
4. **Track Entities**: Monitor sentiment around specific politicians/parties

### For Political Organizations
1. **Campaign Monitoring**: Track public sentiment about policies
2. **Competitor Analysis**: Monitor sentiment around other parties
3. **Language Insights**: Understand Setswana vs English usage patterns
4. **Trend Analysis**: Identify sentiment shifts over time

### For Developers & Administrators
1. **Expand Lexicon**: Add new Setswana political terms
2. **Train Models**: Improve accuracy with user feedback
3. **Monitor System**: Check health and performance metrics
4. **Manage Data**: Configure collection and retention policies

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python simple_app.py  # For testing
# OR
python app_production.py  # For full features

# Frontend
cd frontend
npm install
npm start
```

### Production
```bash
# Backend with Gunicorn
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_production:app

# Frontend build
cd frontend
npm run build
# Serve build/ directory with nginx or similar
```

### Docker (Recommended)
```dockerfile
# Backend Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_production:app"]

# Frontend Dockerfile
FROM node:16 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
```

## 📈 Scaling Considerations

### Database
- **Development**: SQLite (included)
- **Production**: PostgreSQL with proper indexing
- **Analytics**: Consider data warehouse for historical analysis

### Background Tasks
- **Development**: Synchronous processing
- **Production**: Celery + Redis for async data collection and analysis

### Caching
- **API Responses**: Redis caching for dashboard data
- **Model Predictions**: Cache frequent sentiment analyses

### Monitoring
- **Health Checks**: Built-in `/api/health` endpoint
- **Metrics**: Integrate with Prometheus/Grafana
- **Logging**: Structured logging for debugging

## 🔒 Security

### API Security
- **Rate Limiting**: Implement per-IP rate limits
- **Authentication**: Add JWT tokens for admin endpoints
- **Input Validation**: All inputs validated and sanitized

### Data Privacy
- **Anonymization**: Remove PII from collected social media data
- **Retention**: Automatic cleanup of old data
- **Compliance**: GDPR/POPIA compliance for user data

## 🤝 Contributing

### Adding New Features
1. **Backend**: Add routes in `routes/` directory
2. **Frontend**: Create components in appropriate directories
3. **API**: Update `services/api.ts` with new endpoints
4. **Types**: Add TypeScript definitions in `types/`

### Expanding Lexicon
1. Use the Lexicon Manager interface
2. Submit word suggestions for review
3. Contribute training data through feedback
4. Help with Setswana translations and meanings

## 📞 Support

### Troubleshooting
1. **Check Health**: `GET /api/health` for system status
2. **Review Logs**: Check console output for errors
3. **Verify Config**: Ensure environment variables are set
4. **Test APIs**: Use simple_app.py for isolated testing

### Common Issues
- **CORS Errors**: Check frontend API URL configuration
- **Database Errors**: Verify database connection and permissions
- **Model Loading**: Ensure transformers library is installed
- **Social Media APIs**: Verify API credentials and rate limits

---

**🇧🇼 Built for Botswana's unique political and linguistic landscape**