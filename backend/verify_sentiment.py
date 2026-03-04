from sentiment_analyzer import analyzer
import json

test_cases = [
    "I love the new policy changes",
    "This government is terrible and disappointing",
    "The meeting was held in Gaborone yesterday.",
    "BDP is doing a great job",
    "UDC is not happy with the results"
]

print("Starting direct sentiment analysis tests...")
for text in test_cases:
    result = analyzer.analyze_sentiment(text)
    if result:
        print(f"Text: '{text}'")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Model: {result['model_used']}")
        print("-" * 30)
    else:
        print(f"FAILED for: '{text}'")
