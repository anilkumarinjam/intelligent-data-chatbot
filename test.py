from sqlalchemy import create_engine, text

def test_connection():
    from urllib.parse import quote_plus

    user = "sa"
    password = "Ravi@0570"
    host = "localhost"
    port = 1433
    database = "master"
    driver = "ODBC Driver 17 for SQL Server"

    params = quote_plus(f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={user};PWD={password}")

    conn_str = f"mssql+pyodbc:///?odbc_connect={params}"

    engine = create_engine(conn_str)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        version = result.scalar()
        print("Connected! SQL Server version:", version)

if __name__ == "__main__":
    test_connection()
