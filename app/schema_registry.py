# app/schema_registry.py

import json
from app.db import run_query
from app.file_data import get_dataframe

SCHEMA_FILE = "schema_registry.json"

def load_schema_registry():
    try:
        with open(SCHEMA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"sql_tables": {}, "files": {}}

def save_schema_registry(schema):
    with open(SCHEMA_FILE, "w") as f:
        json.dump(schema, f, indent=4)

def update_sql_schema():
    schema = load_schema_registry()
    # Example: query SQL Server for table names and columns
    tables_query = """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_CATALOG = DB_NAME()
    """
    rows = run_query(tables_query)
    sql_tables = {}
    for row in rows:
        table = row["TABLE_NAME"]
        col = row["COLUMN_NAME"]
        dtype = row["DATA_TYPE"]
        if table not in sql_tables:
            sql_tables[table] = []
        sql_tables[table].append({"column": col, "type": dtype})
    schema["sql_tables"] = sql_tables
    save_schema_registry(schema)

def update_file_schema():
    schema = load_schema_registry()
    import os
    files = [f for f in os.listdir("data") if f.endswith((".csv", ".xls", ".xlsx"))]
    file_meta = {}
    for file in files:
        df = get_dataframe(file)
        columns = list(df.columns)
        file_meta[file] = {"columns": columns}
    schema["files"] = file_meta
    save_schema_registry(schema)
