# Botswana Political Sentiment Analysis Platform

## Project Overview
A real-time political sentiment monitoring platform for Botswana that:
- Fetches live social media data (Twitter, Facebook)
- Analyzes sentiment with Setswana-English code-switching support
- Provides dashboard for political organizations, researchers, and journalists
- Tracks political discourse trends and public opinion

## Architecture

```
botswana-political-sentiment/
├── backend/
│   ├── app.py                          # Main Production Flask API
│   ├── simple_app.py                   # Simple Testing API (keep for development)
│   ├── config.py                       # Configuration management
│   ├── models.py                       # Database schemas
│   ├── lexicon_manager.py              # Setswana lexicon management
│   ├── training_data_collector.py      # Training data collection
│   ├── model_trainer.py                # Model training pipeline
│   ├── sentiment_analyzer.py           # Enhanced sentiment analysis
│   ├── data_collector.py               # Social media data collection
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── sentiment.py                # Sentiment analysis endpoints
│   │   ├── dashboard.py                # Dashboard data endpoints
│   │   ├── lexicon.py                  # Lexicon management endpoints
│   │   ├── training.py                 # Training endpoints
│   │   └── admin.py                    # Admin endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sentiment_service.py        # Sentiment analysis business logic
│   │   ├── data_collection_service.py  # Data collection service
│   │   └── trend_analysis_service.py   # Political trend analysis
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py                  # Utility functions
│       └── validators.py               # Input validation
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.tsx       # Main dashboard container
│   │   │   │   ├── OverviewCards.tsx   # Statistics overview cards
│   │   │   │   ├── SentimentChart.tsx  # Real-time sentiment charts
│   │   │   │   ├── TrendChart.tsx      # Political trend visualization
│   │   │   │   ├── PostsTable.tsx      # Social media posts table
│   │   │   │   └── FilterPanel.tsx     # Search and filter controls
│   │   │   ├── Analysis/
│   │   │   │   ├── SentimentAnalyzer.tsx # Text analysis interface
│   │   │   │   └── ResultDisplay.tsx   # Analysis results display
│   │   │   ├── Management/
│   │   │   │   ├── LexiconManager.tsx  # Lexicon management interface
│   │   │   │   ├── TrainingManager.tsx # Model training interface
│   │   │   │   └── AdminPanel.tsx      # Admin controls
│   │   │   ├── Common/
│   │   │   │   ├── Header.tsx          # App header with navigation
│   │   │   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   │   │   ├── LoadingSpinner.tsx  # Loading component
│   │   │   │   └── ErrorBoundary.tsx   # Error handling
│   │   │   └── Charts/
│   │   │       ├── LineChart.tsx       # Reusable line chart
│   │   │       ├── BarChart.tsx        # Reusable bar chart
│   │   │       └── PieChart.tsx        # Reusable pie chart
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx       # Dashboard page
│   │   │   ├── AnalysisPage.tsx        # Analysis page
│   │   │   ├── ManagementPage.tsx      # Management page
│   │   │   └── SettingsPage.tsx        # Settings page
│   │   ├── services/
│   │   │   ├── api.ts                  # API service layer
│   │   │   ├── websocket.ts            # Real-time updates
│   │   │   └── storage.ts              # Local storage utilities
│   │   ├── hooks/
│   │   │   ├── useApi.ts               # API hooks
│   │   │   ├── useWebSocket.ts         # WebSocket hooks
│   │   │   └── useLocalStorage.ts      # Storage hooks
│   │   ├── types/
│   │   │   ├── index.ts                # Common type definitions
│   │   │   ├── api.ts                  # API response types
│   │   │   └── dashboard.ts            # Dashboard-specific types
│   │   ├── styles/
│   │   │   ├── globals.css             # Global styles
│   │   │   ├── components.css          # Component styles
│   │   │   └── dashboard.css           # Dashboard-specific styles
│   │   └── utils/
│   │       ├── formatters.ts           # Data formatting utilities
│   │       ├── constants.ts            # App constants
│   │       └── helpers.ts              # Helper functions
├── data/
│   ├── training_data/
│   │   ├── setswana_sentiment_dataset.csv
│   │   └── political_keywords.json
│   └── models/
│       └── sentiment_model_setswana/
└── scripts/
    ├── train_model.py                  # Model training script
    ├── collect_data.py                 # Data collection script
    └── setup_database.py               # Database initialization
```

## Key Features

### 1. Real-time Data Collection
- Twitter API v2 integration for political hashtags
- Facebook Graph API for public political pages
- Automated data collection with configurable keywords
- Data cleaning and preprocessing for Setswana-English text

### 2. Advanced Sentiment Analysis
- Custom XLM-RoBERTa model trained on Setswana-English code-switching data
- Political context-aware sentiment classification
- Confidence scoring and uncertainty handling
- Support for political terminology and slang

### 3. Interactive Dashboard
- Real-time sentiment trends visualization
- Political party/candidate sentiment comparison
- Geographic sentiment mapping (if location data available)
- Keyword trend analysis
- Export capabilities for researchers

### 4. Target Users
- **Political Organizations**: Monitor public opinion on policies/candidates
- **Researchers**: Academic research on political discourse
- **Journalists**: Story leads and public sentiment verification
- **Government**: Public opinion monitoring (transparency)

## Technology Stack
- **Backend**: Flask, SQLAlchemy, Celery (background tasks)
- **Frontend**: React, TypeScript, Chart.js/D3.js
- **Database**: PostgreSQL
- **ML**: Transformers, PyTorch, scikit-learn
- **APIs**: Twitter API v2, Facebook Graph API
- **Deployment**: Docker, AWS/Azure