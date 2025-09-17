from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Load multilingual sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis")

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Run sentiment analysis
    analysis = sentiment_pipeline(text)
    label = analysis[0]['label'].lower()
    score = float(analysis[0]['score'])

    # Simple language detection (optional, can be improved)
    if any(ord(char) > 127 for char in text):
        language = "Setswana-English"
    else:
        language = "English"

    result = {
        "sentiment": label,
        "confidence": score,
        "language": language
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)