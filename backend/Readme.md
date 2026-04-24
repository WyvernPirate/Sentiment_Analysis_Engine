# Backend Service

This backend is a Flask API for sentiment analysis and political text enrichment.

## What It Does
- Analyzes English text sentiment (`positive`, `neutral`, `negative`).
- Matches user-managed political lexicon terms.
- Extracts political entities from a SQLite-backed entity table.
- Supports runtime lexicon and entity updates without restart.

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

## Persistence
- Lexicon JSON: `backend/data/setswana_lexicon.json`
- Entity DB (SQLite): `backend/data/political_entities.db`
