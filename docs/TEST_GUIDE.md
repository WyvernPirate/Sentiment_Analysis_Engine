# 🧪 Quick Test Guide - Botswana Political Sentiment Analysis

## 🎯 Goal
Test the basic Setswana sentiment analysis functionality before adding complex ML models and social media APIs.

## 🚀 Quick Start (2 minutes)

### Step 1: Start the Backend
```bash
cd backend
python simple_app.py
```

Or use the interactive startup script:
```bash
cd backend
python start.py
# Choose option 1 for testing mode
```

This will:
- ✅ Start the enhanced sentiment analysis server
- 📊 Provide mock dashboard data for frontend testing
- 🔧 Enable lexicon management and training features
- 🧪 Show all available test endpoints

### Step 2: Start the Frontend (New Terminal)
```bash
cd frontend
npm start
```

The React app will open at `http://localhost:3000` with three tabs:
- **📊 Dashboard** - Political sentiment overview (mock data)
- **🔍 Analyzer** - Text sentiment analysis
- **🔧 Management** - Lexicon and training management

## 🧪 What to Test

### 1. **Pure English Sentiment (Enhanced)**
Try: `"I love the new policy changes"`
- Should use: Transformers model (if installed) or enhanced keyword analysis
- Should detect: English language, positive sentiment
- Should show: High confidence with proper English analysis

### 2. **Pure English Negative**
Try: `"This government is terrible and disappointing"`
- Should use: Advanced English sentiment analysis
- Should detect: English language, negative sentiment
- Should show: Detailed English analysis breakdown

### 3. **Pure Setswana Positive**
Try: `"Ke rata mmuso o, o dira sentle thata"`
- Should use: Setswana lexicon analysis
- Should detect: Setswana language, positive sentiment
- Should find: "rata" (love), "sentle" (good/beautiful)

### 4. **Pure Setswana Negative**
Try: `"Mmuso o o botlhoko, ga o dire sepe"`
- Should use: Setswana lexicon analysis
- Should detect: Setswana language, negative sentiment
- Should find: "botlhoko" (painful/bad)

### 5. **Code-Switching Hybrid Analysis**
Try: `"The government is doing botlhoko work"`
- Should use: Hybrid analysis combining both models
- Should detect: Code-switching, negative sentiment
- Should show: Both English and Setswana analysis results

### 6. **Complex Code-Switching**
Try: `"Masisi is doing sentle work for batho"`
- Should use: Hybrid analysis
- Should detect: Code-switching, positive sentiment
- Should find: Political entity "Masisi", Setswana words "sentle", "batho"

### 7. **Political Context Detection**
Try: `"BDP le UDC ba lwantshana, but I think it's good for democracy"`
- Should detect: Political entities "BDP" and "UDC"
- Should show: Complex hybrid analysis
- Should handle: Mixed sentiment with political context

## 📊 Expected Results

Each analysis now returns:
- **Sentiment**: positive/negative/neutral with confidence score
- **Language**: English/Setswana/Setswana-English  
- **Code-switching**: True/False
- **Model Strategy**: english_primary, setswana_primary, hybrid_blend, etc.
- **Analysis Breakdown**: Shows both English and Setswana analysis results
- **Setswana words found**: List with meanings (e.g., "sentle (good/beautiful)")
- **Political context**: Entities (parties, leaders) and keywords
- **Combination Logic**: Explains how the final result was determined

### Model Strategies You'll See:
- **english_primary**: Mainly English with Setswana word boost
- **setswana_primary**: Mainly Setswana lexicon analysis  
- **hybrid_blend**: Balanced combination of both models
- **english_dominant**: Code-switching but English analysis used
- **setswana_fallback_english**: Setswana detected but fell back to English

## 🔧 API Endpoints to Test

1. **Health Check**: `GET http://localhost:5000/api/health`
2. **Sentiment Analysis**: `POST http://localhost:5000/api/sentiment`
3. **View Lexicon**: `GET http://localhost:5000/api/lexicon`
4. **Test Examples**: `GET http://localhost:5000/api/test-examples`

## 🎯 What This Tests

✅ **Hybrid Sentiment Analysis** - English transformers + Setswana lexicon
✅ **Dynamic Lexicon Management** - Add/search/suggest new words
✅ **Training Data Collection** - User feedback and corrections
✅ **Code-switching Recognition** - Critical for real-world usage  
✅ **Political Entity Extraction** - Identifies parties, leaders, locations
✅ **Model Retraining** - Incremental improvement with user data
✅ **Dashboard Interface** - Political sentiment visualization (mock data)
✅ **Complete Frontend** - Dashboard + Analyzer + Management tabs

## 🔄 Next Steps After Testing

Now that you have the enhanced system:

1. **Expand Setswana Lexicon**: Use the Lexicon Manager to add more words
2. **Collect User Feedback**: Test with real users and collect corrections
3. **Train Custom Model**: Use the training endpoints to create XLM-RoBERTa model
4. **Social Media Integration**: Add Twitter/Facebook data collection
5. **Production Deployment**: Scale with proper database and monitoring

## 🎓 Using the Enhanced Features

### **Lexicon Manager Tab**
- **Search existing words** in the Setswana lexicon
- **Add new words directly** to categories (positive, negative, political)
- **Suggest words for review** if you're not sure about categorization
- **View statistics** about lexicon size and recent additions
- **Quick retrain** to update the system with new words

### **Training Data Collection**
- System automatically collects user feedback on predictions
- Disagreements are flagged for model improvement
- Export training datasets for external model training
- View performance analytics and improvement suggestions

### **Model Training Endpoints**
- `/api/training/prepare-dataset` - Prepare comprehensive training data
- `/api/training/train-model` - Full XLM-RoBERTa model training
- `/api/training/quick-retrain` - Fast lexicon and data updates

## 🐛 Troubleshooting

**Backend won't start?**
- Make sure you're in the `backend` directory
- Install Flask: `pip install flask flask-cors`
- Check port 5000 isn't in use

**Frontend won't connect?**
- Make sure backend is running on port 5000
- Check browser console for CORS errors
- Try `http://localhost:5000/api/health` directly

**No Setswana detection?**
- The lexicon is basic - we'll expand it based on your needs
- Try the exact test examples provided
- Check the `/api/lexicon` endpoint to see available words

## 📈 Success Metrics

You'll know it's working when:
- ✅ Health endpoint returns status "healthy"
- ✅ Setswana text is detected correctly
- ✅ Code-switching examples work
- ✅ Political entities are recognized
- ✅ Frontend shows detailed analysis results

## 💡 Tips for Testing

1. **Start Simple**: Use the provided examples first
2. **Check Language Detection**: Focus on Setswana word recognition
3. **Test Edge Cases**: Very short text, mixed languages, typos
4. **Political Context**: Try different party names and leaders
5. **Real Content**: Test with actual social media posts (in Setswana/English)

---

**Ready to test?** Run `python test_setup.py` in the backend directory! 🚀