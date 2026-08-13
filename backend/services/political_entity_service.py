import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import PoliticalEntity


class PoliticalEntityService:
    """Political entity CRUD + text matching, backed by the PoliticalEntity table.

    Schema creation, seeding, and the DB connection lifecycle are handled by
    Flask-Migrate / models.seed_defaults_if_empty() at app startup — this
    service only reads/writes rows within the current request's app context.
    """

    # Public methods for API routes and internal use
    def list_entities(self, entity_type: Optional[str] = None) -> List[Dict]:
        query = PoliticalEntity.query
        if entity_type:
            query = query.filter_by(type=entity_type.strip().lower())
        query = query.order_by(PoliticalEntity.type.asc(), PoliticalEntity.entity.asc())
        return [row.to_dict() for row in query.all()]

    # Adds a new political entity, returns dict with 'ok' status and 'id' or 'error' message
    def add_entity(self, entity: str, entity_type: str, full_name: str = '', description: str = '') -> Dict:
        clean_entity = (entity or '').strip()
        clean_type = (entity_type or '').strip().lower()

        if not clean_entity:
            return {'ok': False, 'error': 'entity is required'}

        if not clean_type:
            return {'ok': False, 'error': 'type is required'}

        row = PoliticalEntity(
            entity=clean_entity,
            normalized_entity=clean_entity.lower(),
            type=clean_type,
            full_name=(full_name or '').strip(),
            description=(description or '').strip(),
            created_at=datetime.now(timezone.utc),
        )

        try:
            db.session.add(row)
            db.session.commit()
            return {'ok': True, 'id': row.id}
        except IntegrityError:
            db.session.rollback()
            return {'ok': False, 'error': 'Entity already exists for this type'}
        except Exception as exc:
            db.session.rollback()
            return {'ok': False, 'error': str(exc)}

    # Deletes an entity by ID, returns True if deleted, False if not found
    def delete_entity(self, entity_id: int) -> bool:
        row = PoliticalEntity.query.get(entity_id)
        if row is None:
            return False
        db.session.delete(row)
        db.session.commit()
        return True

    # Extracts political entities from text by matching against database entries, returns list of matches with metadata.
    # `entities` can be pre-fetched (via list_entities()) and passed in to avoid a DB round-trip per call —
    # batch_analysis_service does this to avoid re-querying every entity on every row of a batch.
    def extract_entities(self, text: str, entities: Optional[List[Dict]] = None) -> List[Dict]:
        normalized_text = (text or '').lower()
        if entities is None:
            entities = self.list_entities()
        matches: List[Dict] = []
        seen = set()

        for item in entities:
            entity_name = item.get('entity', '')
            full_name = item.get('full_name', '')
            entity_type = item.get('type', 'unknown')

            candidates = [entity_name]
            if full_name and full_name.lower() != entity_name.lower():
                candidates.append(full_name)

            for candidate in candidates:
                if not candidate:
                    continue

                pattern = r'\b' + re.escape(candidate.lower()) + r'\b'
                if re.search(pattern, normalized_text):
                    key = (entity_name.lower(), entity_type)
                    if key in seen:
                        break
                    seen.add(key)
                    matches.append(
                        {
                            'entity': entity_name,
                            'type': entity_type,
                            'full_name': full_name,
                            'description': item.get('description', ''),
                        }
                    )
                    break

        return matches

    def get_search_terms(self) -> List[str]:
        terms = set()

        for entity in self.list_entities():
            entity_name = (entity.get('entity') or '').strip().lower()
            full_name = (entity.get('full_name') or '').strip().lower()

            if entity_name:
                terms.add(entity_name)

            if full_name:
                terms.add(full_name)
                terms.update(part for part in re.split(r'\s+', full_name) if part)

                compact = re.sub(r'[^a-z0-9]+', '', full_name)
                snake_case = re.sub(r'[^a-z0-9]+', '_', full_name).strip('_')

                if compact:
                    terms.add(compact)
                    terms.add(f'@{compact}')
                if snake_case:
                    terms.add(snake_case)
                    terms.add(f'@{snake_case}')

            if entity_name:
                compact_entity = re.sub(r'[^a-z0-9]+', '', entity_name)
                if compact_entity:
                    terms.add(compact_entity)
                    terms.add(f'@{compact_entity}')

        return sorted(term for term in terms if term)


political_entity_service = PoliticalEntityService()
