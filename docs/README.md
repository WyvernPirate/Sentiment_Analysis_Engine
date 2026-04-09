# Documentation Index

This repository is intentionally documented with a small, accurate doc set.

## Core documents
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md): local development setup and API verification.
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md): production deployment baseline.
- [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md): complete list of what the application can do today.

## Quick start commands
- Backend: `cd backend && python -m venv .venv_local && .venv_local/bin/pip install -r requirements.txt && .venv_local/bin/python app.py`
- Frontend: `cd frontend && npm install && npm start`

## Scope note
- The backend is currently a minimal API focused on sentiment analysis, lexicon management, and political-entity management.
- Some old docs were removed because they described modules/routes that do not exist in this branch.
