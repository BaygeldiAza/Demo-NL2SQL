# NL2SQL

NL2SQL is a FastAPI service that converts natural-language questions into PostgreSQL `SELECT` queries, validates the generated SQL, executes it against a connected PostgreSQL database, and returns the query results.

It is designed for local experimentation and demo use, with a Docker Compose setup for PostgreSQL, the API, and Ollama running a local Qwen model.

---

## Project Architecture

The application follows a simple pipeline:

```text
┌─────────────────────┐
│       User          │
│                     │
│ "Show me 10 users"  │
└──────────┬──────────┘
           │
           │ Natural-language question
           ▼
┌─────────────────────┐
│      FastAPI        │
│                     │
│    POST /nl2sql     │
└──────────┬──────────┘
           │
           │ 1. Get database schema
           ▼
┌─────────────────────┐
│  PostgreSQL Schema  │
│                     │
│ users               │
│ products            │
│ orders              │
│ relationships       │
└──────────┬──────────┘
           │
           │ Schema + user question
           ▼
┌─────────────────────┐
│   Ollama + Qwen     │
│                     │
│  Natural Language   │
│         ↓           │
│        SQL          │
└──────────┬──────────┘
           │
           │ Generated SQL
           ▼
┌─────────────────────┐
│     SQLGlot         │
│                     │
│ SQL parsing &       │
│ validation          │
│                     │
│ Only SELECT allowed │
└──────────┬──────────┘
           │
           │ Valid SELECT
           ▼
┌─────────────────────┐
│     PostgreSQL      │
│                     │
│ Execute SQL query   │
└──────────┬──────────┘
           │
           │ Query rows
           ▼
┌─────────────────────┐
│      FastAPI        │
│                     │
│ Format response     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│        JSON         │
│                     │
│ SQL + row_count     │
│ + rows              │
└─────────────────────┘
```

### Request Flow

For a request such as:

```text
Show me the first 10 users
```

the application performs the following steps:

1. FastAPI receives the natural-language question.
2. The application introspects PostgreSQL and retrieves the relevant database schema.
3. The question and schema are sent to the Qwen model through Ollama.
4. Qwen generates a PostgreSQL `SELECT` query.
5. SQLGlot parses and validates the generated SQL.
6. The application rejects invalid or non-`SELECT` statements.
7. The validated query is executed against PostgreSQL.
8. The database returns the matching rows.
9. FastAPI returns the generated SQL and query results as JSON.

The core pipeline is:

```text
Natural Language
       ↓
   FastAPI
       ↓
 Database Schema
       ↓
   Qwen/Ollama
       ↓
 Generated SQL
       ↓
   SQLGlot
       ↓
 PostgreSQL
       ↓
   Query Rows
       ↓
     JSON
```

---

## Component Architecture

### 1. FastAPI

FastAPI is the HTTP API layer.

It is responsible for:

* receiving user questions
* validating request parameters
* coordinating the NL2SQL pipeline
* executing validated queries
* returning JSON responses
* exposing interactive API documentation

Main endpoint:

```text
POST /nl2sql
```

---

### 2. PostgreSQL

PostgreSQL stores the application data.

The database also provides the schema information used by the LLM.

Example tables:

```text
users
products
orders
```

Example relationship:

```text
users
  │
  │ user_id
  ▼
orders
  │
  │ product_id
  ▼
products
```

---

### 3. Schema Introspection

Before generating SQL, the application inspects PostgreSQL to understand the available database structure.

It retrieves information such as:

* table names
* column names
* column types
* foreign keys
* table relationships

Example schema information:

```text
Table: users
  - id: INTEGER
  - name: VARCHAR
  - email: VARCHAR

Table: orders
  - id: INTEGER
  - user_id: INTEGER
  - product_id: INTEGER
  - quantity: INTEGER
  - amount: NUMERIC

  - FOREIGN KEY:
    orders.user_id -> users.id

  - FOREIGN KEY:
    orders.product_id -> products.id
```

This schema is provided to the LLM so that it can generate SQL using the actual database structure.

---

### 4. Ollama + Qwen

Ollama runs the local LLM.

The default model is:

```text
qwen2.5-coder:7b
```

The model receives:

```text
User question
+
Database schema
+
SQL generation rules
```

and produces SQL.

For example:

```text
Question:
Show the first 10 users
```

The model may generate:

```sql
SELECT id, name, email
FROM users
ORDER BY id
LIMIT 10;
```

The model is responsible for **generating SQL**, not directly accessing the database.

---

### 5. SQLGlot Validation

Generated SQL is treated as untrusted input.

Before execution, SQLGlot parses the query and checks that:

