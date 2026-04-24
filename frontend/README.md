# Frontend (React + TypeScript)

## Overview
This UI provides:
- text sentiment analysis
- lexicon management
- political entity management (database-backed)

## Setup
```bash
cd frontend
npm install
npm start
```

Default URL: `http://localhost:3000`

## Backend URL
Optional `.env`:
```bash
REACT_APP_API_URL=http://localhost:5000/api
```

## Current UI Sections
- Analyzer: submit text and view sentiment output.
- Results: sentiment, confidence, model, matched words, trigger words, entities.
- Lexicon manager: search and add words.
- Entity manager: add and delete political entities persisted in SQLite.