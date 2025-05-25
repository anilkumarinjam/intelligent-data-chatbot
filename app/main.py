# app/main.py

from fastapi import FastAPI, Query
from app.schema_registry import load_schema_registry, update_sql_schema, update_file_schema
from app.db import run_query
from app.file_data import query_file
from fastapi import Body
from app.nl_query import nl_query_handler
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Intelligent Data Chatbot Phase 1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup_event():
    # Update schema registry on startup
    update_sql_schema()
    update_file_schema()

# filepath: /Users/anilkumarinjam/Downloads/Techlancer/intelligent-data-chatbot/app/main.py
@app.get("/")
def read_root():
    return {"message": "Welcome to the Intelligent Data Chatbot API"}

@app.get("/schemas")
def get_schemas():
    return load_schema_registry()

@app.get("/query/sql")
def query_sql(q: str = Query(..., description="SQL query to execute")):
    try:
        result = run_query(q)
        return {"data": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/query/file")
def query_file_endpoint(
    filename: str = Query(..., description="CSV or Excel filename"),
    filter_column: str = Query(None, description="Column to filter on"),
    filter_value: str = Query(None, description="Value to filter by"),
):
    try:
        result = query_file(filename, filter_column, filter_value)
        return {"data": result}
    except Exception as e:
        return {"error": str(e)}

# filepath: /Users/anilkumarinjam/Downloads/Techlancer/intelligent-data-chatbot/app/main.py
@app.get("/favicon.ico")
def favicon():
    return {"message": "Favicon not implemented"}

from fastapi import Body, Query

@app.post("/query/nl")
def query_nl_endpoint(
    query: str = Body(..., embed=True),
    generate_chart: bool = Query(False, description="Generate chart for result"),
):
    """
    Accepts a natural language query in POST body JSON { "query": "..." }
    Returns generated query, query type, results, and optionally chart.
    """
    try:
        result = nl_query_handler(query, generate_chart=generate_chart)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/feedback")
def feedback_endpoint(
    id: str = Body(..., embed=True),
    text: str = Body(..., embed=True),
    formula_name: str = Body(None),
    formula_code: str = Body(None),
    formula_description: str = Body(None),
):
    """
    Accept user feedback or formulas and update knowledge base and registry.
    """
    try:
        # Add to vector store
        add_knowledge(id, text)

        # Add formula if provided
        if formula_name and formula_code:
            add_formula(formula_name, formula_code, formula_description or "")

        return {"message": "Feedback added successfully."}
    except Exception as e:
        return {"error": str(e)}