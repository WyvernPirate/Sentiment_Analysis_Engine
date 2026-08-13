#!/usr/bin/env python3
"""
Setswana Lexicon Manager for Botswana Political Sentiment Analysis.

Backed by the LexiconEntry table (see models.py) instead of a JSON file
that got rewritten whole on every edit — that approach had no locking, so
concurrent writers could corrupt or lose data. Per-word CRUD now goes
straight to the database; `self.lexicon` is kept as an in-memory dict
projection (same category -> word -> details shape callers already expect)
so the rest of the app didn't need to change.
"""

import csv
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

from extensions import db
from models import LexiconEntry
from services.lexicon_defaults import DEFAULT_LEXICON

CATEGORIES = ('common_words', 'positive', 'negative', 'political', 'botswana_specific')


class SetswanaLexiconManager:
    def __init__(self):
        # Deliberately does NOT query the database here: this singleton is
        # constructed at module-import time, before the Flask app (and thus
        # the DB connection) exists. Call refresh() once an app context is
        # available (create_app() does this at startup); routes that read
        # lexicon data also call refresh() to stay correct across workers.
        self.lexicon: Dict = {category: {} for category in CATEGORIES}
        self.lexicon['metadata'] = {
            'version': '2.0',
            'last_updated': None,
            'total_words': 0,
            'contributors': ['system'],
            'sources': ['database'],
        }

    def refresh(self) -> Dict:
        """Rebuild the in-memory dict projection from the database."""
        lexicon: Dict = {category: {} for category in CATEGORIES}
        last_updated = None

        for entry in LexiconEntry.query.all():
            lexicon.setdefault(entry.category, {})[entry.word] = entry.to_details_dict()
            modified = entry.last_modified or entry.added_date
            if modified and (last_updated is None or modified > last_updated):
                last_updated = modified

        total_words = sum(len(words) for words in lexicon.values())
        lexicon['metadata'] = {
            'version': '2.0',
            'last_updated': (last_updated or datetime.now(timezone.utc)).isoformat(),
            'total_words': total_words,
            'contributors': ['system'],
            'sources': ['database'],
        }

        self.lexicon = lexicon
        return self.lexicon

    def get_default_lexicon(self) -> Dict:
        """Retained for callers that want the baseline seed content directly."""
        return DEFAULT_LEXICON

    def add_word(self, word: str, category: str, meaning: str, **kwargs) -> bool:
        """Add (or update, if it already exists) a word in the lexicon."""
        try:
            word = word.lower().strip()
            entry = LexiconEntry.query.filter_by(word=word, category=category).first()

            if entry is None:
                entry = LexiconEntry(word=word, category=category, source=kwargs.get('source', 'user_contribution'))
                db.session.add(entry)
            else:
                entry.last_modified = datetime.now(timezone.utc)

            entry.meaning = meaning
            for key in ('intensity', 'context', 'type', 'frequency'):
                if key in kwargs and kwargs[key]:
                    setattr(entry, key, kwargs[key])

            db.session.commit()
            self.refresh()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error adding word: {e}")
            return False

    def remove_word(self, word: str, category: str) -> bool:
        """Remove a word from the lexicon."""
        try:
            word = word.lower().strip()
            entry = LexiconEntry.query.filter_by(word=word, category=category).first()
            if entry is None:
                return False

            db.session.delete(entry)
            db.session.commit()
            self.refresh()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error removing word: {e}")
            return False

    def update_word(self, word: str, category: str, **updates) -> bool:
        """Update an existing word in the lexicon."""
        try:
            word = word.lower().strip()
            entry = LexiconEntry.query.filter_by(word=word, category=category).first()
            if entry is None:
                return False

            for key, value in updates.items():
                if hasattr(entry, key) and key not in ('id', 'word', 'category'):
                    setattr(entry, key, value)
            entry.last_modified = datetime.now(timezone.utc)

            db.session.commit()
            self.refresh()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error updating word: {e}")
            return False

    def search_words(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search for words in the lexicon."""
        query = (query or '').lower().strip()
        results = []

        for cat, words in self.lexicon.items():
            if cat == 'metadata':
                continue
            if category and cat != category:
                continue

            for word, details in words.items():
                if (query in word or
                        query in str(details.get('meaning', '')).lower() or
                        any(query in str(v).lower() for v in details.values())):
                    results.append({'word': word, 'category': cat, 'details': details})

        return results

    def get_category_stats(self) -> Dict:
        """Get statistics for each category."""
        stats = {}
        now = datetime.now(timezone.utc)

        for category, words in self.lexicon.items():
            if category == 'metadata':
                continue

            recent = 0
            for details in words.values():
                added_date = details.get('added_date')
                if added_date:
                    try:
                        added_dt = datetime.fromisoformat(added_date)
                        if added_dt.tzinfo is None:
                            added_dt = added_dt.replace(tzinfo=timezone.utc)
                        if (now - added_dt).days <= 7:
                            recent += 1
                    except ValueError:
                        pass

            stats[category] = {'word_count': len(words), 'recent_additions': recent}

        return stats

    def count_total_words(self) -> int:
        """Count total words in lexicon."""
        return sum(len(words) for category, words in self.lexicon.items() if category != 'metadata')

    def export_to_csv(self, filename: str) -> bool:
        """Export lexicon to CSV for training data."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['word', 'category', 'meaning', 'sentiment', 'context', 'intensity'])

                for category, words in self.lexicon.items():
                    if category == 'metadata':
                        continue

                    sentiment = 1
                    if category == 'positive':
                        sentiment = 2
                    elif category == 'negative':
                        sentiment = 0

                    for word, details in words.items():
                        writer.writerow([
                            word,
                            category,
                            details.get('meaning', ''),
                            sentiment,
                            details.get('context', ''),
                            details.get('intensity', 'medium'),
                        ])

            return True

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def import_from_csv(self, filename: str) -> bool:
        """Import words from CSV file."""
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    word = row.get('word', '').strip()
                    category = row.get('category', 'common_words')
                    meaning = row.get('meaning', '')

                    if word and meaning:
                        self.add_word(
                            word,
                            category,
                            meaning,
                            context=row.get('context', ''),
                            intensity=row.get('intensity', 'medium'),
                            source='csv_import',
                        )

            return True

        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False

    def generate_training_sentences(self, count: int = 100) -> List[Tuple[str, int]]:
        """Generate template-based training sentences using the lexicon.

        NOTE: these are synthetic/template-generated, not organic text —
        useful as a bootstrap scaffold only, not a substitute for real
        labeled data.
        """
        import random

        sentences = []
        templates = {
            'positive': [
                "Ke {positive} {political}",
                "{political} e {positive} thata",
                "Batho ba {positive} {political}",
                "{political} o dira {positive}",
                "Re {positive} ka {political}",
            ],
            'negative': [
                "Ke {negative} {political}",
                "{political} e {negative} thata",
                "Batho ba {negative} {political}",
                "{political} o dira {negative}",
                "Re {negative} ka {political}",
            ],
            'neutral': [
                "Ke bona {political}",
                "{political} e teng",
                "Batho ba bua ka {political}",
                "Re itse {political}",
                "{political} o kae",
            ],
        }

        for _ in range(count):
            sentiment_type = random.choice(['positive', 'negative', 'neutral'])
            template = random.choice(templates[sentiment_type])

            if '{positive}' in template:
                template = template.replace('{positive}', random.choice(list(self.lexicon['positive'].keys())))
            if '{negative}' in template:
                template = template.replace('{negative}', random.choice(list(self.lexicon['negative'].keys())))
            if '{political}' in template:
                template = template.replace('{political}', random.choice(list(self.lexicon['political'].keys())))

            label = 1
            if sentiment_type == 'positive':
                label = 2
            elif sentiment_type == 'negative':
                label = 0

            sentences.append((template, label))

        return sentences


lexicon_manager = SetswanaLexiconManager()
