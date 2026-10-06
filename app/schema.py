from sqlalchemy import inspect

from app.database import engine


def get_schema() -> str:
    inspector = inspect(engine)

    output = []

    for table_name in inspector.get_table_names():
        output.append(f"Table: {table_name}")

        columns = inspector.get_columns(table_name)

        for column in columns:
            output.append(
                f"  - {column['name']}: {column['type']}"
            )

        foreign_keys = inspector.get_foreign_keys(table_name)

        for fk in foreign_keys:
            output.append(
                f"  - FOREIGN KEY: "
                f"{table_name}.{fk['constrained_columns'][0]} "
                f"-> "
                f"{fk['referred_table']}.{fk['referred_columns'][0]}"
            )

    return "\n".join(output)