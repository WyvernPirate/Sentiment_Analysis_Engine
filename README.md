# Botswana Political Sentiment Analysis Engine

A modular platform for analyzing political discourse in Botswana, supporting both English and Setswana linguistic contexts.

## Project Structure

```
.
├── backend/                # Flask API & Sentiment Engine
│   ├── app.py              # Main Entry Point
│   ├── routes/             # API Blueprints
│   ├── services/           # Core Business Logic
│   └── data/               # Local SQLite & JSON storage
├── frontend/               # React Dashboard (Material Design 3)
│   ├── src/pages/          # Main Dashboard Views
│   ├── src/components/     # Reusable UI Components
│   └── src/services/       # API Integration Layer
├── docs/                   # System Documentation
└── data/                   # Shared Data & Samples
```

## Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```
The API will be available at `http://localhost:5000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```
The dashboard will open at `http://localhost:3000`.

## Core Features
- **Linguistic Context**: Enhanced analysis for Botswana political terms.
- **Dynamic Lexicon**: Manage the political word pool via the UI.
- **Data Collection**: Integrated social media collection (X, Facebook) and CSV ingest.
- **Batch Analysis**: Process large datasets and view aggregate trends.
- **Entity Tracking**: Database-backed management of political figures and parties.

## Documentation
- [DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md): Local setup and testing.
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md): Production deployment tips.
- [CURRENT_CAPABILITIES.md](docs/CURRENT_CAPABILITIES.md): Feature roadmap and status.

---
**BW_REGION_ALPHA | Sentiment Analysis Engine v1.0.0**
