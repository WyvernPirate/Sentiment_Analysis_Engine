# 🕷️ Web Scraping Guide - No Facebook API Required

## 🎯 Overview

This guide shows how to collect Botswana political content using web scraping and public APIs, **without requiring Facebook API access**. We focus on accessible, public sources that provide rich political discourse data.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install requests beautifulsoup4 lxml
```

### 2. Test Web Scraping
```bash
# Test the scraping functionality
python test_web_scraping.py

# Start the backend with web scraping support
python simple_app.py
```

### 3. Use the API
```bash
# Trigger data collection
curl -X POST http://localhost:5000/api/collect/web-scraping

# Check available sources
curl http://localhost:5000/api/collect/status
```

## 📊 Available Data Sources

### ✅ **Reddit r/Botswana** (Active)
- **API**: Public Reddit JSON API
- **Authentication**: None required
- **Data**: Political discussions and posts
- **Language**: English, Setswana, Code-switching
- **Example**: Real posts about BDP, UDC, elections, government policies

```python
# Endpoint: https://www.reddit.com/r/Botswana.json
# Filters for political keywords automatically
```

### ✅ **Mock Social Media Data** (Active)
- **Purpose**: Realistic testing data
- **Content**: Sample Botswana political posts
- **Languages**: English and Setswana with code-switching
- **Examples**:
  - "BDP's new economic policy looks promising #BDP2024"
  - "Ke dumela gore UDC e tla fetola Botswana #UDC2024"
  - "Mmuso o tshwanetse go thusa babereki #Jobs"

### ✅ **News Headlines** (Active)
- **Sources**: Botswana news aggregation
- **Content**: Political news and announcements
- **Examples**:
  - "President Masisi announces new economic recovery plan"
  - "UDC leader Boko criticizes unemployment handling"
  - "Parliament debates new mining legislation"

### 🔧 **Web Scraping** (Available)
- **Sources**: Public Botswana news websites
- **Targets**: Mmegi Online, The Voice, Botswana Guardian
- **Method**: BeautifulSoup HTML parsing
- **Content**: Articles, opinion pieces, political coverage

## 🎯 Target Content

### Hashtags Monitored
```
#BotswanaPolitics    #BDP2024           #UDC2024
#Masisi              #Boko              #BotswanaElections  
#BWPolitics          #BotswanaGovernment #BotswanaParliament
```

### Keywords Tracked
```
English: Botswana politics, BDP, UDC, BCP, AP, Masisi, Boko, election
Setswana: mmuso, polotiki, kgethololo, palamente, setšhaba, batho
```

### Political Entities
```
Parties: BDP, UDC, BCP, AP
Leaders: Masisi, Boko, Saleshando
Locations: Gaborone, Francistown, Maun
```

## 🔧 Implementation Details

### Reddit Collection
```python
# Public API - no authentication
url = "https://www.reddit.com/r/Botswana.json?limit=25"
response = requests.get(url)
data = response.json()

# Filter for political content
for post in data['data']['children']:
    if any(keyword in post['data']['title'].lower() 
           for keyword in political_keywords):
        # Process political post
```

### News Website Scraping
```python
# Target Botswana news sites
sources = [
    'https://www.mmegi.bw',
    'https://www.thevoicebw.com', 
    'https://www.botswanaguardian.co.bw'
]

# Use BeautifulSoup for parsing
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.select('article, .news-item')
```

### Mock Data Generation
```python
# Realistic Botswana political content
sample_posts = [
    "BDP's new economic policy looks promising for Botswana's future #BDP2024",
    "Ke dumela gore UDC e tla fetola Botswana #UDC2024 #Change",
    "Mmuso o tshwanetse go thusa babereki ba ba latlhegileng #Jobs"
]
```

## 📡 API Endpoints

### Data Collection
```bash
# Trigger web scraping collection
POST /api/collect/web-scraping

Response:
{
  "message": "Web scraping data collection completed",
  "success": true,
  "total_collected": 45,
  "sources": {
    "reddit": 8,
    "mock_social_media": 16,
    "news": 10
  }
}
```

### Collection Status
```bash
# Check available data sources
GET /api/collect/status

Response:
{
  "available_sources": {
    "reddit_r_botswana": {
      "status": "active",
      "description": "Public Reddit API - no authentication required"
    }
  },
  "facebook_api_required": false,
  "twitter_api_required": false,
  "target_hashtags": ["#BotswanaPolitics", "#BDP2024", ...]
}
```

## 🎯 Benefits of This Approach

### ✅ **No API Keys Required**
- No Facebook API application process
- No Twitter API approval waiting
- No rate limit concerns with major platforms
- Immediate access to data sources

### ✅ **Botswana-Focused**
- Targets specific Botswana political content
- Includes local news sources
- Supports Setswana language content
- Focuses on relevant political entities

### ✅ **Scalable and Flexible**
- Easy to add new data sources
- Can expand to more news websites
- Supports different content types
- Adaptable to changing requirements

### ✅ **Legal and Ethical**
- Uses public APIs and websites
- Respects robots.txt and rate limits
- Focuses on publicly available content
- No private data access

## 🔄 Data Processing Pipeline

### 1. Collection
```
Web Sources → Raw Data → JSON Storage
```

### 2. Processing
```
Raw Text → Language Detection → Sentiment Analysis → Database
```

### 3. Analysis
```
Stored Data → Trend Analysis → Dashboard Visualization
```

## 📈 Scaling Options

### Immediate (No API Keys)
- ✅ Reddit public API
- ✅ News website scraping
- ✅ Public forum monitoring
- ✅ Mock data for testing

### Future Expansion (Optional APIs)
- 🔧 Twitter API v2 (free tier available)
- 🔧 YouTube Data API (for video comments)
- 🔧 News API for broader coverage
- 🔧 RSS feeds from Botswana media

## 🛡️ Best Practices

### Rate Limiting
```python
import time
time.sleep(2)  # Pause between requests
```

### Error Handling
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"Request failed: {e}")
```

### Content Filtering
```python
# Filter for political content
is_political = any(
    keyword.lower() in text.lower() 
    for keyword in political_keywords
)
```

### Data Quality
```python
# Validate content length and relevance
if len(content) > 50 and is_political:
    # Process the content
```

## 🧪 Testing

### Test Individual Components
```bash
# Test Reddit collection
python -c "from simple_data_collector import SimpleDataCollector; print(SimpleDataCollector().collect_reddit_botswana_politics())"

# Test mock data generation  
python -c "from simple_data_collector import SimpleDataCollector; print(SimpleDataCollector().generate_mock_social_media_data())"

# Test full collection
python test_web_scraping.py
```

### Test API Integration
```bash
# Start backend
python simple_app.py

# Test collection endpoint
curl -X POST http://localhost:5000/api/collect/web-scraping

# Test status endpoint
curl http://localhost:5000/api/collect/status
```

## 🔮 Future Enhancements

### Additional Sources
- **Botswana Government Websites**: Official announcements and press releases
- **University Forums**: Academic discussions about Botswana politics
- **Local Blogs**: Political commentary and analysis
- **Community Forums**: Grassroots political discussions

### Advanced Features
- **Real-time Monitoring**: Continuous data collection
- **Sentiment Tracking**: Historical sentiment analysis
- **Trend Detection**: Emerging political topics
- **Language Analysis**: Code-switching patterns

### Integration Options
- **Database Storage**: PostgreSQL for production
- **Background Tasks**: Celery for scheduled collection
- **Caching**: Redis for performance optimization
- **Monitoring**: Health checks and alerting

---

**🎯 This approach gives you immediate access to Botswana political content without waiting for Facebook API approval!**