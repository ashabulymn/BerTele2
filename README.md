# BerTele2

BerTele2 is an open-source Telegram MTProto gateway built with FastAPI and Telethon.

## What is included

- REST API versioned under `/api/v1`
- Health endpoint
- Version endpoint
- FastAPI lifespan management
- Dependency injection for application services
- Swagger UI at `/docs`
- OpenAPI schema at `/openapi.json`
- Docker and Docker Compose support

## Technology stack

- Python 3.12
- FastAPI
- Telethon
- SQLAlchemy 2
- Alembic
- Pydantic v2
- HTTPX
- Uvicorn
- Pytest
- Ruff
- Black

## Configuration

Copy `.env.example` to `.env` and set your Telegram credentials when you are ready to connect to MTProto.

## Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```
