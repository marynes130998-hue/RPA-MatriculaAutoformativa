import pyodbc
from config import settings

def get_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.SERVER};"
            f"DATABASE={settings.DATABASE};"
            # f"UID={settings.USERNAME};"
            # f"PWD={settings.PASSWORD};"
            f"Trusted_Connection=yes;" # <--- Esto reemplaza a UID y PWD (para Windows Authentication)
        )
        return conn
    
    except Exception as e:
        return