* the SQL is syntactically valid
* there is only one SQL statement
* the statement is a `SELECT`
* modification statements such as `INSERT`, `UPDATE`, and `DELETE` are rejected
* DDL statements such as `DROP`, `ALTER`, and `CREATE` are rejected

The pipeline therefore becomes:

```text
Qwen
 ↓
Generated SQL
 ↓
SQLGlot
 ↓
Validation
 ↓
PostgreSQL
```

Invalid SQL is rejected before reaching PostgreSQL.

---

### 6. PostgreSQL Query Execution

After validation, the application executes the generated `SELECT` query against PostgreSQL.

The request supports a configurable `row_limit` to prevent unnecessarily large responses.

Example:

```json
{
  "question": "Show the first 10 users",
  "row_limit": 10
}
```

The database executes the validated query and returns the matching rows.

---

### 7. JSON Response

FastAPI converts the database result into a JSON response.

Example:

```json
{
  "question": "Show the first 10 users",
  "sql": "SELECT id, name, email FROM users ORDER BY id LIMIT 10",
  "row_limit": 10,
  "row_count": 10,
  "rows": [
    {
      "id": 1,
      "name": "User 1",
      "email": "user1@example.com"
    },
    {
      "id": 2,
      "name": "User 2",
      "email": "user2@example.com"
    }
  ]
}
```

---

## Features

* FastAPI-based REST API
* Natural-language-to-SQL generation
* Local Qwen LLM through Ollama
* PostgreSQL schema introspection
* SQL parsing and validation
* Single-statement enforcement
* `SELECT`-only execution
* PostgreSQL query execution
* Configurable result row limits
* JSON query results
* Docker Compose development environment
* Seeded demo database
* Environment-based configuration
* Interactive Swagger API documentation

---

## Project Structure

```text
NL2SQL/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── schema.py
│   ├── llm.py
│   └── validator.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .env
├── .env.example
└── README.md
```

### Application Modules

#### `app/main.py`

Main FastAPI application.

Responsible for:

```text
Request
  ↓
Schema
  ↓
LLM
  ↓
Validation
  ↓
Execution
  ↓
Response
```

---

#### `app/database.py`

Database configuration and SQLAlchemy engine creation.

Responsible for connecting the API to PostgreSQL.

---

#### `app/schema.py`

PostgreSQL schema introspection.

Responsible for discovering:

* tables
* columns
* data types
* foreign keys
* relationships

---

#### `app/llm.py`

Ollama/Qwen integration.

Responsible for:

* building the LLM prompt
* sending the question and schema to Ollama
* receiving generated SQL
* cleaning the model response

---

#### `app/validator.py`

SQL validation layer.

Responsible for parsing generated SQL and ensuring that only safe `SELECT` statements are accepted.

---

#### `docker-compose.yml`

Defines the development infrastructure:

```text
┌────────────────────────────────────┐
│          Docker Compose            │
│                                    │
│  ┌────────────┐                    │
│  │  FastAPI   │                    │
│  │    API     │                    │
│  └─────┬──────┘                    │
│        │                           │
│        ├──────────────┐            │
│        │              │            │
│        ▼              ▼            │
│  ┌──────────┐   ┌──────────────┐  │
│  │PostgreSQL│   │    Ollama    │  │
│  │          │   │    + Qwen    │  │
│  └──────────┘   └──────────────┘  │
│                                    │
└────────────────────────────────────┘
```

---

## Prerequisites

* Docker
* Docker Compose
* A working Docker registry/network connection
* Optional: Python 3.13 for local development

---

## Quick Start

### 1. Create the environment file

```bash
cp .env.example .env
```

### 2. Configure `.env`

Example:

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

### 3. Start the stack

```bash
docker compose up --build -d
```

The stack contains:

```text
FastAPI
PostgreSQL
Ollama
Qwen model initialization
```

### 4. Check the API

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

### 5. Open Swagger

Open:

```text
http://localhost:8000/docs
```

---

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

---

### Generate and Execute SQL

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
    {
      "id": 1,
      "name": "User 1",
      "email": "user1@example.com"
    },
    {
      "id": 2,
      "name": "User 2",
      "email": "user2@example.com"
    }
  ]
}
```

The important distinction is that the API returns **both**:

```text
Generated SQL
+
Actual database results
```

---

## Example NL2SQL Questions

The API can answer questions such as:

```text
Show me the first 10 users
```

```text
How many users are in the database?
```

```text
Show all products that cost more than 500
```

```text
What are the most expensive products?
```

```text
Show the total order amount for each user
```

```text
Which users have placed the most orders?
```

The model generates the SQL required to answer the question, and the API executes the validated query against PostgreSQL.

---

## Environment Variables

The application supports environment-based configuration.

### Database

You can configure PostgreSQL using:

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=nl2sql
DB_USER=nl2sql
DB_PASSWORD=change-me
```

