# Backend Service

This backend is a Flask API for sentiment analysis and political text enrichment.

## What It Does
- Analyzes English text sentiment (`positive`, `neutral`, `negative`).
- Matches user-managed political lexicon terms.
- Extracts political entities from a SQLite-backed entity table.
- Supports runtime lexicon and entity updates without restart.
- Collects political posts from X via approved API access.
- Stores raw batches and runs a deterministic cleaning step.

## Local Run
```bash
cd backend
python -m venv .venv_local
.venv_local/bin/pip install -r requirements.txt
.venv_local/bin/python app.py
```

## API Endpoints
- `GET /api/health`
- `POST /api/sentiment/analyze`
- `GET /api/sentiment/test-examples`
- `GET /api/lexicon/stats`
- `GET /api/lexicon/search?q=...`
- `POST /api/lexicon/add`
- `GET /api/lexicon/health`
- `GET /api/entities/`
- `POST /api/entities/add`
- `DELETE /api/entities/<id>`
- `GET /api/entities/health`
- `GET /api/social/health`
- `POST /api/social/collect`
- `GET /api/social/collections`
- `POST /api/social/clean`

## Social Data Collection (X)
Use approved X API credentials with bearer-token auth. Scraping workarounds are not supported.

Backend `.env` entries:
```bash
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret

# Optional provider switch
SOCIAL_PROVIDER=x_api

# Bright Data provider settings
BRIGHTDATA_API_TOKEN=your-brightdata-token
BRIGHTDATA_COLLECTOR_URL=https://api.brightdata.com/your-collector-endpoint
BRIGHTDATA_TIMEOUT_SECONDS=60
```

Collect recent political posts:
```bash
curl -X POST http://localhost:5000/api/social/collect \
	-H "Content-Type: application/json" \
	-d '{"provider": "x_api", "query": "(botswana politics OR #BotswanaPolitics) -is:retweet", "max_results": 20}'
```

Collect via Bright Data provider:
```bash
curl -X POST http://localhost:5000/api/social/collect \
	-H "Content-Type: application/json" \
	-d '{"provider": "brightdata", "query": "(botswana politics OR #BotswanaPolitics)", "max_results": 20}'
```

Bright Data dataset scrape with explicit input URLs (matches Bright Data dataset API style):
```bash
curl -X POST http://localhost:5000/api/social/collect \
	-H "Content-Type: application/json" \
	-d '{
		"provider": "brightdata",
		"input": [
			{"url": "https://x.com/FabrizioRomano/status/1683559267524136962"},
			{"url": "https://x.com/CNN/status/1796673270344810776"}
		],
		"request_params": {
			"dataset_id": "your-dataset-id",
			"notify": "false",
			"include_errors": "true"
		}
	}'
```

Clean a collected batch:
```bash
curl -X POST http://localhost:5000/api/social/clean \
	-H "Content-Type: application/json" \
	-d '{"collection_id": "x-20260424T120000Z"}'
```

## Persistence
- Lexicon JSON: `backend/data/setswana_lexicon.json`
- Entity DB (SQLite): `backend/data/political_entities.db`
- Raw social data: `backend/data/raw_social_data/`
- Cleaned social data: `backend/data/cleaned_social_data/`
