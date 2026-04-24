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
```

## Troubleshooting
- **`ModuleNotFoundError: app`**: run backend from `backend/` or use full path to `backend/app.py`.
- **Port 5000 in use**:
  ```bash
  lsof -i :5000 -P -n | awk 'NR>1 {print $2}' | xargs -r kill
  ```
- **Model download SSL/network failures**: app should still run using fallback behavior; `/api/health` should remain `healthy`.
- **`externally-managed-environment` during `pip install`**: use a virtual environment (`python -m venv .venv_local`) and install with `.venv_local/bin/pip`.
