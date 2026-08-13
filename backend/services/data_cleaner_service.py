# This module defines the DataCleanerService class, responsible for cleaning and normalizing raw social media data.
import re
from typing import Dict, List, Optional, Tuple

from config import Config
from services.lexicon_service import lexicon_service
from services.political_entity_service import political_entity_service

# The DataCleanerService class provides methods to normalize, clean and filter data from social media
class DataCleanerService:
    URL_PATTERN = re.compile(r'https?://\S+', re.IGNORECASE)
    WHITESPACE_PATTERN = re.compile(r'\s+')

    # The constructor initializes the service with keywords and hashtags from the configuration.
    def __init__(self):
        self.keywords = [term.lower() for term in Config.POLITICAL_KEYWORDS]
        self.hashtags = [tag.lower().lstrip('#') for tag in Config.POLITICAL_HASHTAGS]

    def _build_dynamic_political_terms(self) -> List[str]:
        terms = set(self.keywords)
        terms.update(self.hashtags)

        try:
            terms.update(political_entity_service.get_search_terms())
        except Exception:
            pass

        try:
            legacy_lexicon = lexicon_service.legacy_lexicon or {}
            political_words = legacy_lexicon.get('political', {}) or {}
            botswana_specific = legacy_lexicon.get('botswana_specific', {}) or {}

            terms.update(word.strip().lower() for word in political_words.keys() if word)
            terms.update(word.strip().lower() for word in botswana_specific.keys() if word)
        except Exception:
            pass

        return sorted(term for term in terms if term)

    # The normalize_text method removes URLs, collapses whitespace, and converts text to lowercase for uniformity.
    def normalize_text(self, text: str) -> str:
        cleaned = self.URL_PATTERN.sub(' ', text or '')
        cleaned = self.WHITESPACE_PATTERN.sub(' ', cleaned)
        return cleaned.strip().lower()

    # This method calculates a simple relevance score based on the presence of configured keywords and hashtags.
    # `political_terms` can be pre-computed once per batch (see clean_records) and passed in, to avoid rebuilding
    # the same DB-backed + lexicon-backed term set (a real per-record perf cost) on every single record.
    def _relevance_score(self, normalized_text: str, political_terms: Optional[List[str]] = None) -> int:
        if political_terms is None:
            political_terms = self._build_dynamic_political_terms()
        score = 0
        for term in political_terms:
            if term and term in normalized_text:
                score += 1
        return score

    def get_dynamic_terms(self) -> List[str]:
        return self._build_dynamic_political_terms()

    # This method applies normalization and relevance scoring to a single record, determining if it should be kept or dropped.
    def _clean_record(self, record: Dict, filter_mode: str = 'relaxed', political_terms: Optional[List[str]] = None) -> Tuple[bool, Dict, str]:
        raw_text = record.get('text_raw', '')
        normalized_text = self.normalize_text(raw_text)
        filter_mode = (filter_mode or 'relaxed').strip().lower()
        if political_terms is None:
            political_terms = self._build_dynamic_political_terms()

        relevance_score = self._relevance_score(normalized_text, political_terms=political_terms)

        if filter_mode == 'strict':
            if len(normalized_text) < 12:
                return False, {}, 'too_short'

            if relevance_score < 1:
                return False, {}, 'irrelevant'

        cleaned = dict(record)
        cleaned['text_clean'] = normalized_text
        cleaned['cleaning_meta'] = {
            'relevance_score': relevance_score,
            'cleaned': True,
            'filter_mode': filter_mode,
            'political_terms_used': len(political_terms),
            'relevance_label': 'relevant' if relevance_score > 0 else 'unmatched'
        }

        if filter_mode == 'relaxed':
            return True, cleaned, 'kept_relaxed'

        return True, cleaned, 'ok'

    # This method processes a batch of records, applying cleaning and filtering logic, and returns the cleaned records along with a report.
    def clean_records(self, records: List[Dict], filter_mode: str = 'relaxed') -> Tuple[List[Dict], Dict]:
        filter_mode = (filter_mode or 'relaxed').strip().lower()
        if filter_mode not in ('relaxed', 'strict'):
            raise ValueError("filter_mode must be 'relaxed' or 'strict'")

        # Compute the political-terms set once for the whole batch instead of once per record
        # (it's DB-backed + lexicon-backed, so rebuilding it per record was a real perf cost).
        political_terms = self._build_dynamic_political_terms()

        dedupe = set()
        cleaned_records: List[Dict] = []
        dropped = {
            'too_short': 0,
            'irrelevant': 0,
            'duplicate': 0
        }

        for record in records:
            keep, cleaned, reason = self._clean_record(record, filter_mode=filter_mode, political_terms=political_terms)
            if not keep:
                dropped[reason] = dropped.get(reason, 0) + 1
                continue

            if filter_mode == 'strict':
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
            'filter_mode': filter_mode,
            'drop_breakdown': dropped
        }
        return cleaned_records, report


data_cleaner_service = DataCleanerService()