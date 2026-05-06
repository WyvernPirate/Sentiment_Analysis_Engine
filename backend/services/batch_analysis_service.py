"""
Batch Analysis Service
Processes a collected batch of social records through the sentiment pipeline,
producing per-row analysis results and aggregate statistics.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from services.sentiment_service import sentiment_service
from services.lexicon_service import lexicon_service
from services.political_entity_service import political_entity_service
from services.raw_data_manager import raw_data_manager


class BatchAnalysisService:

    RESULTS_DIR = os.path.join('data', 'analysis_results')

    def __init__(self):
        os.makedirs(self.RESULTS_DIR, exist_ok=True)

    def analyze_batch(self, collection_id: str) -> Dict:
        """
        Run sentiment analysis on every record in a collection.

        1. Load raw records for the collection
        2. Refresh lexicon for up-to-date political word matching
        3. Analyze each row: sentiment, confidence, trigger words, political words, entities
        4. Compute aggregate statistics
        5. Persist results to disk
        6. Return full result set

        Returns dict with: job_id, filename, analyzed_at, rows[], aggregate{}
        """
        # Look up the collection
        entry = raw_data_manager.get_collection(collection_id)
        if not entry:
            raise ValueError(f'Collection not found: {collection_id}')

        raw_file = entry.get('raw_file', '')
        records = raw_data_manager.load_raw_records(raw_file)
        if not records:
            raise ValueError(f'No records found in collection: {collection_id}')

        # Refresh lexicon for political word matching
        lexicon_service.refresh_lexicon()
        lexicon = lexicon_service.legacy_lexicon

        # Pre-collect all texts for batch inference
        valid_records = []
        texts_to_analyze = []
        for record in records:
            text = (record.get('text_raw') or record.get('text_clean') or '').strip()
            if text:
                valid_records.append(record)
                texts_to_analyze.append(text)

        if not texts_to_analyze:
            raise ValueError(f'No valid text records found in collection: {collection_id}')

        # Run batch sentiment analysis (MUCH faster)
        batch_results = sentiment_service.analyze_english_sentiment_batch(texts_to_analyze)

        # Process results
        analyzed_rows = []
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        total_confidence = 0.0
        trigger_word_counts: Dict[str, Dict] = {}
        entity_counts: Dict[str, int] = {}

        for idx, (record, (sentiment, confidence, details)) in enumerate(zip(valid_records, batch_results)):
            text = texts_to_analyze[idx]
            
            # Match political words from lexicon
            matched_political = sentiment_service.match_political_words(text, lexicon)

            # Extract political entities from database
            political_entities = political_entity_service.extract_entities(text)

            # Extract trigger words - Use basic mode for batch to avoid LOO performance hit
            exclude_names = [e.get('entity', '') for e in political_entities]
            trigger_words = sentiment_service.extract_basic_trigger_words(
                text, 
                exclude_words=exclude_names
            )

            # Build analyzed row
            row_result = {
                'row_index': idx,
                'text': text,
                'sentiment': sentiment,
                'confidence': round(confidence, 3),
                'model_used': details.get('model', 'unknown'),
                'trigger_words': trigger_words,
                'political_words': [
                    {'term': w['term'], 'meaning': w['meaning']}
                    for w in matched_political
                ],
                'entities': [
                    {'entity': e.get('entity', ''), 'type': e.get('type', '')}
                    for e in political_entities
                ],
                'meta': {
                    'author': record.get('author_username', ''),
                    'date': record.get('created_at_utc', ''),
                    'source': record.get('source', ''),
                    'url': record.get('post_url', ''),
                },
            }
            analyzed_rows.append(row_result)

            # Update aggregates
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_confidence += confidence

            # Track trigger words
            for word_type in ('positive', 'negative'):
                for word in trigger_words.get(word_type, []):
                    key = word.lower()
                    if key not in trigger_word_counts:
                        trigger_word_counts[key] = {'count': 0, 'type': word_type}
                    trigger_word_counts[key]['count'] += 1

            # Track entities
            for ent in political_entities:
                ent_name = ent.get('entity', '')
                if ent_name:
                    entity_counts[ent_name] = entity_counts.get(ent_name, 0) + 1

        total_rows = len(analyzed_rows)
        avg_confidence = round(total_confidence / total_rows, 3) if total_rows > 0 else 0

        # Sort trigger words and entities by count
        top_trigger_words = sorted(
            [{'word': k, 'count': v['count'], 'type': v['type']} for k, v in trigger_word_counts.items()],
            key=lambda x: x['count'],
            reverse=True,
        )[:20]

        top_entities = sorted(
            [{'entity': k, 'count': v} for k, v in entity_counts.items()],
            key=lambda x: x['count'],
            reverse=True,
        )[:20]

        # Build aggregate
        aggregate = {
            'total_rows': total_rows,
            'sentiment_distribution': sentiment_counts,
            'avg_confidence': avg_confidence,
            'top_trigger_words': top_trigger_words,
            'top_entities': top_entities,
            'model_used': analyzed_rows[0]['model_used'] if analyzed_rows else 'unknown',
        }

        # Build result
        job_id = f'analysis-{collection_id}-{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}'
        result = {
            'job_id': job_id,
            'collection_id': collection_id,
            'filename': os.path.basename(raw_file),
            'analyzed_at': datetime.utcnow().isoformat(),
            'rows': analyzed_rows,
            'aggregate': aggregate,
        }

        # Persist to disk
        result_path = os.path.join(self.RESULTS_DIR, f'{job_id}.json')
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def list_jobs(self, limit: int = 20) -> List[Dict]:
        """List past analysis jobs (metadata only, no row data)."""
        jobs = []
        if not os.path.exists(self.RESULTS_DIR):
            return jobs

        files = sorted(
            [f for f in os.listdir(self.RESULTS_DIR) if f.endswith('.json')],
            reverse=True,
        )

        for filename in files[:limit]:
            filepath = os.path.join(self.RESULTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                jobs.append({
                    'job_id': data.get('job_id', ''),
                    'collection_id': data.get('collection_id', ''),
                    'filename': data.get('filename', ''),
                    'analyzed_at': data.get('analyzed_at', ''),
                    'row_count': data.get('aggregate', {}).get('total_rows', 0),
                    'sentiment_summary': data.get('aggregate', {}).get('sentiment_distribution', {}),
                })
            except (json.JSONDecodeError, OSError):
                continue

        return jobs

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Retrieve full results for a specific analysis job."""
        result_path = os.path.join(self.RESULTS_DIR, f'{job_id}.json')
        if not os.path.exists(result_path):
            return None

        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None


batch_analysis_service = BatchAnalysisService()
