import plotly.express as px
import pandas as pd
import json

def generate_chart(data: list, chart_type: str = "bar", x_col: str = None, y_col: str = None):
    """
    Generates Plotly chart data as JSON.

    Args:
        data: list of dicts (records)
        chart_type: one of "bar", "line", "pie", "scatter"
        x_col, y_col: columns to plot on X and Y axes (if applicable)

    Returns:
        dict: JSON-serializable Plotly figure data
    """
    if not data:
        raise ValueError("Empty data provided for chart generation")

    df = pd.DataFrame(data)

    if chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col)
    elif chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col)
    elif chart_type == "pie":
        fig = px.pie(df, names=x_col, values=y_col)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x_col, y=y_col)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return json.loads(fig.to_json())