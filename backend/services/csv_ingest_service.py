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

    def _is_fragmented_scraper_csv(self, headers: List[str]) -> bool:
        """Detect if the CSV has technical CSS headers typical of messy scrapers."""
        css_header_count = sum(1 for h in headers if 'css-' in h.lower() or 'r-' in h.lower())
        return css_header_count > len(headers) / 2

    def _stitch_fragmented_text(self, row: Dict, headers: List[str]) -> str:
        """
        Heuristic: merge adjacent columns that contain text segments.
        Specifically handles the 'css-1jxf684' style where text is split.
        """
        # Common political keywords that often trigger splits in scrapers (due to being links)
        SPLIT_TRIGGERS = {'duma', 'boko', 'masisi', 'bdp', 'udc', 'bcp', 'botswana'}
        
        fragments = []
        # We look at columns in order. If they are adjacent and contain text, we join them.
        for h in headers:
            val = str(row.get(h, '') or '').strip()
            if val:
                fragments.append(val)
        
        # Heuristic: Find a sequence that looks like a sentence
        # In messy scrapers, the text is often in a specific range of columns
        # For 'Instant Data Scraper', it's usually the middle-to-end columns
        text_candidate = " ".join(fragments)
        # Clean up multiple spaces
        import re
        return re.sub(r'\s+', ' ', text_candidate).strip()

    def parse_csv(self, file_content: str, filename: str = 'upload.csv') -> Dict:
        """
        Parse CSV content into normalized social records.
        Now includes 'Auto-Repair' for fragmented scraper outputs.
        """
        reader = csv.DictReader(io.StringIO(file_content))
        headers = reader.fieldnames or []
        rows = list(reader)

        if not headers:
            raise ValueError('CSV file has no headers')
        if not rows:
            raise ValueError('CSV file has no data rows')

        # Detect columns using standard candidate names
        text_col = self._detect_column(headers, TEXT_COLUMN_NAMES)
        author_col = self._detect_column(headers, AUTHOR_COLUMN_NAMES)
        date_col = self._detect_column(headers, DATE_COLUMN_NAMES)
        url_col = self._detect_column(headers, URL_COLUMN_NAMES)
        id_col = self._detect_column(headers, ID_COLUMN_NAMES)

        is_fragmented = False
        # If standard detection fails AND it looks like a messy scraper file, try Auto-Repair
        if not text_col and self._is_fragmented_scraper_csv(headers):
            is_fragmented = True
            # For messy scrapers, we pick common indices if they aren't named
            # Based on user's sample: Name=Col3, Handle=Col5, URL=Col6, Date=Col7
            if not author_col and len(headers) > 2: author_col = headers[2]
            if not url_col and len(headers) > 5: url_col = headers[5]
            if not date_col and len(headers) > 6: date_col = headers[6]

        # Fallback text column detection if still not found
        if not text_col and not is_fragmented:
            text_col = self._detect_text_column_by_content(headers, rows)

        if not text_col and not is_fragmented:
            raise ValueError(
                f'Could not detect a text column. Headers found: {headers}.'
            )

        fetched_at = datetime.utcnow().isoformat()
        query_label = f'csv_upload:{filename}'
        records = []

        for idx, row in enumerate(rows):
            if is_fragmented:
                # Merge columns that look like text fragments (usually starting from col 7-8 in sample)
                # But we'll try a safer approach: merge everything after the known metadata columns
                # or just use the _stitch method on a subset
                text_raw = self._stitch_fragmented_text(row, headers[7:15])
            else:
                text_raw = str(row.get(text_col, '') or '').strip()

            if not text_raw:
                continue

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
                'raw_item': dict(row),
                'was_repaired': is_fragmented
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
                'was_auto_repaired': is_fragmented,
                'detected_columns': {
                    'text': 'REPAIRED_FRAGMENTS' if is_fragmented else text_col,
                    'author': author_col,
                    'date': date_col,
                    'url': url_col,
                }
            }
        }


csv_ingest_service = CsvIngestService()
