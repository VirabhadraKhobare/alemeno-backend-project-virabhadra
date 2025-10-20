# Enhanced Backend Internship Project
This project is an enhanced backend prepared for the internship assignment.

Features:
- Flask REST API (health, items CRUD)
- ML integration module (OpenAI + mock fallback)
- Dockerfile and docker-compose with PostgreSQL
- GitHub Actions CI workflow (lint + tests)
- Pytest tests
- Instructions to run locally and with Docker

## Run locally (recommended for development)
1. Create a virtualenv: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -r requirements.txt`
3. Export env vars:
   - `FLASK_APP=run.py`
   - `FLASK_ENV=development`
   - `DATABASE_URL=sqlite:///dev.db` (or a Postgres connection)
   - `OPENAI_API_KEY` (optional, for real ML calls)
4. Run: `flask run --host=0.0.0.0 --port=5000`

## Run with Docker
1. `docker compose up --build`
2. API available at http://localhost:5000

## Endpoints
- `GET /health` - health check
- `GET /api/v1/items` - list items
- `POST /api/v1/items` - create item (json: {"name":"...","description":"..."})
- `POST /api/v1/ml/summarize` - summarize text using OpenAI or mock (json: {"text":"..."})

## Notes
- This project uses an OpenAI integration as a placeholder. If you provide `OPENAI_API_KEY`, the `/ml/summarize` endpoint will attempt to call OpenAI's API.
- CI uses pytest and flake8.
