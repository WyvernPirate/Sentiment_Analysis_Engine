import json
import asyncio
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests

try:
    from twikit import Client as TwikitClient
except Exception:
    TwikitClient = None

from config import Config
from services.lexicon_service import lexicon_service
from services.political_entity_service import political_entity_service

class SocialCollectorService:
    APIFY_RUNS_URL_TEMPLATE = 'https://api.apify.com/v2/acts/{actor_id}/runs'
    APIFY_DATASET_ITEMS_URL_TEMPLATE = 'https://api.apify.com/v2/datasets/{dataset_id}/items'

    STOPWORDS = {
        'a', 'an', 'and', 'as', 'at', 'be', 'by', 'change', 'congress', 'democratic', 'for', 'from',
        'in', 'is', 'of', 'on', 'or', 'party', 'politics', 'progressives', 'the', 'to', 'udc', 'ap', 'bcp', 'bdp'
    }

    def __init__(self):
        self.provider_default = (Config.SOCIAL_PROVIDER or 'brightdata').strip().lower()
        self.brightdata_token = Config.BRIGHTDATA_API_TOKEN
        self.brightdata_collector_url = Config.BRIGHTDATA_COLLECTOR_URL
        self.apify_api_token = Config.APIFY_API_TOKEN
        self.apify_actor_id = Config.APIFY_ACTOR_ID
        self.twikit_username = Config.TWIKIT_USERNAME
        self.twikit_email = Config.TWIKIT_EMAIL
        self.twikit_password = Config.TWIKIT_PASSWORD
        self.twikit_cookies_path = Config.TWIKIT_COOKIES_PATH
        self.twikit_language = Config.TWIKIT_LANGUAGE
        self.twikit_enable_ui_metrics = Config.TWIKIT_ENABLE_UI_METRICS

    def _normalized_brightdata_token(self) -> str:
        token = (self.brightdata_token or '').strip().strip('"').strip("'")
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        return token

    def _normalized_apify_token(self) -> str:
        token = (self.apify_api_token or '').strip().strip('"').strip("'")
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        return token

    # This function constructs a default query string for collecting relavent posts
    def _build_default_query(self) -> str:
        return self._build_query_from_terms(self._build_dynamic_search_terms())

    def _build_query_from_terms(self, terms: List[str]) -> str:
        clean_terms: List[str] = []
        seen = set()

        for term in terms:
            normalized = (term or '').strip().lower()
            if not normalized:
                continue
            if normalized in self.STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            clean_terms.append(normalized)

        if not clean_terms:
            clean_terms = [kw.lower() for kw in Config.POLITICAL_KEYWORDS[:6] if kw]

        parts: List[str] = []
        for term in clean_terms:
            if term.startswith('@') or term.startswith('#'):
                parts.append(term)
            elif ' ' in term:
                parts.append(f'"{term}"')
            else:
                parts.append(term)

        base_query = ' OR '.join(parts)
        return f"({base_query}) -is:retweet"

    def _build_dynamic_search_terms(self) -> List[str]:
        terms = set()

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

    def _focus_terms_for_entity(self, seed_entity: Optional[str] = None, focus_terms: Optional[List[str]] = None) -> List[str]:
        terms: List[str] = []

        if focus_terms:
            terms.extend(focus_terms)

        seed = (seed_entity or '').strip().lower()
        if seed:
            for entity in political_entity_service.list_entities():
                entity_name = (entity.get('entity') or '').strip().lower()
                full_name = (entity.get('full_name') or '').strip().lower()

                candidates = {entity_name, full_name}
                if seed in candidates or seed == re.sub(r'[^a-z0-9]+', '', entity_name) or seed == re.sub(r'[^a-z0-9]+', '', full_name):
                    if entity_name:
                        terms.append(entity_name)
                    if full_name:
                        terms.append(full_name)
                        terms.append(re.sub(r'\s+', ' ', full_name))

                        compact = re.sub(r'[^a-z0-9]+', '', full_name)
                        snake_case = re.sub(r'[^a-z0-9]+', '_', full_name).strip('_')
                        if compact:
                            terms.append(compact)
                            terms.append(f'@{compact}')
                        if snake_case:
                            terms.append(snake_case)
                            terms.append(f'@{snake_case}')

                    break

        return terms

    def _extract_brightdata_items(self, payload) -> List[Dict]:
        if isinstance(payload, list):
            return payload
        if not isinstance(payload, dict):
            return []

        for key in ('data', 'results', 'items', 'records'):
            value = payload.get(key)
            if isinstance(value, list):
                return value

        if isinstance(payload.get('data'), dict):
            nested = payload.get('data')
            for key in ('results', 'items', 'records'):
                value = nested.get(key)
                if isinstance(value, list):
                    return value

        # Some dataset calls return a single record object directly.
        if any(key in payload for key in ('id', 'url', 'description', 'text', 'full_text', 'date_posted', 'created_at')):
            return [payload]

        return []

    def _normalize_input_urls(self, input_items: Optional[List[Dict]]) -> List[str]:
        urls: List[str] = []
        for item in input_items or []:
            if not isinstance(item, dict):
                continue
            url = (item.get('url') or '').strip()
            if url:
                urls.append(url)
        return urls

    def _extract_x_username_from_url(self, url: str) -> str:
        match = re.match(r'^https?://(?:www\.)?(?:x|twitter)\.com/([^/]+)/?.*$', (url or '').strip(), re.IGNORECASE)
        if not match:
            return ''
        username = (match.group(1) or '').strip()
        if not username or username.lower() in ('i', 'search', 'home', 'explore'):
            return ''
        return username

    def _is_status_url(self, url: str) -> bool:
        return bool(re.search(r'/(?:status|statuses)/\d+', (url or '').strip(), re.IGNORECASE))

    def _parse_brightdata_response(self, response: requests.Response):
        try:
            return response.json()
        except json.JSONDecodeError:
            # Bright Data dataset scrape may return NDJSON (one JSON object per line).
            items: List[Dict] = []
            for line in (response.text or '').splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    items.append(obj)

            if items:
                return items

            raise RuntimeError('Bright Data response is not valid JSON or NDJSON')

    def _value(self, obj, *keys, default=None):
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                value = obj.get(key)
            elif hasattr(obj, key):
                value = getattr(obj, key)
            else:
                continue

            if callable(value):
                try:
                    value = value()
                except Exception:
                    continue

            if value is not None:
                return value
        return default

    def _normalize_twikit_tweet(self, tweet, active_query: str, fetched_at: str) -> Dict:
        user = self._value(tweet, 'user', default={}) or {}

        tweet_id = str(self._value(tweet, 'id', 'tweet_id', default='') or '')
        author_username = self._value(user, 'screen_name', 'username', default='') or ''
        author_name = self._value(user, 'name', default='') or ''
        author_id = str(self._value(user, 'id', 'user_id', default='') or '')
        post_url = self._value(tweet, 'url', default='') or ''
        if not post_url and tweet_id and author_username:
            post_url = f'https://x.com/{author_username}/status/{tweet_id}'

        hashtags = self._value(tweet, 'hashtags', default=[])
        if not isinstance(hashtags, list):
            hashtags = []

        return {
            'source': 'x',
            'provider': 'twikit',
            'source_post_id': tweet_id,
            'post_url': post_url,
            'author_id': author_id,
            'author_username': author_username,
            'author_name': author_name,
            'created_at_utc': str(self._value(tweet, 'created_at', default='') or ''),
            'text_raw': str(self._value(tweet, 'full_text', 'text', default='') or ''),
            'language': str(self._value(tweet, 'lang', default='') or ''),
            'hashtags': hashtags,
            'public_metrics': {
                'reply_count': int(self._value(tweet, 'reply_count', default=0) or 0),
                'retweet_count': int(self._value(tweet, 'retweet_count', default=0) or 0),
                'like_count': int(self._value(tweet, 'favorite_count', 'like_count', default=0) or 0),
                'quote_count': int(self._value(tweet, 'quote_count', default=0) or 0)
            },
            'query_used': active_query,
            'fetched_at_utc': fetched_at,
            'raw_item': tweet if isinstance(tweet, dict) else {}
        }

    async def _collect_twikit_posts_async(self, query: str, max_results: int) -> Dict:
        if TwikitClient is None:
            raise RuntimeError('Twikit is not installed. Install it with: pip install twikit')

        try:
            client = TwikitClient(self.twikit_language)
        except TypeError:
            client = TwikitClient(language=self.twikit_language)

        cookies_path = (self.twikit_cookies_path or '').strip() or 'data/twikit_cookies.json'
        username = (self.twikit_username or '').strip()
        password = (self.twikit_password or '').strip()
        email = (self.twikit_email or '').strip()

        if not username or not password:
            raise RuntimeError(
                'Twikit requires TWIKIT_USERNAME and TWIKIT_PASSWORD. '
                'Set TWIKIT_EMAIL when your account requires it.'
            )

        os.makedirs(os.path.dirname(cookies_path), exist_ok=True)
        login_kwargs = {
            'auth_info_1': username,
            'password': password,
            'cookies_file': cookies_path,
            'enable_ui_metrics': self.twikit_enable_ui_metrics
        }
        if email:
            login_kwargs['auth_info_2'] = email

        # Twikit handles cookie reuse when cookies_file exists.
        await client.login(**login_kwargs)

        safe_max = max(10, min(int(max_results), 100))
        active_query = (query or '').strip() or self._build_default_query()

        tweets_page = await client.search_tweet(active_query, 'Latest')

        tweets = []
        try:
            tweets.extend(list(tweets_page))
        except Exception:
            pass

        # Try paginating when the result wrapper supports it.
        while len(tweets) < safe_max:
            next_page = None
            if hasattr(tweets_page, 'next'):
                next_page = await tweets_page.next()
            elif hasattr(tweets_page, 'get_next_page'):
                next_page = await tweets_page.get_next_page()

            if not next_page:
                break

            tweets_page = next_page
            try:
                tweets.extend(list(tweets_page))
            except Exception:
                break

        tweets = tweets[:safe_max]
        fetched_at = datetime.utcnow().isoformat()
        normalized_records = [self._normalize_twikit_tweet(tweet, active_query, fetched_at) for tweet in tweets]

        return {
            'source': 'x',
            'provider': 'twikit',
            'query': active_query,
            'count': len(normalized_records),
            'records': normalized_records,
            'meta': {
                'collection_mode': 'query_search',
                'raw_result_count': len(tweets),
                'normalized_with_text_count': sum(1 for r in normalized_records if r.get('text_raw')),
                'normalized_with_author_count': sum(1 for r in normalized_records if r.get('author_username')),
                'normalized_with_date_count': sum(1 for r in normalized_records if r.get('created_at_utc')),
                'normalized_with_url_count': sum(1 for r in normalized_records if r.get('post_url'))
            }
        }

    def collect_twikit_posts(self, query: Optional[str] = None, max_results: int = 20) -> Dict:
        active_query = (query or '').strip() or self._build_default_query()

        try:
            return asyncio.run(self._collect_twikit_posts_async(active_query, max_results))
        except RuntimeError as exc:
            if 'asyncio.run() cannot be called from a running event loop' not in str(exc):
                raise

            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._collect_twikit_posts_async(active_query, max_results))
            finally:
                loop.close()
        except Exception as exc:
            message = str(exc)
            if 'KEY_BYTE' in message or "Couldn't get KEY_BYTE indices" in message:
                raise RuntimeError(
                    'Twikit failed because X changed anti-bot transaction scripts (KEY_BYTE parse error). '
                    'This is an upstream Twikit breakage. Use provider="apify" for search collection for now, '
                    'or retry Twikit after a library update that fixes the transaction parser.'
                ) from exc
            raise

    def _extract_apify_items(self, payload) -> List[Dict]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            if isinstance(payload.get('items'), list):
                return [item for item in payload.get('items') if isinstance(item, dict)]
            return [payload]
        return []

    def _normalize_apify_record(self, item: Dict, active_query: str, fetched_at: str) -> Dict:
        author = item.get('author') if isinstance(item.get('author'), dict) else {}
        user = item.get('user') if isinstance(item.get('user'), dict) else {}

        text_raw = (
            item.get('text')
            or item.get('fullText')
            or item.get('full_text')
            or item.get('content')
            or item.get('description')
            or ''
        )

        public_metrics = item.get('public_metrics') or {
            'reply_count': item.get('replyCount') or item.get('replies') or 0,
            'retweet_count': item.get('retweetCount') or item.get('reposts') or 0,
            'like_count': item.get('likeCount') or item.get('likes') or 0,
            'quote_count': item.get('quoteCount') or item.get('quotes') or 0
        }

        return {
            'source': 'x',
            'provider': 'apify',
            'source_post_id': str(item.get('id') or item.get('tweetId') or item.get('postId') or ''),
            'post_url': item.get('url') or item.get('twitterUrl') or '',
            'author_id': item.get('authorId') or author.get('id') or user.get('id') or '',
            'author_username': (
                item.get('username')
                or author.get('userName')
                or author.get('username')
                or user.get('username')
                or user.get('screen_name')
                or ''
            ),
            'author_name': item.get('name') or author.get('name') or user.get('name') or '',
            'created_at_utc': item.get('createdAt') or item.get('created_at') or item.get('date') or '',
            'text_raw': text_raw,
            'language': item.get('lang') or item.get('language') or '',
            'hashtags': item.get('hashtags') or [],
            'public_metrics': public_metrics,
            'query_used': active_query,
            'fetched_at_utc': fetched_at,
            'raw_item': item
        }

    def collect_apify_posts(
        self,
        query: Optional[str] = None,
        max_results: int = 20,
        input_items: Optional[List[Dict]] = None,
        extra_params: Optional[Dict] = None,
        actor_input: Optional[Dict] = None
    ) -> Dict:
        token = self._normalized_apify_token()
        if not token:
            raise RuntimeError('APIFY_API_TOKEN is required for Apify collection')

        params = dict(extra_params or {})
        actor_id = (params.pop('actor_id', None) or self.apify_actor_id or '').strip()
        if not actor_id:
            raise RuntimeError('APIFY_ACTOR_ID (or request_params.actor_id) is required for Apify collection')

        safe_max = max(10, min(int(max_results), 100))
        active_query = (query or '').strip() or self._build_default_query()

        run_input = dict(actor_input or {})
        if not run_input:
            run_input['maxItems'] = safe_max
            run_input['searchTerms'] = [active_query]

            start_urls = [
                {'url': item.get('url').strip()}
                for item in (input_items or [])
                if isinstance(item, dict) and (item.get('url') or '').strip()
            ]
            if start_urls:
                run_input['startUrls'] = start_urls

        run_url = self.APIFY_RUNS_URL_TEMPLATE.format(actor_id=actor_id)
        run_params = {
            'token': token,
            'waitForFinish': str(Config.APIFY_WAIT_FOR_FINISH_SECONDS)
        }

        run_response = requests.post(
            run_url,
            params=run_params,
            json=run_input,
            timeout=Config.APIFY_TIMEOUT_SECONDS
        )
        if run_response.status_code >= 400:
            raise RuntimeError(f'Apify run failed: {run_response.status_code} {run_response.text}')

        run_payload = run_response.json() or {}
        run_data = run_payload.get('data', {}) if isinstance(run_payload, dict) else {}
        dataset_id = run_data.get('defaultDatasetId')
        if not dataset_id:
            raise RuntimeError('Apify run completed without defaultDatasetId')

        items_url = self.APIFY_DATASET_ITEMS_URL_TEMPLATE.format(dataset_id=dataset_id)
        items_response = requests.get(
            items_url,
            params={'token': token, 'clean': 'true', 'format': 'json'},
            timeout=Config.APIFY_TIMEOUT_SECONDS
        )
        if items_response.status_code >= 400:
            raise RuntimeError(f'Apify dataset read failed: {items_response.status_code} {items_response.text}')

        payload = items_response.json()
        records = self._extract_apify_items(payload)
        fetched_at = datetime.utcnow().isoformat()
        normalized_records = [self._normalize_apify_record(item, active_query, fetched_at) for item in records]

        return {
            'source': 'x',
            'provider': 'apify',
            'query': active_query,
            'count': len(normalized_records),
            'records': normalized_records,
            'meta': {
                'collection_mode': 'query_search',
                'actor_id': actor_id,
                'apify_dataset_id': dataset_id,
                'raw_result_count': len(records),
                'collector_url': run_url,
                'request_params': params,
                'run_input': run_input
            }
        }

    def collect_brightdata_posts(
        self,
        query: Optional[str] = None,
        max_results: int = 20,
        input_items: Optional[List[Dict]] = None,
        extra_params: Optional[Dict] = None,
        seed_entity: Optional[str] = None,
        focus_terms: Optional[List[str]] = None
    ) -> Dict:
        token = self._normalized_brightdata_token()
        if not token:
            raise RuntimeError('BRIGHTDATA_API_TOKEN is required for Bright Data collection')
        if not self.brightdata_collector_url:
            raise RuntimeError('BRIGHTDATA_COLLECTOR_URL is required for Bright Data collection')

        safe_max = max(10, min(int(max_results), 100))
        active_query = (query or '').strip()
        if not active_query:
            active_query = 'input_urls'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        dataset_mode = '/datasets/' in (self.brightdata_collector_url or '')
        collection_mode = 'input_urls'
        base_input_urls = self._normalize_input_urls(input_items)
        if not base_input_urls:
            raise RuntimeError(
                'Bright Data collection is URL-driven for this setup. Provide input as a list of X status URLs.'
            )

        invalid_urls = [url for url in base_input_urls if not self._is_status_url(url)]
        if invalid_urls:
            raise RuntimeError(
                'Only X status URLs are supported in input for this Bright Data dataset. '
                f'Invalid example: {invalid_urls[0]}'
            )

        body = {'input': [{'url': url} for url in base_input_urls]}

        request_params = extra_params or {}

        response = requests.post(
            self.brightdata_collector_url,
            headers=headers,
            params=request_params,
            json=body,
            timeout=Config.BRIGHTDATA_TIMEOUT_SECONDS
        )

        if response.status_code >= 400:
            raise RuntimeError(f'Bright Data request failed: {response.status_code} {response.text}')

        payload = self._parse_brightdata_response(response)
        records = self._extract_brightdata_items(payload)
        fetched_at = datetime.utcnow().isoformat()

        normalized_records: List[Dict] = []
        for item in records:
            if not isinstance(item, dict):
                continue

            text_raw = (
                item.get('text')
                or item.get('full_text')
                or item.get('content')
                or item.get('description')
                or ''
            )
            source_post_id = item.get('id') or item.get('tweet_id') or item.get('post_id') or ''
            author = item.get('author') if isinstance(item.get('author'), dict) else {}

            normalized_records.append(
                {
                    'source': 'x',
                    'provider': 'brightdata',
                    'source_post_id': str(source_post_id),
                    'post_url': item.get('url') or '',
                    'author_id': item.get('author_id') or author.get('id') or '',
                    'author_username': item.get('username') or item.get('user_posted') or author.get('username') or '',
                    'author_name': item.get('name') or author.get('name') or '',
                    'created_at_utc': item.get('created_at') or item.get('date') or item.get('date_posted') or '',
                    'text_raw': text_raw,
                    'language': item.get('lang') or item.get('language') or '',
                    'hashtags': item.get('hashtags') or [],
                    'public_metrics': item.get('public_metrics') or {
                        'reply_count': item.get('replies', 0),
                        'retweet_count': item.get('reposts', 0),
                        'like_count': item.get('likes', 0),
                        'quote_count': item.get('quotes', 0)
                    },
                    'query_used': active_query,
                    'fetched_at_utc': fetched_at,
                    'raw_item': item
                }
            )

        return {
            'source': 'x',
            'provider': 'brightdata',
            'query': active_query,
            'count': len(normalized_records),
            'records': normalized_records,
            'meta': {
                'collection_mode': collection_mode,
                'dataset_mode': dataset_mode,
                'input_url_count': len(base_input_urls),
                'expanded_input_url_count': len(base_input_urls),
                'raw_result_count': len(records),
                'normalized_with_text_count': sum(1 for r in normalized_records if r.get('text_raw')),
                'normalized_with_author_count': sum(1 for r in normalized_records if r.get('author_username') or r.get('author_name')),
                'normalized_with_date_count': sum(1 for r in normalized_records if r.get('created_at_utc')),
                'normalized_with_url_count': sum(1 for r in normalized_records if r.get('post_url')),
                'collector_url': self.brightdata_collector_url,
                'request_params': request_params,
                'raw_payload': payload if not normalized_records else None
            }
        }

    def collect_posts(
        self,
        provider: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 20,
        input_items: Optional[List[Dict]] = None,
        extra_params: Optional[Dict] = None,
        seed_entity: Optional[str] = None,
        focus_terms: Optional[List[str]] = None,
        actor_input: Optional[Dict] = None
    ) -> Dict:
        chosen = (provider or self.provider_default or 'brightdata').strip().lower()

        if chosen in ('brightdata', 'bright_data'):
            return self.collect_brightdata_posts(
                query=query,
                max_results=max_results,
                input_items=input_items,
                extra_params=extra_params,
                seed_entity=seed_entity,
                focus_terms=focus_terms
            )

        if chosen in ('apify',):
            return self.collect_apify_posts(
                query=query,
                max_results=max_results,
                input_items=input_items,
                extra_params=extra_params,
                actor_input=actor_input
            )

        if chosen in ('twikit',):
            return self.collect_twikit_posts(query=query, max_results=max_results)

        raise RuntimeError(f'Unsupported social provider: {chosen}. Use brightdata, apify, or twikit.')

    def get_default_search_terms(self) -> List[str]:
        return self._build_dynamic_search_terms()


social_collector_service = SocialCollectorService()