# This module defines the RawDataManager class, responsible for managing the storage and retrieval of raw social media data batches, as well as logging collection metadata and saving cleaned data.
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# The RawDataManager class provides methods to save raw data batches, list collections, retrieve specific collections, load raw records, and save cleaned data along with reports.
class RawDataManager:
    def __init__(self, base_data_dir: str = 'data'):
        self.base_data_dir = base_data_dir
        self.raw_dir = os.path.join(self.base_data_dir, 'raw_social_data')
        self.cleaned_dir = os.path.join(self.base_data_dir, 'cleaned_social_data')
        self.collection_log_path = os.path.join(self.raw_dir, 'collection_log.jsonl')

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.cleaned_dir, exist_ok=True)
    # This method creates a directory for the current day within the specified root directory, ensuring that data is organized by date.
    def _daily_dir(self, root: str) -> str:
        day = datetime.utcnow().strftime('%Y-%m-%d')
        target = os.path.join(root, day)
        os.makedirs(target, exist_ok=True)
        return target
::
    # This method saves a batch of raw records to a JSONL file, along with metadata about the collection, and logs the collection in a separate log file.
    def save_raw_batch(self, source: str, query: str, records: List[Dict], run_meta: Optional[Dict] = None) -> Dict:
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        collection_id = f"{source}-{timestamp}"
        out_dir = self._daily_dir(self.raw_dir)
        file_name = f"raw_{source}_{timestamp}.jsonl"
        file_path = os.path.join(out_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + '\n')

        # This is to capture all the 
        entry = {
            'collection_id': collection_id,
            'source': source,
            'query': query,
            'count': len(records),
            'raw_file': file_path,
            'collected_at_utc': datetime.utcnow().isoformat(),
            'run_meta': run_meta or {}
        }

        with open(self.collection_log_path, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + '\n')

        return entry

    # This method lists recent collections of raw social media data, reading from the collection log file and returning a list of collection entries, limited by the specified number.
    def list_collections(self, limit: int = 20) -> List[Dict]:
        if not os.path.exists(self.collection_log_path):
            return []

        entries: List[Dict] = []
        with open(self.collection_log_path, 'r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return list(reversed(entries[-limit:]))

    # This method retrieves a specific collection entry by its collection_id, searching through the recent collections and returning the matching entry if found.
    def get_collection(self, collection_id: str) -> Optional[Dict]:
        for entry in self.list_collections(limit=1000):
            if entry.get('collection_id') == collection_id:
                return entry
        return None
    
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
