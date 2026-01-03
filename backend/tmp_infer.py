#!/usr/bin/env python3
import os, sys, json

# Point the analyzer to the baseline model saved under backend/models
os.environ['BASELINE_MODEL_PATH'] = 'backend/models/baseline_sentiment_model.joblib'

# Ensure backend modules import correctly
sys.path.insert(0, 'backend')

from sentiment_analyzer import analyzer

samples = [
    "I love the new policies, they are helpful.",
    "I hate how the government handled this."
]

for s in samples:
    result = analyzer.analyze_sentiment(s)
    print(json.dumps(result, indent=2))