Alternatively, the application can use:

```env
DATABASE_URL=postgresql+psycopg://...
```

### Ollama

```env
OLLAMA_URL=http://ollama:11434/api/generate
OLLAMA_MODEL=qwen2.5-coder:7b
```

### Docker Host Settings

```env
APP_PORT=8000
POSTGRES_PORT=5432
BIND_ADDRESS=127.0.0.1
```

---

## Demo Database

The application initializes a local demo database with sample data.

The default dataset contains:

```text
10,000 users
100 products
10,000 orders
```

The database is useful for testing natural-language queries against a realistic dataset.

### Reset the Demo Database

To completely recreate the PostgreSQL database:

```bash
docker compose down -v
docker compose up --build -d
```

> Warning: `docker compose down -v` deletes the PostgreSQL Docker volume and all data stored in it.

---

## Local Development

For development without Docker:

```bash
uv sync
```

Then:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Make sure PostgreSQL and Ollama are available to the application.

---

## Security Considerations

This project is intended for local experimentation and demonstration.

Generated SQL should always be treated as untrusted input.

The current validation layer provides basic protection by enforcing:

```text
Single SQL statement
        ↓
Valid SQL
        ↓
SELECT only
        ↓
Execute
```

For production use, additional controls should be implemented, including:

* dedicated read-only PostgreSQL user
* database-level permissions
* statement timeouts
* query cost limits
* explicit table/column allowlists
* protection against expensive joins
* result-size limits
* query logging and monitoring
* authentication and authorization
* proper secret management
* SQL execution policies

The LLM itself should never be considered a security boundary.

---

## Troubleshooting

### Docker image cannot be pulled

Test Docker registry connectivity:

```bash
docker pull hello-world
```

If this fails, check:

* network connectivity
* Docker daemon
* proxy configuration
* Docker registry access

---

### PostgreSQL authentication failed

If you see:

```text
password authentication failed for user "nl2sql"
```

the PostgreSQL volume may contain credentials from an earlier initialization.

For a disposable development database:

```bash
docker compose down -v
docker compose up --build -d
```

---

### `relation ... does not exist`

The database may not have been initialized correctly.

Reset the development database:

```bash
docker compose down -v
docker compose up --build -d
```

---

### Ollama model download is slow

The first startup downloads the configured Qwen model.

Check:

```bash
docker compose logs ollama-init
```

After the model has been downloaded, it is stored in the Docker volume:

```text
ollama_data
```

Avoid using:

```bash
docker compose down -v
```

unless you intentionally want to remove the stored model and database volumes.

---

### Want to change the model

Edit:

```env
OLLAMA_MODEL=qwen2.5-coder:7b
```

Then restart the stack:

```bash
docker compose up --build -d
```

---

## Future Improvements

The current implementation is intentionally simple. A production-oriented version could introduce:

### V1 — Current MVP

```text
Question
   ↓
Full Schema
   ↓
Qwen
   ↓
SQL Validation
   ↓
PostgreSQL
   ↓
Results
```

### V2 — Schema Retrieval

For larger databases, sending the entire schema to the LLM becomes inefficient.

The system could retrieve only relevant:

* tables
* columns
* relationships

before generating SQL.

```text
Question
   ↓
Schema Retrieval
   ↓
Relevant Schema
   ↓
Qwen
   ↓
SQL
```

### V3 — Embeddings / Vector Database

Embeddings can be used to find semantically relevant schema descriptions, table documentation, and business terminology.

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Relevant Schema
   ↓
Qwen
```

### V4 — Relationship-Aware Retrieval

Foreign-key relationships can be represented explicitly so that the system understands how tables should be joined.

```text
users
  │
  └── orders
        │
        └── products
```

### V5 — Query Optimization and Evaluation

Future versions could add:

* SQL query cost analysis
* `EXPLAIN`-based validation
* query caching with Redis
* latency monitoring
* SQL generation evaluation
* failed-query tracking
* LLM response quality metrics

---

## Architecture Summary

The main design principle of this project is to separate **generation, validation, and execution**.

```text
┌─────────────────┐
│ Natural Language│
└────────┬────────┘
         ↓
┌─────────────────┐
│     Qwen LLM    │
│ SQL Generation   │
└────────┬────────┘
         ↓
┌─────────────────┐
│     SQLGlot     │
│ SQL Validation  │
└────────┬────────┘
         ↓
┌─────────────────┐
│   PostgreSQL    │
│ SQL Execution   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Query Results  │
└─────────────────┘
```

This separation makes the system easier to understand, test, secure, and extend.

---

## License

This project is intended for educational, experimentation, and demonstration purposes.
