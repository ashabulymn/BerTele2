# BerTele2

BerTele2 is an open-source Telegram MTProto gateway built with FastAPI and Telethon.

## Features

- REST API with versioning under `/api/v1`
- OpenAPI at `/openapi.json`
- Interactive docs at `/docs`
- Telethon session-string authentication
- SQLite by default, PostgreSQL supported
- Structured JSON logging
- Clean Architecture folder layout
- Docker and Docker Compose support

## API

- `GET /api/v1/health`
- `GET /api/v1/version`
- `GET /api/v1/me`
- `POST /api/v1/messages/send`
- `GET /api/v1/dialogs`

## Configuration

Copy `.env.example` to `.env` and set:

- `BERTELE2_TELEGRAM_API_ID`
- `BERTELE2_TELEGRAM_API_HASH`
- `BERTELE2_TELEGRAM_SESSION_STRING`

Optional values:

- `BERTELE2_TELEGRAM_PHONE_NUMBER`
- `BERTELE2_TELEGRAM_BOT_TOKEN`
- `BERTELE2_DATABASE_URL`

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```

