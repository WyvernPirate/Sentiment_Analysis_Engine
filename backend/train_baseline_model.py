#!/usr/bin/env python3
"""Train a lightweight baseline sentiment model (TF-IDF + LogisticRegression).

This is intended as a fast, dependency-light alternative to transformer-based
models so the project has a working custom model for deliverables.
"""
import os
import json
import argparse
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

from config import Config


def load_dataset(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    df = pd.read_csv(csv_path)
    # Expect columns: text,label with label 0/1/2
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError('CSV must contain text and label columns')
    return df


def train_baseline(csv_path: str, output_path: str, test_size: float = 0.2, random_state: int = 42):
    df = load_dataset(csv_path)
    X = df['text'].astype(str).tolist()
    y = df['label'].astype(int).tolist()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=20000, ngram_range=(1,2))),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    print(f"Training baseline model on {len(X_train)} examples...")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Validation accuracy: {acc:.4f}")
    print("Classification report:\n", classification_report(y_test, preds))

    # Ensure output directory exists
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, output_path)
    print(f"Saved baseline model to: {output_path}")
    return output_path, acc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default=os.path.join(os.path.dirname(__file__), 'setswana_sentiment_dataset.csv'))
    parser.add_argument('--output', default=Config.BASELINE_MODEL_PATH)
    args = parser.parse_args()

    try:
        train_baseline(args.dataset, args.output)
    except Exception as e:
        print(f"Error training baseline model: {e}")
        raise


if __name__ == '__main__':
    main()
