#!/usr/bin/env python3
"""Collect posts from public sources (Reddit + seed news pages) and save a CSV for training.

Saves CSV to `backend/data/training_data/botswana_collection_<timestamp>.csv` with columns:
  text, source, platform, created_at, url, auto_label, auto_confidence

This is a lightweight collector for initial dataset building (no API keys required).
"""
import argparse
import csv
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup

# Import analyzer (global instance) so we can auto-label
import sys
sys.path.insert(0, 'backend')
from sentiment_analyzer import analyzer


def clean_text(s: str) -> str:
    """Normalize and clean a text string for training/visualization.

    - Remove URLs
    - Remove extra whitespace
    - Trim leading/trailing punctuation
    - Replace repeated punctuation/characters
    """
    import re

    if not s:
        return ''

    # Normalize whitespace
    text = ' '.join(s.split())

    # Remove URLs
    text = re.sub(r'http\S+|https\S+|www\.\S+', '', text)

    # Remove mentions (@user)
    text = re.sub(r'@\w+', '', text)

    # Replace multiple punctuation with a single instance
    text = re.sub(r'([!?.,]){2,}', r"\1", text)

    # Trim
    text = text.strip(' \n\t\r"')

    return text


def hash_text(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def fetch_reddit(subreddit: str = 'Botswana', size: int = 100, keywords: List[str] = None) -> List[dict]:
    """Fetch recent submissions from Pushshift for a subreddit and optional keywords.

    Uses HTTPS and a browser-like User-Agent and retries a few times on transient errors.
    """
    results = []
    base = 'https://api.pushshift.io/reddit/search/submission/'
    params = {'subreddit': subreddit, 'size': size, 'sort': 'desc'}
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; dataset-collector/1.0; +https://example.com)'}

    for attempt in range(3):
        try:
            r = requests.get(base, params=params, headers=headers, timeout=20)
            r.raise_for_status()
            data = r.json().get('data', [])
            for item in data:
                title = item.get('title') or ''
                selftext = item.get('selftext') or ''
                text = f"{title} \n {selftext}".strip()
                if not text:
                    continue
                if keywords:
                    lowered = text.lower()
                    if not any(k.lower() in lowered for k in keywords):
                        continue
                results.append({
                    'text': clean_text(text),
                    'source': subreddit,
                    'platform': 'reddit',
                    'created_at': datetime.fromtimestamp(item.get('created_utc', time.time())).isoformat(),
                    'url': item.get('full_link') or item.get('url')
                })
            break
        except Exception as e:
            print(f"Reddit fetch attempt {attempt+1} failed: {e}")
            time.sleep(2 + attempt)
            continue
    return results


def scrape_news(urls: List[str]) -> List[dict]:
    items = []
    headers = {'User-Agent': 'Mozilla/5.0 (dataset-collector)'}
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'lxml')
            # Try to extract headline + first paragraph(s)
            headline = ''
            h1 = soup.find('h1')
            if h1:
                headline = h1.get_text(separator=' ', strip=True)

            paragraphs = soup.find_all('p')
            body = ' '.join(p.get_text(separator=' ', strip=True) for p in paragraphs[:3])
            text = clean_text(f"{headline} {body}")
            if text:
                items.append({
                    'text': text,
                    'source': url,
                    'platform': 'news',
                    'created_at': datetime.now().isoformat(),
                    'url': url
                })
        except Exception as e:
            print(f"News scrape failed for {url}: {e}")
    return items


def auto_label_items(items: List[dict]) -> List[dict]:
    labeled = []
    for it in items:
        try:
            result = analyzer.analyze_sentiment(it['text'])
            if not result:
                it['auto_label'] = ''
                it['auto_confidence'] = ''
            else:
                it['auto_label'] = result.get('sentiment', '')
                it['auto_confidence'] = result.get('confidence', 0.0)
        except Exception as e:
            it['auto_label'] = ''
            it['auto_confidence'] = ''
        labeled.append(it)
    return labeled


def save_csv(items: List[dict], out_dir: str = 'backend/data/training_data') -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f'botswana_collection_{ts}.csv'
    path = os.path.join(out_dir, fname)
    fields = ['text', 'source', 'platform', 'created_at', 'url', 'auto_label', 'auto_confidence']
    seen = set()
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for it in items:
            text = it.get('text', '')
            h = hash_text(text)
            if h in seen:
                continue
            seen.add(h)
            writer.writerow({k: it.get(k, '') for k in fields})
    return path


def collect_main(dry_run: bool = True, reddit_limit: int = 200, keywords: List[str] = None):
    print(f"Collector: dry_run={dry_run}, reddit_limit={reddit_limit}")

    collected = []
    # Fetch Reddit posts
    reddit_items = fetch_reddit(size=reddit_limit, keywords=keywords)
    print(f"Fetched {len(reddit_items)} reddit items")
    collected.extend(reddit_items)

    # Scrape seed news pages
    seed_news = [
        'https://www.mmegi.bw',
        'https://www.sundaystandard.info',
        'https://allafrica.com',
    ]
    news_items = scrape_news(seed_news)
    print(f"Scraped {len(news_items)} news items")
    collected.extend(news_items)

    if not collected:
        print("No items collected")
        return None

    # Auto-label using analyzer
    labeled = auto_label_items(collected)

    if dry_run:
        # Report a short summary
        labels = [it.get('auto_label', '') for it in labeled if it.get('auto_label')]
        from collections import Counter
        print("Label distribution (dry run):", Counter(labels))
        return {'collected': len(labeled), 'label_distribution': dict(Counter(labels))}

    out_path = save_csv(labeled)
    print(f"Saved collected dataset to: {out_path}")
    # Summarize labels
    from collections import Counter
    labels = [it.get('auto_label', '') for it in labeled if it.get('auto_label')]
    return {'collected': len(labeled), 'label_distribution': dict(Counter(labels)), 'filename': out_path}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--reddit-limit', type=int, default=200)
    parser.add_argument('--keyword', action='append', help='Keyword to filter reddit posts (can repeat)')
    args = parser.parse_args()

    result = collect_main(dry_run=args.dry_run, reddit_limit=args.reddit_limit, keywords=args.keyword)
    print(json.dumps(result or {}, indent=2))


if __name__ == '__main__':
    main()
