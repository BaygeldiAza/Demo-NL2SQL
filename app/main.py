from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app import init_db
from app.database import engine
from app.schema import get_schema
from app.llm import generate_sql
from app.validator import validate_sql, UnsafeSQL


app = FastAPI(title="NL2SQL API")


@app.on_event("startup")
async def startup_event():
    init_db()


class QuestionRequest(BaseModel):
    question: str
    row_limit: int = Field(default=50, ge=1, le=500)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/nl2sql")
async def nl2sql(request: QuestionRequest):

    schema = get_schema()

    sql = await generate_sql(
        question=request.question,
        schema=schema,
    )

    try:
        safe_sql = validate_sql(sql)
    except UnsafeSQL as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    try:
        with engine.connect() as connection:
            result = connection.execute(text(safe_sql))
            rows = result.mappings().fetchmany(request.row_limit)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {exc}",
        ) from exc

    return {
        "question": request.question,
        "sql": safe_sql,
        "row_limit": request.row_limit,
        "row_count": len(rows),
        "rows": [dict(row) for row in rows],
    }