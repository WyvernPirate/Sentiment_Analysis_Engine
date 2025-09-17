# Backend (Flask API)

## Overview
This is a Flask REST API that receives text and returns sentiment analysis results using a Hugging Face Transformers model.

## Features
- `/api/sentiment` POST endpoint
- CORS enabled for frontend communication
- Integrates with a sentiment analysis model

## Setup
1. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```
   python app.py
   ```
4. The API will be available at `http://localhost:5000/api/sentiment`

## API Usage
- **POST** `/api/sentiment`
- **Body:** `{ "text": "Your text here" }`
- **Response:**  
  ```json
  {
    "sentiment": "positive",
    "confidence": 0.98,
    "language": "English"
  }
  ```

---
# Sentiment Model

## Overview
The sentiment analysis model is powered by Hugging Face Transformers.

## Model Details
- Default: DistilBERT (English sentiment analysis)
- For multilingual support: Use `cardiffnlp/twitter-xlm-roberta-base-sentiment`
- Predicts sentiment (`positive`, `neutral`, `negative`) and confidence score

## How It Works
- The model is loaded in the backend using the `pipeline` API.
- Input text is tokenized and passed to the model for inference.
- The model returns the most likely sentiment and a confidence score.

## Customization
- For Setswana/code-switching support, fine-tune a multilingual model with custom data.
- Replace the model name in the backend code