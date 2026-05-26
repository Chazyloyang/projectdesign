# Backend API

FastAPI application for the DevSecOps Quality Automation Platform.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Celery worker

```bash
celery -A app.workers.celery_app worker -l info
```

## Migrations

```bash
alembic upgrade head
```
