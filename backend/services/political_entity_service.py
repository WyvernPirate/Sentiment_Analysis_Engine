import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class PoliticalEntityService:
    def __init__(self, db_path: Optional[str] = None):
        default_db = os.path.join('data', 'political_entities.db')
        self.db_path = db_path or os.environ.get('POLITICAL_ENTITY_DB_PATH', default_db)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._ensure_schema()
        self._seed_defaults_if_empty()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._get_conn() as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS political_entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    normalized_entity TEXT NOT NULL,
                    type TEXT NOT NULL,
                    full_name TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(normalized_entity, type)
                )
                '''
            )

    def _seed_defaults_if_empty(self):
        with self._get_conn() as conn:
            row = conn.execute('SELECT COUNT(*) AS count FROM political_entities').fetchone()
            if not row or row['count'] > 0:
                return

            defaults = [
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
                {'entity': 'Serowe', 'type': 'location', 'full_name': 'Serowe', 'description': 'Traditional capital'}
            ]

            for item in defaults:
                normalized = item['entity'].strip().lower()
                now = datetime.utcnow().isoformat()
                conn.execute(
                    '''
                    INSERT INTO political_entities (
                        entity, normalized_entity, type, full_name, description, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        item['entity'].strip(),
                        normalized,
                        item['type'].strip().lower(),
                        item.get('full_name', '').strip(),
                        item.get('description', '').strip(),
                        now,
                    ),
                )

    def list_entities(self, entity_type: Optional[str] = None) -> List[Dict]:
        query = 'SELECT id, entity, type, full_name, description, created_at FROM political_entities'
        params = []

        if entity_type:
            query += ' WHERE type = ?'
            params.append(entity_type.strip().lower())

        query += ' ORDER BY type ASC, entity ASC'

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def add_entity(self, entity: str, entity_type: str, full_name: str = '', description: str = '') -> Dict:
        clean_entity = (entity or '').strip()
        clean_type = (entity_type or '').strip().lower()

        if not clean_entity:
            return {'ok': False, 'error': 'entity is required'}

        if not clean_type:
            return {'ok': False, 'error': 'type is required'}

        normalized = clean_entity.lower()
        now = datetime.utcnow().isoformat()

        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    '''
                    INSERT INTO political_entities (
                        entity, normalized_entity, type, full_name, description, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (clean_entity, normalized, clean_type, full_name.strip(), description.strip(), now),
                )
                return {'ok': True, 'id': cursor.lastrowid}
        except sqlite3.IntegrityError:
            return {'ok': False, 'error': 'Entity already exists for this type'}
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}

    def delete_entity(self, entity_id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute('DELETE FROM political_entities WHERE id = ?', (entity_id,))
            return cursor.rowcount > 0

    def extract_entities(self, text: str) -> List[Dict]:
        normalized_text = (text or '').lower()
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

                pattern = r'\\b' + re.escape(candidate.lower()) + r'\\b'
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


political_entity_service = PoliticalEntityService()
