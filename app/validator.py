import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


class UnsafeSQL(Exception):
    pass


def validate_sql(sql: str) -> str:
    sql = sql.strip()

    if not sql:
        raise UnsafeSQL("SQL query is empty.")

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError:
        raise UnsafeSQL("Invalid SQL query.")

    if len(statements) != 1:
        raise UnsafeSQL("Only one SQL statement is allowed.")

    expression = statements[0]

    if not isinstance(expression, exp.Select):
        raise UnsafeSQL("Only SELECT queries are allowed.")

    return expression.sql(dialect="postgres")