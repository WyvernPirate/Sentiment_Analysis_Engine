# Development Guide

## Prerequisites
- Python environment available at project `.venv`
- Node/npm installed for frontend

## 1) Start backend
```bash
cd backend
python app.py
```
Health check:
```bash
curl http://localhost:5000/api/health
```

## 2) Start frontend
```bash
cd frontend
npm install
npm start
```
Frontend default URL: `http://localhost:3000`

## 3) Backend refresh flow (dashboard data)
The API no longer blocks on implicit data collection during reads. Use explicit refresh:
```bash
curl -X POST http://localhost:5000/api/dashboard/refresh
```

## Frontend-connected endpoints
- `GET /api/health`
- `POST /api/sentiment/analyze`
- `GET /api/sentiment/test-examples`
- `GET /api/dashboard/overview`
- `GET /api/dashboard/trends`
- `GET /api/dashboard/political-entities`
- `GET /api/dashboard/analytics`
- `GET /api/dashboard/real-time-stats`
- `POST /api/dashboard/refresh`
- `GET /api/lexicon/stats`
- `GET /api/lexicon/search`
- `POST /api/lexicon/add`
- `POST /api/lexicon/suggest`
- `GET /api/lexicon/health`
- `GET /api/training/stats`
- `POST /api/training/quick-retrain`
- `POST /api/training/export`

## Environment variables
Frontend (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:5000
```

Backend (`backend/.env`):
```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite:///botswana_sentiment.db
```

## Troubleshooting
- **`ModuleNotFoundError: app`**: run backend from `backend/` or use full path to `backend/app.py`.
- **Port 5000 in use**:
  ```bash
  lsof -i :5000 -P -n | awk 'NR>1 {print $2}' | xargs -r kill
  ```
- **Model download SSL/network failures**: app should still run using fallback behavior; `/api/health` should remain `healthy`.
