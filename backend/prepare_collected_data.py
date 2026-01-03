#!/usr/bin/env python3
"""Prepare collected CSV training data into analyzed JSON files for the frontend.

Reads CSV files from `backend/data/training_data/`, cleans text, runs the global
`analyzer` to get sentiment analysis, and writes two files expected by the simple
app frontend:

- `data/collected_posts.json` : raw collected posts with metadata
- `data/analyzed_posts.json`  : posts annotated with `sentiment_analysis` (used by dashboards)

This script is idempotent and can be re-run after adding new CSVs.
"""
import csv
import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, 'backend')
from sentiment_analyzer import analyzer


DATA_DIR = Path('data')
TRAINING_DIR = Path('backend/data/training_data')


def find_csv_files():
    if not TRAINING_DIR.exists():
        return []
    return sorted([p for p in TRAINING_DIR.iterdir() if p.suffix.lower() == '.csv'])


def read_csv_texts(path: Path):
    rows = []
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        # If no header or missing 'text', fall back to first column
        for r in reader:
            if 'text' in r and r['text'].strip():
                rows.append(r['text'].strip())
            else:
                # try first non-empty value
                for v in r.values():
                    if v and v.strip():
                        rows.append(v.strip())
                        break
    return rows


def clean_text(s: str) -> str:
    return ' '.join(s.split()).strip()


def prepare():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = find_csv_files()
    if not csv_files:
        print('No CSV files found in', TRAINING_DIR)
        return

    all_texts = []
    for p in csv_files:
        print('Reading', p)
        texts = read_csv_texts(p)
        all_texts.extend(texts)

    print(f'Found {len(all_texts)} texts across {len(csv_files)} CSV files')

    posts = []
    analyzed = []
    now = datetime.now().isoformat()

    for i, t in enumerate(all_texts, start=1):
        text = clean_text(t)
        post = {
            'id': i,
            'text': text,
            'platform': 'collected',
            'created_at': now,
            'collected_at': now,
            'likes': 0,
            'shares': 0,
            'comments': 0,
            'raw_data': ''
        }

        # Analyze sentiment using analyzer (may return None)
        try:
            analysis = analyzer.analyze_sentiment(text)
            if analysis is None:
                analysis = {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'detected_language': 'English',
                    'code_switching_detected': False
                }
        except Exception as e:
            print('Analyzer error for text:', e)
            analysis = {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'detected_language': 'English',
                'code_switching_detected': False
            }

        post['sentiment_analysis'] = analysis
        posts.append(post)
        analyzed.append(post)

    # Save raw collected posts and analyzed posts
    collected_path = DATA_DIR / 'collected_posts.json'
    analyzed_path = DATA_DIR / 'analyzed_posts.json'

    with collected_path.open('w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    with analyzed_path.open('w', encoding='utf-8') as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    print('Wrote', collected_path, 'and', analyzed_path)
    # Print brief stats
    counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for p in analyzed:
        s = p.get('sentiment_analysis', {}).get('sentiment', 'neutral')
        counts[s] = counts.get(s, 0) + 1

    print('Distribution:', counts)


if __name__ == '__main__':
    prepare()
