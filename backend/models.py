"""SQLAlchemy models backing the structured/queryable parts of the app.

Large raw/cleaned social-media payloads stay on disk as JSONL files (see
services/raw_data_manager.py) — this module only covers data that is
actually queried, filtered, or joined: political entities, the Setswana
lexicon, analysis job metadata, and the collection index.
"""
from datetime import datetime, timezone

from extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PoliticalEntity(db.Model):
    __tablename__ = 'political_entities'
    __table_args__ = (
        db.UniqueConstraint('normalized_entity', 'type', name='uq_entity_type'),
    )

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(255), nullable=False)
    normalized_entity = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(255), default='')
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'entity': self.entity,
            'type': self.type,
            'full_name': self.full_name or '',
            'description': self.description or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LexiconEntry(db.Model):
    __tablename__ = 'lexicon_entries'
    __table_args__ = (
        db.UniqueConstraint('word', 'category', name='uq_word_category'),
    )

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    meaning = db.Column(db.Text, default='')
    intensity = db.Column(db.String(50))
    context = db.Column(db.String(100))
    type = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    source = db.Column(db.String(50), default='system')
    added_date = db.Column(db.DateTime, default=_utcnow, nullable=False)
    last_modified = db.Column(db.DateTime)

    def to_details_dict(self) -> dict:
        """Mirror the legacy per-word details dict shape used throughout the app."""
        details = {'meaning': self.meaning or ''}
        for key in ('intensity', 'context', 'type', 'frequency', 'source'):
            value = getattr(self, key)
            if value:
                details[key] = value
        details['added_date'] = self.added_date.isoformat() if self.added_date else None
        if self.last_modified:
            details['last_modified'] = self.last_modified.isoformat()
        return details


class Collection(db.Model):
    """Index of collected raw social-media batches.

    The actual records stay in JSONL files on disk (raw_file); this table
    is only the queryable index, replacing the old collection_log.jsonl
    linear-scan approach.
    """
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False)
    search_query = db.Column(db.Text, default='')
    count = db.Column(db.Integer, default=0)
    raw_file = db.Column(db.String(500), nullable=False)
    collected_at_utc = db.Column(db.DateTime, default=_utcnow, nullable=False)
    run_meta = db.Column(db.JSON, default=dict)

    def to_dict(self) -> dict:
        return {
            'collection_id': self.collection_id,
            'source': self.source,
            'query': self.search_query or '',
            'count': self.count or 0,
            'raw_file': self.raw_file,
            'collected_at_utc': self.collected_at_utc.isoformat() if self.collected_at_utc else None,
            'run_meta': self.run_meta or {},
        }


class AnalysisJob(db.Model):
    """A completed batch-analysis run: metadata + aggregates + per-row detail."""
    __tablename__ = 'analysis_jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    collection_id = db.Column(db.String(255), nullable=False, index=True)
    filename = db.Column(db.String(500), default='')
    analyzed_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    total_rows = db.Column(db.Integer, default=0)
    avg_confidence = db.Column(db.Float, default=0.0)
    model_used = db.Column(db.String(255), default='unknown')
    sentiment_distribution = db.Column(db.JSON, default=dict)
    top_trigger_words = db.Column(db.JSON, default=list)
    top_entities = db.Column(db.JSON, default=list)
    rows = db.Column(db.JSON, default=list)

    def to_summary_dict(self) -> dict:
        """Metadata-only shape, for job listing (no row-level detail)."""
        return {
            'job_id': self.job_id,
            'collection_id': self.collection_id,
            'filename': self.filename or '',
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'row_count': self.total_rows or 0,
            'sentiment_summary': self.sentiment_distribution or {},
        }

    def to_full_dict(self) -> dict:
        """Full shape, matching the legacy per-job JSON file format."""
        return {
            'job_id': self.job_id,
            'collection_id': self.collection_id,
            'filename': self.filename or '',
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'rows': self.rows or [],
            'aggregate': {
                'total_rows': self.total_rows or 0,
                'sentiment_distribution': self.sentiment_distribution or {},
                'avg_confidence': self.avg_confidence or 0,
                'top_trigger_words': self.top_trigger_words or [],
                'top_entities': self.top_entities or [],
                'model_used': self.model_used or 'unknown',
            },
        }


DEFAULT_POLITICAL_ENTITIES = [
    {'entity': 'BDP', 'type': 'party', 'full_name': 'Botswana Democratic Party', 'description': 'Political party'},
    {'entity': 'UDC', 'type': 'party', 'full_name': 'Umbrella for Democratic Change', 'description': 'Political party'},
    {'entity': 'BCP', 'type': 'party', 'full_name': 'Botswana Congress Party', 'description': 'Political party'},
    {'entity': 'AP', 'type': 'party', 'full_name': 'Alliance for Progressives', 'description': 'Political party'},
    {'entity': 'Masisi', 'type': 'leader', 'full_name': 'Mokgweetsi Masisi', 'description': 'Political leader'},
    {'entity': 'Boko', 'type': 'leader', 'full_name': 'Duma Boko', 'description': 'Political leader'},
    {'entity': 'Saleshando', 'type': 'leader', 'full_name': 'Dumelang Saleshando', 'description': 'Political leader'},
    {'entity': 'Khama', 'type': 'leader', 'full_name': 'Ian Khama', 'description': 'Political leader'},
    {'entity': 'Gaborone', 'type': 'location', 'full_name': 'Gaborone', 'description': 'Capital city'},
    {'entity': 'Francistown', 'type': 'location', 'full_name': 'Francistown', 'description': 'Second largest city'},
    {'entity': 'Maun', 'type': 'location', 'full_name': 'Maun', 'description': 'Tourism hub'},
    {'entity': 'Serowe', 'type': 'location', 'full_name': 'Serowe', 'description': 'Traditional capital'},
]


def seed_defaults_if_empty() -> None:
    """Idempotent seed so a fresh clone + `flask db upgrade` isn't empty.

    Safe to call on every startup — each seed only inserts if its table is
    currently empty.
    """
    if PoliticalEntity.query.first() is None:
        for item in DEFAULT_POLITICAL_ENTITIES:
            db.session.add(PoliticalEntity(
                entity=item['entity'],
                normalized_entity=item['entity'].strip().lower(),
                type=item['type'].strip().lower(),
                full_name=item.get('full_name', ''),
                description=item.get('description', ''),
            ))

    if LexiconEntry.query.first() is None:
        from services.lexicon_defaults import DEFAULT_LEXICON
        for category, words in DEFAULT_LEXICON.items():
            for word, details in words.items():
                db.session.add(LexiconEntry(
                    word=word,
                    category=category,
                    meaning=details.get('meaning', ''),
                    intensity=details.get('intensity'),
                    context=details.get('context'),
                    type=details.get('type'),
                    frequency=details.get('frequency'),
                    source='system',
                ))

    db.session.commit()
