# Development Guide

## Prerequisites
- Python 3.10+
- Node/npm installed for frontend

## 1) Backend setup and run
```bash
cd backend
python -m venv .venv_local
.venv_local/bin/pip install -r requirements.txt
.venv_local/bin/python app.py
```

Health check:
```bash
curl http://localhost:5000/api/health
```

## 2) Frontend setup and run
```bash
cd frontend
npm install
npm start
```
Frontend default URL: `http://localhost:3000`

## Frontend-connected endpoints
- `GET /api/health`
- `POST /api/sentiment/analyze`
- `GET /api/sentiment/test-examples`
- `GET /api/lexicon/stats`
- `GET /api/lexicon/search`
- `POST /api/lexicon/add`
- `GET /api/lexicon/health`
- `GET /api/entities/`
- `POST /api/entities/add`
- `DELETE /api/entities/<id>`
- `GET /api/entities/health`
- `GET /api/social/health`
- `GET /api/social/auth-diagnose`
- `POST /api/social/collect`
- `GET /api/social/collections`
- `POST /api/social/clean`

## Environment variables
Frontend (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:5000
```

Backend (`backend/.env`):
```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite:///botswana_sentiment.db
POLITICAL_ENTITY_DB_PATH=data/political_entities.db
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
SOCIAL_PROVIDER=x_api
BRIGHTDATA_API_TOKEN=your-brightdata-token
BRIGHTDATA_COLLECTOR_URL=https://api.brightdata.com/your-collector-endpoint
BRIGHTDATA_TIMEOUT_SECONDS=60
```

## 3) Social data pipeline (X first)
The first implementation slice uses approved X API access for recent keyword search, stores raw batches, then cleans them.

Collect data:
```bash
curl -X POST http://localhost:5000/api/social/collect \
  -H "Content-Type: application/json" \
  -d '{"provider": "x_api", "query": "(botswana politics OR #BotswanaPolitics) -is:retweet", "max_results": 20}'
```

Collect data with Bright Data provider:
```bash
curl -X POST http://localhost:5000/api/social/collect \
  -H "Content-Type: application/json" \
  -d '{"provider": "brightdata", "query": "(botswana politics OR #BotswanaPolitics)", "max_results": 20}'
```

Collect Bright Data dataset items by passing explicit `input` URLs and dataset query params:
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

List collected batches:
```bash
curl "http://localhost:5000/api/social/collections?limit=5"
```

Clean a specific batch (replace collection id):
```bash
curl -X POST http://localhost:5000/api/social/clean \
  -H "Content-Type: application/json" \
  -d '{"collection_id": "x-20260424T120000Z"}'
```

## Troubleshooting
- **`ModuleNotFoundError: app`**: run backend from `backend/` or use full path to `backend/app.py`.
- **Port 5000 in use**:
  ```bash
  lsof -i :5000 -P -n | awk 'NR>1 {print $2}' | xargs -r kill
  ```
- **Model download SSL/network failures**: app should still run using fallback behavior; `/api/health` should remain `healthy`.
- **`externally-managed-environment` during `pip install`**: use a virtual environment (`python -m venv .venv_local`) and install with `.venv_local/bin/pip`.
- **`/api/social/collect` returns 401 Unauthorized**:
  1. Run `curl http://localhost:5000/api/social/auth-diagnose`.
  2. Ensure `TWITTER_BEARER_TOKEN` is in `backend/.env` (not only `.env.example`).
  3. Confirm token belongs to the same app/project with X API v2 access.
  4. Restart backend after `.env` changes.
