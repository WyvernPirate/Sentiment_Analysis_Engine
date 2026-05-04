"""
CSV Ingest Service
Parses uploaded CSV files and normalizes rows into the standard social record
schema used by all other providers (Bright Data, Apify, Twikit).
"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# Column name mappings for auto-detection
TEXT_COLUMN_NAMES = [
    'text', 'text_raw', 'content', 'tweet', 'message', 'post',
    'body', 'description', 'full_text', 'tweet_text', 'post_text',
]

AUTHOR_COLUMN_NAMES = [
    'author', 'author_username', 'user', 'username', 'screen_name',
    'handle', 'user_posted', 'name', 'author_name',
]

DATE_COLUMN_NAMES = [
    'date', 'created_at', 'created_at_utc', 'timestamp', 'posted_at',
    'date_posted', 'time', 'datetime',
]

URL_COLUMN_NAMES = [
    'url', 'post_url', 'link', 'tweet_url', 'source_url',
]

ID_COLUMN_NAMES = [
    'id', 'post_id', 'tweet_id', 'source_post_id', 'status_id',
]


class CsvIngestService:

    def _detect_column(self, headers: List[str], candidates: List[str]) -> Optional[str]:
        """Find the first header that matches a candidate name (case-insensitive)."""
        header_lower = {h.lower().strip(): h for h in headers}
        for candidate in candidates:
            if candidate in header_lower:
                return header_lower[candidate]
        return None

    def _detect_text_column_by_content(self, headers: List[str], rows: List[Dict]) -> Optional[str]:
        """Fallback: pick the column with the longest average string length."""
        if not rows:
            return headers[0] if headers else None

        best_col = None
        best_avg = 0

        for header in headers:
            total_len = sum(len(str(row.get(header, ''))) for row in rows[:50])
            avg_len = total_len / min(len(rows), 50)
            if avg_len > best_avg:
                best_avg = avg_len
                best_col = header

        return best_col

    def _is_url_only_csv(self, headers: List[str], rows: List[Dict]) -> bool:
        """
        Check if the CSV is a URL-only list (no substantive text column).
        A CSV is URL-only if it has a url column and no detectable text column,
        or if the only content column contains URLs.
        """
        text_col = self._detect_column(headers, TEXT_COLUMN_NAMES)
        url_col = self._detect_column(headers, URL_COLUMN_NAMES)

        # Has an explicit text column — it's a data CSV
        if text_col:
            return False

        # Has a URL column and no text column — it's URL-only
        if url_col:
            return True

        # Single-column CSV where most values look like URLs
        if len(headers) == 1 and rows:
            url_count = sum(
                1 for row in rows[:20]
                if str(row.get(headers[0], '')).strip().startswith('http')
            )
            return url_count > len(rows[:20]) * 0.7

        return False

    def detect_csv_type(self, file_content: str) -> Dict:
        """
        Analyze CSV content and return detection results.
        Returns dict with: csv_type ('data' or 'url_only'), detected columns, row count.
        """
        reader = csv.DictReader(io.StringIO(file_content))
        headers = reader.fieldnames or []
        rows = list(reader)

        is_url_only = self._is_url_only_csv(headers, rows)

        text_col = self._detect_column(headers, TEXT_COLUMN_NAMES)
        if not text_col and not is_url_only:
            text_col = self._detect_text_column_by_content(headers, rows)

        return {
            'csv_type': 'url_only' if is_url_only else 'data',
            'headers': headers,
            'row_count': len(rows),
            'detected_columns': {
                'text': text_col,
                'author': self._detect_column(headers, AUTHOR_COLUMN_NAMES),
                'date': self._detect_column(headers, DATE_COLUMN_NAMES),
                'url': self._detect_column(headers, URL_COLUMN_NAMES),
                'id': self._detect_column(headers, ID_COLUMN_NAMES),
            }
        }

    def parse_csv(self, file_content: str, filename: str = 'upload.csv') -> Dict:
        """
        Parse CSV content into normalized social records.

        Returns dict with:
        - records: list of normalized record dicts
        - count: number of records
        - query: identifier string
        - meta: detection metadata
        - provider: 'csv_upload'
        """
        reader = csv.DictReader(io.StringIO(file_content))
        headers = reader.fieldnames or []
        rows = list(reader)

        if not headers:
            raise ValueError('CSV file has no headers')
        if not rows:
            raise ValueError('CSV file has no data rows')

        # Detect columns
        text_col = self._detect_column(headers, TEXT_COLUMN_NAMES)
        author_col = self._detect_column(headers, AUTHOR_COLUMN_NAMES)
        date_col = self._detect_column(headers, DATE_COLUMN_NAMES)
        url_col = self._detect_column(headers, URL_COLUMN_NAMES)
        id_col = self._detect_column(headers, ID_COLUMN_NAMES)

        # Fallback text column detection
        if not text_col:
            text_col = self._detect_text_column_by_content(headers, rows)

        if not text_col:
            raise ValueError(
                f'Could not detect a text column. Headers found: {headers}. '
                f'Expected one of: {TEXT_COLUMN_NAMES}'
            )

        fetched_at = datetime.utcnow().isoformat()
        query_label = f'csv_upload:{filename}'
        records = []

        for idx, row in enumerate(rows):
            text_raw = str(row.get(text_col, '') or '').strip()
            if not text_raw:
                continue  # Skip empty text rows

            record = {
                'source': 'csv',
                'provider': 'csv_upload',
                'source_post_id': str(row.get(id_col, '') if id_col else idx),
                'post_url': str(row.get(url_col, '') if url_col else '').strip(),
                'author_id': '',
                'author_username': str(row.get(author_col, '') if author_col else '').strip(),
                'author_name': '',
                'created_at_utc': str(row.get(date_col, '') if date_col else '').strip(),
                'text_raw': text_raw,
                'language': '',
                'hashtags': [],
                'public_metrics': {
                    'reply_count': 0,
                    'retweet_count': 0,
                    'like_count': 0,
                    'quote_count': 0,
                },
                'query_used': query_label,
                'fetched_at_utc': fetched_at,
                'raw_item': dict(row),  # Preserve all original columns
            }

            records.append(record)

        return {
            'source': 'csv',
            'provider': 'csv_upload',
            'query': query_label,
            'count': len(records),
            'records': records,
            'meta': {
                'collection_mode': 'csv_upload',
                'filename': filename,
                'total_csv_rows': len(rows),
                'rows_with_text': len(records),
                'rows_skipped_empty': len(rows) - len(records),
                'detected_columns': {
                    'text': text_col,
                    'author': author_col,
                    'date': date_col,
                    'url': url_col,
                    'id': id_col,
                },
                'all_headers': headers,
            }
        }


csv_ingest_service = CsvIngestService()
