# this module is responsible for collecting social media posts from X using the Twitter API v2.
from datetime import datetime
from typing import Dict, List, Optional

import requests

from config import Config

#  This function builds a default query using political keywords and hashtags from config 
class SocialCollectorService:
    X_RECENT_SEARCH_URL = 'https://api.twitter.com/2/tweets/search/recent'

    def __init__(self):
        self.bearer_token = Config.TWITTER_BEARER_TOKEN

    # This function constructs a default query string for collecting relavent posts
    def _build_default_query(self) -> str:
        keywords = Config.POLITICAL_KEYWORDS[:8]
        hashtags = [tag.lstrip('#') for tag in Config.POLITICAL_HASHTAGS[:4]]
        parts = [f'"{term}"' for term in keywords] + [f'#{tag}' for tag in hashtags]
        base_query = ' OR '.join(parts)
        return f"({base_query}) -is:retweet"

    # Function for collecting posts from X based on a query and max results. 
    def collect_x_recent_posts(self, query: Optional[str] = None, max_results: int = 20) -> Dict:
        if not self.bearer_token:
            raise RuntimeError('TWITTER_BEARER_TOKEN is required for X collection')

        # Ensure max_results is within acceptable bounds to prevent abuse and manage API limits
        safe_max = max(10, min(int(max_results), 100))
        active_query = (query or '').strip() or self._build_default_query()

        # Set up headers and parameters for the API request, including authentication and query details
        headers = {'Authorization': f'Bearer {self.bearer_token}'}
        params = {
            'query': active_query,
            'max_results': safe_max,
            'tweet.fields': 'id,text,author_id,created_at,lang,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'id,name,username'
        }

        # Make the API request to X and handle potential errors
        response = requests.get(
            self.X_RECENT_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=20
        )

        # Check for HTTP errors
        if response.status_code >= 400:
            raise RuntimeError(f'X API request failed: {response.status_code} {response.text}')

        payload = response.json()
        users_by_id = {
            user.get('id'): user
            for user in payload.get('includes', {}).get('users', [])
            if user.get('id')
        }

        normalized_records: List[Dict] = []
        fetched_at = datetime.utcnow().isoformat()

        # Normalize each tweet into our internal format, enriching with author info and metadata
        for tweet in payload.get('data', []):
            author_id = tweet.get('author_id')
            author = users_by_id.get(author_id, {})
            normalized_records.append(
                {
                    'source': 'x',
                    'source_post_id': tweet.get('id', ''),
                    'author_id': author_id,
                    'author_username': author.get('username', ''),
                    'author_name': author.get('name', ''),
                    'created_at_utc': tweet.get('created_at', ''),
                    'text_raw': tweet.get('text', ''),
                    'language': tweet.get('lang', ''),
                    'public_metrics': tweet.get('public_metrics', {}),
                    'query_used': active_query,
                    'fetched_at_utc': fetched_at
                }
            )

        return {
            'source': 'x',
            'query': active_query,
            'count': len(normalized_records),
            'records': normalized_records,
            'meta': payload.get('meta', {})
        }


social_collector_service = SocialCollectorService()