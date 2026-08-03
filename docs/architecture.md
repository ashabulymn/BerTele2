# Architecture

BerTele2 follows a clean, layered structure:

- `app/api` defines HTTP routes and versioned endpoints.
- `app/core` contains configuration, logging, database, dependency, and lifespan wiring.
- `app/services` contains application services that orchestrate Telegram and persistence behavior.
- `app/models` contains SQLAlchemy ORM models.
- `app/schemas` contains Pydantic response and request schemas.

The initial bootstrap focuses on the health and version endpoints so the gateway can be deployed and observed before Telegram credentials are configured.
