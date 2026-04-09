# Current Application Capabilities

This document is slide-ready and describes what the current project can do today.

## 1. Core Product Capability
- Analyze English text sentiment through a Flask API.
- Return one of three labels: `positive`, `neutral`, `negative`.
- Provide a confidence score and model metadata for each analysis.

## 2. Sentiment Inference Pipeline
- Primary inference uses transformer model: `cardiffnlp/twitter-roberta-base-sentiment-latest`.
- If transformer loading/inference fails, backend falls back to keyword-based sentiment scoring.
- Fallback mode still returns a valid response (`sentiment`, `confidence`, `model_used=basic`).

## 3. Political Context Enrichment
- Matches curated political lexicon terms in the analyzed text.
- Returns exact matched terms with location metadata (`start`, `end`) and stored meaning.
- Extracts sentiment trigger words from static positive/negative trigger sets for UI explainability.

## 4. Dynamic Lexicon Management
- Add new lexicon words via API without restarting the backend.
- Search lexicon by word/meaning and optionally by category.
- Fetch category-level statistics and metadata (total words, last update, recent additions).
- Supported categories include: `political`, `positive`, `negative`, `common_words`, `botswana_specific`.

## 5. Dynamic Political Entity Management (New)
- Political entities are now stored in SQLite, not hardcoded in service code.
- API supports listing entities, adding entities, and deleting entities.
- Sentiment analysis reads entities from database each request, so newly added entities are immediately available.
- Entity matching supports both short label (`entity`) and optional `full_name`.

## 6. Persistence Layer
- Lexicon data is persisted as JSON file in `backend/data/setswana_lexicon.json`.
- Political entities are persisted in SQLite DB at `backend/data/political_entities.db`.
- Database path can be overridden via `POLITICAL_ENTITY_DB_PATH` environment variable.

## 7. Backend API Surface
- `GET /` service metadata and endpoint summary.
- `GET /api/health` health check.
- `POST /api/sentiment/analyze` sentiment and political context analysis.
- `GET /api/sentiment/test-examples` canned sample texts.
- `GET /api/lexicon/stats` lexicon statistics.
- `GET /api/lexicon/search?q=...` lexicon search.
- `POST /api/lexicon/add` add lexicon entry.
- `GET /api/lexicon/health` lexicon service health.
- `GET /api/entities/` list political entities.
- `POST /api/entities/add` add political entity.
- `DELETE /api/entities/<id>` delete political entity.
- `GET /api/entities/health` political entity service health.

## 8. Frontend Capability
- React + TypeScript single-page interface.
- Manual analyzer form with quick sample text testing.
- Result panel showing sentiment, confidence, matched lexicon terms, trigger words, and political entities.
- Lexicon manager for searching and adding words.
- Political entity manager for adding and deleting database entities.
- Startup backend health indicator.

## 9. Operational Characteristics
- CORS enabled for frontend-backend local communication.
- No background job system required for core analysis flow.
- Minimal deployment path supported (Flask + static frontend build).

## 10. Current Constraints
- Input pipeline currently assumes English-focused sentiment model.
- No authentication or role-based permissions on management endpoints.
- No rate limiting or audit trail on entity/lexicon modifications.
- Automated test coverage is minimal in the current repository state.
