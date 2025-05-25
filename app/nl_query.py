# app/nl_query.py

from app.schema_registry import load_schema_registry
from app.db import run_query
from app.file_data import query_file
from app.llm_client import llm_generate
import ast
import re
from app.chart_utils import generate_chart as generate_chart_fn
from app.vector_store import query_knowledge
from app.formula_registry import get_all_formulas

def build_prompt(nl_query: str, schema: dict):
    sql_tables = schema.get("sql_tables", {})
    files = schema.get("files", {})

    prompt = "You are a data assistant. Here are the schemas available:\n\n"

    prompt += "SQL Tables:\n"
    for table, cols in sql_tables.items():
        cols_list = ", ".join([str(c["column"]) for c in cols])
        prompt += f"- {table}: {cols_list}\n"

    prompt += "\nFiles:\n"
    for fname, meta in files.items():
        cols_list = ", ".join([str(col) for col in meta["columns"]])
        prompt += f"- {fname}: {cols_list}\n"

    # <-- Add these instructions here -->
    prompt += "\nAssume dataframes for CSV/Excel files are preloaded and named after file, replacing dots with underscores.\n"
    prompt += "For example, 'sales_data.xlsx' is available as 'sales_data_xlsx'.\n"
    prompt += "Do NOT include import statements or file loading commands.\n"
    prompt += "Output only valid Python code that assigns your final dataframe to variable named 'result'.\n\n"

    prompt += "User Query:\n"
    prompt += nl_query + "\n"

    prompt += "\nReturn either a valid SQL query (starting with SQL:) or a Python pandas code snippet (starting with PANDAS:) to answer the question.\n"
    prompt += "If multiple data sources are mentioned, generate code accordingly.\n"
    prompt += "Only output the query/code, nothing else."

    return prompt


def parse_llm_response(resp: str):
    """
    Parses LLM response to detect SQL or Pandas code and extract it.
    Cleans out markdown code fences and language tags.
    """
    # Find SQL or PANDAS section
    sql_match = re.search(r"SQL:\s*([\s\S]*?)(?:PANDAS:|$)", resp)
    pandas_match = re.search(r"PANDAS:\s*([\s\S]*)", resp)

    if sql_match:
        code = sql_match.group(1).strip()
        # Remove code fences and language tags
        code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
        code = re.sub(r"```$", "", code)
        return "sql", code.strip()
    elif pandas_match:
        code = pandas_match.group(1).strip()
        code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
        code = re.sub(r"```$", "", code)
        return "pandas", code.strip()
    else:
        raise ValueError("LLM response not in expected format (missing SQL: or PANDAS: prefix)")

def execute_pandas_code(code: str, schema: dict):
    """
    Very simple and safe way to execute generated pandas code snippet.
    Only allow dataframe names from known files.
    Returns list of dicts as result.
    """
    # print("Generated pandas code:")
    # print(code)
    # Available dataframes in code namespace
    dfs = {}
    from app.file_data import get_dataframe
    for fname in schema.get("files", {}):
        dfs[fname.replace('.', '_')] = get_dataframe(fname)

    # Prepare execution environment
    exec_env = {"pd": __import__("pandas")}
    exec_env.update(dfs)

    try:
        # The code should produce a variable `result` which is a dataframe or list of dicts
        exec(code, exec_env)
        result = exec_env.get("result", None)
        if result is None:
            raise ValueError("Pandas code must assign the output to variable 'result'")
        if hasattr(result, "to_dict"):
            return result.to_dict(orient="records")
        else:
            return list(result)
    except Exception as e:
        raise RuntimeError(f"Error executing pandas code: {e}")

# app/nl_query.py (add import)
from app.chart_utils import generate_chart

def build_prompt_with_memory(nl_query: str, schema: dict):
    base_prompt = build_prompt(nl_query, schema)

    # Retrieve context from vector store
    retrieved_docs = query_knowledge(nl_query)

    # Get formulas as text
    formulas = get_all_formulas()
    formulas_text = "\n".join([f"{name}: {info['description']}\n{info['code']}" for name, info in formulas.items()])

    # Combine all
    full_prompt = (
        base_prompt
        + "\n\nRelevant Knowledge:\n"
        + "\n".join(retrieved_docs)
        + "\n\nBusiness Logic Formulas:\n"
        + formulas_text
    )
    return full_prompt


def nl_query_handler(nl_query: str, generate_chart: bool = False):
    schema = load_schema_registry()
    prompt = build_prompt(nl_query, schema)
    llm_resp = llm_generate(prompt)

    query_type, query_or_code = parse_llm_response(llm_resp)

    if query_type == "sql":
        data = run_query(query_or_code)
    elif query_type == "pandas":
        data = execute_pandas_code(query_or_code, schema)
    else:
        data = None

    response = {
        "query_type": query_type,
        "query": query_or_code,
        "data": data,
    }

    if generate_chart:
        # Simple heuristic: guess x and y columns for charting
        if data and len(data) > 0:
            cols = list(data[0].keys())
            x_col = cols[0]
            y_col = None
            # Find first numeric column for y
            for c in cols[1:]:
                try:
                    if isinstance(data[0][c], (int, float)):
                        y_col = c
                        break
                except Exception:
                    continue
            if y_col:
                chart_html = generate_chart_fn(data, chart_type="bar", x_col=x_col, y_col=y_col)
                response["chart"] = chart_html
            else:
                response["chart"] = "No numeric column found for chart."
        else:
            response["chart"] = "No data to plot."

    return response

