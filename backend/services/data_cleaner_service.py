# This module defines the DataCleanerService class, responsible for cleaning and normalizing raw social media data.
import re
from typing import Dict, List, Tuple

from config import Config

# The DataCleanerService class provides methods to normalize, clean and filter data from social media
class DataCleanerService:
    URL_PATTERN = re.compile(r'https?://\S+', re.IGNORECASE)
    WHITESPACE_PATTERN = re.compile(r'\s+')

    # The constructor initializes the service with keywords and hashtags from the configuration.
    def __init__(self):
        self.keywords = [term.lower() for term in Config.POLITICAL_KEYWORDS]
        self.hashtags = [tag.lower().lstrip('#') for tag in Config.POLITICAL_HASHTAGS]

    # The normalize_text method removes URLs, collapses whitespace, and converts text to lowercase for uniformity.
    def normalize_text(self, text: str) -> str:
        cleaned = self.URL_PATTERN.sub(' ', text or '')
        cleaned = self.WHITESPACE_PATTERN.sub(' ', cleaned)
        return cleaned.strip().lower()

    # This method calculates a simple relevance score based on the presence of configured keywords and hashtags.
    def _relevance_score(self, normalized_text: str) -> int:
        score = 0
        for term in self.keywords:
            if term and term in normalized_text:
                score += 1
        for tag in self.hashtags:
            if tag and tag in normalized_text:
                score += 1
        return score

    # This method applies normalization and relevance scoring to a single record, determining if it should be kept or dropped.
    def _clean_record(self, record: Dict) -> Tuple[bool, Dict, str]:
        raw_text = record.get('text_raw', '')
        normalized_text = self.normalize_text(raw_text)

        if len(normalized_text) < 12:
            return False, {}, 'too_short'

        relevance_score = self._relevance_score(normalized_text)
        if relevance_score < 1:
            return False, {}, 'irrelevant'

        cleaned = dict(record)
        cleaned['text_clean'] = normalized_text
        cleaned['cleaning_meta'] = {
            'relevance_score': relevance_score,
            'cleaned': True
        }
        return True, cleaned, 'ok'

    # This method processes a batch of records, applying cleaning and filtering logic, and returns the cleaned records along with a report.
    def clean_records(self, records: List[Dict]) -> Tuple[List[Dict], Dict]:
        dedupe = set()
        cleaned_records: List[Dict] = []
        dropped = {
            'too_short': 0,
            'irrelevant': 0,
            'duplicate': 0
        }

        for record in records:
            keep, cleaned, reason = self._clean_record(record)
            if not keep:
                dropped[reason] = dropped.get(reason, 0) + 1
                continue

            dedupe_key = cleaned.get('text_clean', '')
            if dedupe_key in dedupe:
                dropped['duplicate'] += 1
                continue

            dedupe.add(dedupe_key)
            cleaned_records.append(cleaned)

        report = {
            'total_records': len(records),
            'cleaned_records': len(cleaned_records),
            'dropped_records': sum(dropped.values()),
            'drop_breakdown': dropped
        }
        return cleaned_records, report


data_cleaner_service = DataCleanerService()