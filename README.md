# NL2SQL

NL2SQL is a FastAPI service that converts natural-language questions into PostgreSQL SELECT queries, validates the generated SQL, executes it on a connected database, and returns the result rows.

It is designed for local experimentation and demo use, with a Docker Compose setup for PostgreSQL, the API, and Ollama.

## Features

- FastAPI-based API
- SQL parsing and validation before execution
- PostgreSQL execution of generated SELECT statements
- configurable database and Ollama settings via environment variables
- Docker Compose setup for easy local startup
- seeded demo database for testing with realistic sample data

## Project structure

- `app/main.py` — FastAPI app and request handling
- `app/database.py` — database engine configuration
- `app/schema.py` — schema introspection from PostgreSQL
- `app/llm.py` — calls Ollama to generate SQL from natural language
- `app/validator.py` — ensures the generated SQL is a single safe SELECT
- `app/__init__.py` — database initialization and demo data seeding
- `docker-compose.yml` — services for Postgres, Ollama, and the API
- `Dockerfile` — image for the API service
- `.env.example` — example environment file

## Prerequisites

- Docker and Docker Compose
- a working Docker registry/network connection for pulling base images
- optional: Python 3.13 for local non-container development

## Quick start

1. Create your environment file:

   ```bash
   cp .env.example .env
   ```

2. Update the values in `.env` before starting the stack. At minimum, set a secure database password:

   ```env
   DB_USER=nl2sql
   DB_PASSWORD=change-me
   DB_NAME=nl2sql
   DB_HOST=postgres
   DB_PORT=5432
   APP_PORT=8000
   BIND_ADDRESS=127.0.0.1
   OLLAMA_MODEL=qwen2.5-coder:7b
   ```

3. Start the full stack:

   ```bash
   docker compose up --build -d
   ```

4. Check the API health endpoint:

   ```bash
   curl http://localhost:8000/health
   ```

5. Open the interactive API docs:

   - http://localhost:8000/docs

## API usage

### Health check

```bash
curl http://localhost:8000/health
```

### Generate and execute SQL

```bash
curl -X POST http://localhost:8000/nl2sql \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Show the first 10 users",
    "row_limit": 10
  }'
```

Example response:

```json
{
  "question": "Show the first 10 users",
  "sql": "SELECT id, name, email FROM users ORDER BY id LIMIT 10",
  "row_limit": 10,
  "row_count": 10,
  "rows": [
    {"id": 1, "name": "User 1", "email": "user1@example.com"},
    {"id": 2, "name": "User 2", "email": "user2@example.com"}
  ]
}
```

## Environment variables

The app reads configuration from environment variables instead of hardcoded values.

### Database

You may provide either:

- `DATABASE_URL`, or
- the full `DB_*` set:
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

### Ollama

- `OLLAMA_URL` (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL` (default: `qwen2.5-coder:7b`)

### Docker host settings

- `APP_PORT` — API port on the host
- `POSTGRES_PORT` — Postgres port on the host
- `BIND_ADDRESS` — bind address for exposed ports (default `127.0.0.1`)

## Demo database

The application initializes a local demo database on startup. It creates tables and seeds sample data so the app can generate realistic SQL against a populated schema.

The default seeding includes:

- 10,000 users
- 100 products
- 10,000 orders

Use the following command to reset the database and recreate the demo data:

```bash
docker compose down -v
docker compose up --build -d
```

## Local development

If you want to run the app outside Docker, install dependencies and start the FastAPI app with Uvicorn:

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Notes

- The generated SQL is restricted to a single SELECT statement.
- Query execution is limited by the request `row_limit` field.
- The app expects the connected database to already have the relevant schema, or it uses the included demo initialization path.
- For production use, replace local demo defaults with a managed database and proper secrets management.

## Troubleshooting

### Docker image cannot be pulled

This usually means Docker cannot reach the public registry. Verify connectivity with:

```bash
docker pull hello-world
```

If that fails, check your network, proxy, or Docker daemon configuration.

### Query fails with `relation ... does not exist`

Reset the database volume and restart the stack:

```bash
docker compose down -v
docker compose up --build -d
```

This recreates the demo schema and sample data.

### Want to change the model

Edit `OLLAMA_MODEL` in `.env` and restart the stack:

```bash
docker compose up --build -d
```