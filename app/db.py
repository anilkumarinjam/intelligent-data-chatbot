# app/db.py

import pyodbc
from sqlalchemy import create_engine, text
from app.config import SQL_SERVER_CONN_STRING

# Create SQLAlchemy engine
def get_engine():
    # Build SQLAlchemy connection URL from pyodbc string
    params = SQL_SERVER_CONN_STRING.replace("{", "").replace("}", "")
    # SQLAlchemy mssql+pyodbc format requires a special URL
    conn_str = (
        "mssql+pyodbc://"
        + params
        .replace("Driver=ODBC Driver 17 for SQL Server;", "")
        .replace(";", ":")
        .replace("Server=", "//")
        .replace("UID=", "")
        .replace("PWD=", ":")
    )
    # Actually, better to use urllib.parse for robust encoding - for demo keep simple
    # Alternatively, use URL directly:
    # Example:
    # mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

    # Let's build URL properly:
    from urllib.parse import quote_plus

    conn_str = (
        "mssql+pyodbc://"
        + "sa"  # replace below
        + ":"
        + quote_plus("Ravi@0570")
        + "@localhost:1433"  # replace below
        + "/SampleDB"
        + "?driver=ODBC+Driver+17+for+SQL+Server"
    )

    # You must replace YOUR_USERNAME, YOUR_PASSWORD, YOUR_SQL_SERVER_HOST, YOUR_DATABASE_NAME

    engine = create_engine(conn_str)
    return engine

# Run raw SQL query, return list of dicts
def run_query(sql: str):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(row) for row in result.mappings()]  # Use result.mappings() for dictionary-like rows
    return rows