# This module defines the RawDataManager class, responsible for managing the storage and retrieval of raw social media data batches.
# Large raw/cleaned payloads stay on disk as JSONL files (write-once, append-heavy, no need for relational structure);
# the collection index itself is DB-backed (see models.Collection) instead of an append-only JSONL log that had to be
# linearly scanned (up to the last 1000 entries) on every lookup.
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from extensions import db
from models import Collection


class RawDataManager:
    def __init__(self, base_data_dir: str = 'data'):
        self.base_data_dir = base_data_dir
        self.raw_dir = os.path.join(self.base_data_dir, 'raw_social_data')
        self.cleaned_dir = os.path.join(self.base_data_dir, 'cleaned_social_data')

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.cleaned_dir, exist_ok=True)

    # This method creates a directory for the current day within the specified root directory, ensuring that data is organized by date.
    def _daily_dir(self, root: str) -> str:
        day = datetime.utcnow().strftime('%Y-%m-%d')
        target = os.path.join(root, day)
        os.makedirs(target, exist_ok=True)
        return target

    # This method saves a batch of raw records to a JSONL file, then indexes the collection in the database.
    def save_raw_batch(self, source: str, query: str, records: List[Dict], run_meta: Optional[Dict] = None) -> Dict:
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        collection_id = f"{source}-{timestamp}"
        out_dir = self._daily_dir(self.raw_dir)
        file_name = f"raw_{source}_{timestamp}.jsonl"
        file_path = os.path.join(out_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + '\n')

        row = Collection(
            collection_id=collection_id,
            source=source,
            search_query=query or '',
            count=len(records),
            raw_file=file_path,
            collected_at_utc=datetime.now(timezone.utc),
            run_meta=run_meta or {},
        )
        db.session.add(row)
        db.session.commit()

        return row.to_dict()

    # This method lists recent collections, most-recent first, via an indexed DB query instead of a full log scan.
    def list_collections(self, limit: int = 20) -> List[Dict]:
        rows = (
            Collection.query
            .order_by(Collection.collected_at_utc.desc())
            .limit(limit)
            .all()
        )
        return [row.to_dict() for row in rows]

    # This method retrieves a specific collection entry by its collection_id via an indexed lookup.
    def get_collection(self, collection_id: str) -> Optional[Dict]:
        row = Collection.query.filter_by(collection_id=collection_id).first()
        return row.to_dict() if row else None

    # This method loads raw records from a specified JSONL file path, returning a list of records as dictionaries. It handles cases where the file may not exist or contain invalid JSON lines.
    def load_raw_records(self, raw_file_path: str) -> List[Dict]:
        records: List[Dict] = []
        if not os.path.exists(raw_file_path):
            return records

        with open(raw_file_path, 'r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return records

    # This method saves a batch of cleaned records to a JSONL file, along with a report in JSON format, and returns metadata about the saved files and the count of cleaned records.
    def save_cleaned_batch(self, collection_id: str, cleaned_records: List[Dict], report: Dict) -> Dict:
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        out_dir = self._daily_dir(self.cleaned_dir)

        cleaned_path = os.path.join(out_dir, f"cleaned_{collection_id}_{timestamp}.jsonl")
        report_path = os.path.join(out_dir, f"cleaning_report_{collection_id}_{timestamp}.json")

        with open(cleaned_path, 'w', encoding='utf-8') as handle:
            for record in cleaned_records:
                handle.write(json.dumps(record, ensure_ascii=False) + '\n')

        with open(report_path, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)

        return {
            'cleaned_file': cleaned_path,
            'report_file': report_path,
            'count': len(cleaned_records)
        }


raw_data_manager = RawDataManager()
