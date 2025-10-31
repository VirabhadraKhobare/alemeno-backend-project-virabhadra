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
   - For Streamlit Cloud (frontend) we keep `requirements.txt` minimal to avoid
      native build failures. To install the full backend dependencies (Flask,
      SQLAlchemy, psycopg2, etc.) use:

      pip install -r backend-requirements.txt

   - For simple Streamlit testing locally use the base `requirements.txt`.
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

## Streamlit deployment

This repository includes a Streamlit front-end at `streamlit_app.py` that uses the same ML summarizer logic (so you can deploy on Streamlit Cloud).

To deploy on Streamlit Cloud:

- Ensure `requirements.txt` contains `streamlit` (it has been added).
- In Streamlit app settings set the main file to `streamlit_app.py` (Streamlit often auto-detects it).
- Optionally add an `OPENAI_API_KEY` secret in Streamlit to enable real OpenAI summarization.

Run locally:

```powershell
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

The Flask app entrypoint (`run.py`) remains for running the REST API with Gunicorn or Flask directly.
