# Botswana Political Sentiment Analysis Engine

[![Backend CI](https://github.com/WyvernPirate/Sentiment_Analysis_Engine/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/WyvernPirate/Sentiment_Analysis_Engine/actions/workflows/backend-ci.yml)

A full-stack platform for analyzing political discourse in Botswana, with language-aware
sentiment analysis across English and Setswana (including code-switched text), political
entity tracking, and social-media data collection.

## Core Features

- **Language-aware sentiment analysis**: text is classified as English, Setswana, or
  Setswana-English (code-switched) by measuring Setswana lexicon coverage, then routed to
  the appropriate model — English text to `cardiffnlp/twitter-roberta-base-sentiment-latest`,
  Setswana/code-switched text to the multilingual `cardiffnlp/twitter-xlm-roberta-base-sentiment-latest`,
  blended with a lexicon polarity signal. See `backend/services/sentiment_service.py`.
- **Dynamic Setswana lexicon**: a hand-curated word list (94 words across 5 categories),
  editable via the UI with changes applied immediately, no restart required.
- **Political entity tracking**: SQLAlchemy-backed CRUD for parties, leaders, and locations,
  with real mention-count/net-sentiment/risk aggregation computed from analysis history
  (`GET /api/entities/stats`) — not placeholder numbers.
- **Batch analysis**: CSV upload or social-media collection → cleaning → language-routed
  sentiment analysis → persisted job with per-row detail and aggregate stats.
- **Social data collection**: three working collectors (Bright Data, Apify, Twikit) plus
  CSV upload, all normalizing into the same record schema.
- **System diagnostics**: live checks (database reachable, lexicon populated, sentiment
  engine available, storage writable) instead of a static status page.

## What's Real vs. What's Not

Written for anyone (a reviewer, a future contributor, future me) who wants to know what
actually works versus what's aspirational, without having to read the source to find out.

**Solid / genuinely working:**
- The language routing described above is real — it's not a hardcoded label, it's an
  actual `detect_language()` classifier feeding actual model selection, verified with
  automated tests (`backend/tests/test_sentiment_routing.py`).
- The data layer is a real SQLAlchemy schema with Alembic migrations (`backend/migrations/`),
  not flat files or ad hoc SQL. A fresh clone auto-migrates and seeds on first run.
- Bright Data, Apify, and Twikit integrations make real HTTP calls / use a real
  authenticated client — they are not stubs, though Twikit in particular is fragile
  against X's anti-bot measures (see comments in `social_collector_service.py`).
- 41 backend tests + a frontend test run in CI on every push
  (`.github/workflows/backend-ci.yml`).

**Known limitations, stated plainly:**
- The Setswana lexicon is hand-curated (94 words), not corpus-derived — coverage of real
  political discourse is necessarily partial. It hasn't been fine-tuned on labeled Setswana
  data; the routing + lexicon-blend approach was chosen specifically because it requires no
  training data and is honestly scoped for what a solo project can validate.
- The single-text analyzer's word-importance highlighting (Leave-One-Out trigger words)
  still runs against the English model only, regardless of detected language — a stated
  scope boundary, not a bug.
- Facebook collection was never implemented and its config has been removed rather than
  left as a dead placeholder.
- This is a demo/portfolio-scoped project, not hardened for production traffic: no
  authentication on any endpoint, and social-provider secrets are read from `.env` with
  no secrets-manager integration.

## Architecture

```
.
├── backend/                 # Flask API
│   ├── app.py                # Entry point; runs migrations + seeding on startup
│   ├── models.py              # SQLAlchemy models (entities, lexicon, jobs, collections)
│   ├── migrations/            # Alembic schema history
│   ├── routes/                 # API blueprints (sentiment, lexicon, entities, social, analysis, system)
│   ├── services/                # Business logic — sentiment routing, lexicon, collectors, cleaning
│   └── tests/                    # pytest suite (see backend/tests/conftest.py for fixtures)
├── frontend/                # React 19 + TypeScript dashboard
│   ├── src/pages/             # Top-level views, one per route
│   ├── src/components/         # Shared UI (layout chrome, word cloud)
│   ├── src/services/            # sentimentApi.ts — the one typed API client
│   └── src/types/                 # Shared TypeScript types mirroring backend responses
├── .github/workflows/       # CI
└── docs/                     # Setup and deployment guides
```

Backend: Flask, SQLAlchemy + Flask-Migrate, HuggingFace Transformers, SQLite.
Frontend: React 19, TypeScript, Tailwind CSS, React Query, Recharts, React Router.

## Quick Start

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```
This automatically runs database migrations and seeds baseline lexicon/entity data on
first run — no separate setup step needed. The API is available at `http://localhost:5000`.

### 2. Frontend
```bash
cd frontend
npm install
npm start
```
The dashboard opens at `http://localhost:3000`.

### Running the tests
```bash
# Backend (from backend/, after installing requirements.txt + requirements-dev.txt)
pytest

# Frontend (from frontend/)
npm test
```
The backend suite stubs the sentiment-analysis pipelines, so it runs without needing
`transformers`/`torch` importable — see `backend/tests/conftest.py`.

## Documentation
- [DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md): Local setup, endpoints, environment variables, troubleshooting.
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md): Production deployment notes.
- [CURRENT_CAPABILITIES.md](docs/CURRENT_CAPABILITIES.md): Feature-by-feature status.

---
**BW_REGION_ALPHA | Sentiment Analysis Engine v1.0.0**
