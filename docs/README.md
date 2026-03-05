# Documentation Index

This project now uses a minimal documentation set.

## Core docs
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md): local setup, backend/frontend launch, API sanity checks, troubleshooting.
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md): production configuration and deployment notes.
- [../backend/BACKEND_CONTRACT.md](../backend/BACKEND_CONTRACT.md): canonical backend launch, required runtime files, frontend API contract.

## Canonical launch commands
- Backend: `cd backend && python app.py`
- Frontend: `cd frontend && npm start`

## Notes
- `simple_app.py` is compatibility-only.
- Removed docs were redundant or stale (legacy test scripts, `app_production.py` references, duplicated setup instructions).
