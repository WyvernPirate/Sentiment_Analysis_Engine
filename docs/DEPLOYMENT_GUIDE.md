# Deployment Guide

## Runtime model
- Backend service: Flask app from `backend/app.py`
- Frontend service: React build from `frontend/`

## Backend production example (gunicorn)
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Frontend production build
```bash
cd frontend
npm install
npm run build
```
Serve `frontend/build/` using nginx or another static host.

## Required config
Backend env (example):
```bash
SECRET_KEY=replace-this
DATABASE_URL=sqlite:///botswana_sentiment.db
POLITICAL_ENTITY_DB_PATH=data/political_entities.db
FLASK_ENV=production
```

Frontend env (example):
```bash
REACT_APP_API_URL=https://your-backend-host
```

## Operational checks
- `GET /api/health` should return `status: healthy`
- `GET /api/lexicon/health` should return `status: healthy`
- `GET /api/entities/health` should return `status: healthy`
- `POST /api/sentiment/analyze` should return sentiment payload and not error

## Notes
- `data/political_entities.db` is auto-created on first backend start.
- Use `app.py` as the single backend entrypoint.
