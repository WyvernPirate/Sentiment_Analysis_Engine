#!/usr/bin/env python3
"""
Compatibility data collector.

Provides `collect_simple_data()` for legacy modules that still import
`simple_data_collector` after cleanup/refactoring.
"""

from datetime import datetime
from typing import Dict, List

from web_scraper import web_scraper


def _flatten_collected_data(collected: Dict[str, List[Dict]]) -> List[Dict]:
    """Flatten source buckets into a single list of post dictionaries."""
    flattened: List[Dict] = []

    for source, items in (collected or {}).items():
        for item in items or []:
            post = dict(item)
            post.setdefault('source', source)
            post.setdefault('text', '')
            post.setdefault('platform', 'unknown')
            post.setdefault('created_at', datetime.utcnow().isoformat())
            flattened.append(post)

    return flattened


def collect_simple_data(max_per_source: int = 10) -> Dict:
    """Collect lightweight data using existing web scraper infrastructure.

    Returns:
        {
            "success": bool,
            "data": list,
            "total_collected": int,
            "timestamp": str,
            "error": Optional[str]
        }
    """
    try:
        collected = web_scraper.collect_all_data(max_per_source=max_per_source)
        flattened = _flatten_collected_data(collected)
        source_counts = {source: len(items or []) for source, items in (collected or {}).items()}

        return {
            "success": True,
            "data": flattened,
            "sources": source_counts,
            "total_collected": len(flattened),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        return {
            "success": False,
            "data": [],
            "total_collected": 0,
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
