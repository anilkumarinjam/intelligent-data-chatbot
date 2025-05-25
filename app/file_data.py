import os
import pandas as pd
from app.config import DATA_FOLDER
from zipfile import BadZipFile

# Cache loaded dataframes in memory for performance
dataframes = {}

def load_file(filename: str):
    path = os.path.join(DATA_FOLDER, filename)
    if filename.endswith(".csv"):
        df = pd.read_csv(path)
    elif filename.endswith((".xls", ".xlsx")):
        try:
            df = pd.read_excel(path, engine="openpyxl")  # Use 'openpyxl' for .xlsx files
        except BadZipFile:
            raise ValueError(f"The file '{filename}' is not a valid Excel file.")
    else:
        raise ValueError("Unsupported file type: " + filename)
    dataframes[filename] = df
    return df

def get_dataframe(filename: str):
    if filename in dataframes:
        return dataframes[filename]
    else:
        return load_file(filename)

# Example simple query: filter rows by column value
def query_file(filename: str, filter_column=None, filter_value=None):
    df = get_dataframe(filename)
    if filter_column and filter_value:
        filtered_df = df[df[filter_column] == filter_value]
        return filtered_df.to_dict(orient="records")
    else:
        return df.to_dict(orient="records")
