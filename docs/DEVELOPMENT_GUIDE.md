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
- `GET /api/entities/stats`
- `POST /api/entities/add`
- `DELETE /api/entities/<id>`
- `GET /api/entities/health`
- `GET /api/social/health`
- `POST /api/social/collect`
- `POST /api/social/upload-csv`
- `GET /api/social/collections`
- `POST /api/social/clean`
- `POST /api/analysis/run`
- `GET /api/analysis/jobs`
- `GET /api/analysis/jobs/<job_id>`
- `GET /api/system/health`
- `GET /api/system/logs`
- `POST /api/system/event`

## Environment variables
Frontend (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:5000/api
```

Backend (`backend/.env`) — see `backend/.env.example` for the full, current list. The
social collection providers are Bright Data, Apify, and Twikit (`SOCIAL_PROVIDER` is
one of `brightdata`/`apify`/`twikit`) — there is no `x_api` provider or Twitter-branded
env vars; those were from an earlier design that was replaced. Facebook config was
removed entirely since it was never implemented. `DATABASE_URL` and `SECRET_KEY` are
the only Flask-level values most local setups need to override:
```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite:///botswana_sentiment.db
```

## 3) Social data pipeline
Three collection paths exist: CSV upload (works with no external account), Bright Data
(URL-driven dataset scrape), and Apify (free-text query search). Twikit is a fourth,
more fragile path using an authenticated X account — see `social_collector_service.py`
for its known breakage/fallback behavior. Collected batches are cleaned via `/api/social/clean`.

Upload a CSV (no provider credentials needed):
```bash
curl -X POST http://localhost:5000/api/social/upload-csv \
  -F "file=@your-data.csv"
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
  -d '{"collection_id": "x-20260424T120000Z", "filter_mode": "relaxed"}'
```

Use strict mode only after you have tuned the political pool:
```bash
curl -X POST http://localhost:5000/api/social/clean \
  -H "Content-Type: application/json" \
  -d '{"collection_id": "x-20260424T120000Z", "filter_mode": "strict"}'
```

## Troubleshooting
- **`ModuleNotFoundError: app`**: run backend from `backend/` or use full path to `backend/app.py`.
- **Port 5000 in use**:
  ```bash
  lsof -i :5000 -P -n | awk 'NR>1 {print $2}' | xargs -r kill
  ```
- **Model download SSL/network failures**: app should still run using fallback behavior; `/api/health` should remain `healthy`.
- **`externally-managed-environment` during `pip install`**: use a virtual environment (`python -m venv .venv_local`) and install with `.venv_local/bin/pip`.
- **`/api/social/collect` fails for a provider**: check `GET /api/social/health` — it reports which providers have credentials configured. Ensure the relevant `BRIGHTDATA_*`/`APIFY_*`/`TWIKIT_*` variables are in `backend/.env` (not only `.env.example`), then restart the backend.
- **Fresh clone has no database / lexicon / entities**: not needed as a manual step — `python app.py` runs migrations and seeds baseline data automatically on startup. `flask db upgrade` also works standalone if you prefer to run it explicitly.
