# NL2SQL

Natural-language-to-SQL API backed by PostgreSQL and Ollama.

## Run with Docker Compose

1. Create the local environment file:

   ```sh
   cp .env.example .env
   ```

2. Change `DB_PASSWORD` in `.env` from its example value.
3. Build and start the API, PostgreSQL, and Ollama:

   ```sh
   docker compose up --build
   ```

   On its first start, Ollama downloads the model selected by `OLLAMA_MODEL`
   (default: `qwen2.5-coder:7b`). This model is several gigabytes, so the initial
   startup can take a while. Model data and PostgreSQL data persist in Docker
   volumes.

4. Check the API at <http://localhost:8000/health> or open the interactive API
   docs at <http://localhost:8000/docs>.

PostgreSQL starts with an empty database. Load your tables and data into it
before expecting useful SQL generation.

Send a question to the API:

```sh
curl -X POST http://localhost:8000/nl2sql \
  -H 'Content-Type: application/json' \
  -d '{"question":"List all customers"}'
```

Use `APP_PORT`, `POSTGRES_PORT`, `BIND_ADDRESS`, and `OLLAMA_MODEL` in `.env`
to customize the host ports, bind address, and model. For production, provide
strong credentials through a secret manager and configure appropriate network
exposure rather than relying on the local-development defaults.

## Configuration

The API accepts `DATABASE_URL` or the individual `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER`, and `DB_PASSWORD` settings. Ollama is configured with
`OLLAMA_URL` and `OLLAMA_MODEL`. The Compose setup supplies these settings for
container-to-container networking; do not use `localhost` for a dependency
running in another container.