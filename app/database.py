import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def _create_engine():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return create_engine(database_url)

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    missing = [
        name
        for name, value in {
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
            "DB_HOST": db_host,
            "DB_PORT": db_port,
            "DB_NAME": db_name,
        }.items()
        if value is None or value == ""
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment configuration: " + ", ".join(missing)
            + ". Set DATABASE_URL or all DB_* variables."
        )

    return create_engine(
        URL.create(
            "postgresql+psycopg",
            username=db_user,
            password=db_password,
            host=db_host,
            port=int(db_port),
            database=db_name,
        )
    )


engine = _create_engine()
