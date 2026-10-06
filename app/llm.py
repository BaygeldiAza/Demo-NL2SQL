import os

import httpx


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")


def clean_sql(sql: str) -> str:
    """Remove Markdown code fences from LLM output."""

    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[len("```sql"):].strip()

    elif sql.startswith("```"):
        sql = sql[len("```"):].strip()

    if sql.endswith("```"):
        sql = sql[:-3].strip()

    return sql


async def generate_sql(question: str, schema: str) -> str:

    prompt = f"""
You are an expert PostgreSQL SQL generator.

Your job is to convert the user's natural language question
into a PostgreSQL SELECT query.

DATABASE SCHEMA:

{schema}

RULES:

1. Generate ONLY one PostgreSQL SELECT query.
2. Do NOT use Markdown.
3. Do NOT use ```sql.
4. Do NOT use ``` at all.
5. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
6. Use only tables and columns that exist in the schema.
7. Respect the foreign key relationships.
8. Do not explain the query.
9. Return raw SQL only.

USER QUESTION:

{question}

SQL:
"""

    async with httpx.AsyncClient(
        timeout=120,
        trust_env=False,
    ) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
        )

    response.raise_for_status()

    data = response.json()

    return clean_sql(data["response"])