from googleapiclient.errors import HttpError
import pyodbc
import socket
import requests
import pandas as pd
import traceback

def map_exception(e):
    # -----------------------------
    # DATABASE (SQL SERVER)
    # -----------------------------
    if isinstance(e, (pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.InterfaceError)):
        return build_error("DATABASE_ERROR", 1, e)
    
    # -----------------------------
    # API (MOODLE - SIFODS)
    # -----------------------------
    elif isinstance(e, (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError)):
        return build_error("API_ERROR", 2, e)

    # -----------------------------
    # GMAIL API
    # -----------------------------
    elif isinstance(e, HttpError):
        return build_error("GMAIL_API_ERROR", 3, e)

    # -----------------------------
    # NETWORK / INFRASTRUCTURE
    # -----------------------------
    elif isinstance(e, (socket.gaierror, ConnectionError)):
        return build_error("INFRASTRUCTURE_ERROR", 4, e)
    
    # -----------------------------
    # EXCEL (LECTURA / ESCRITURA)
    # -----------------------------
    elif isinstance(e, (FileNotFoundError, PermissionError)):
        return build_error("EXCEL_ERROR", 5, e)
    
    # -------------------------------------------------
    # ERRORES PROPIOS DE PYTHON (VARIABLES, FUNCIONES)
    # -------------------------------------------------
    elif isinstance(e, (KeyError, pd.errors.EmptyDataError, ValueError, IndexError)):
        return build_error("DATA_STRUCTURE_ERROR", 6, e)
    
    elif isinstance(e, (AttributeError, TypeError)):
        return build_error("APPLICATION_ERROR", 7, e)

    # ------------------
    # ERRORES DE NEGOCIO
    # ------------------
    elif "BUSINESS_RULE_ERROR" in str(e):
        return build_error("BUSINESS_RULE_ERROR", 8, e)

    # -----------------------------
    # ERROR DESCONOCIDO
    # -----------------------------
    else:
        return build_error("APPLICATION_ERROR", 7, e)

def build_error(categoria, id_error, e=None):
    return {
        "categoria": categoria,
        "id": id_error,
        "detalle": str(e) if e else None,
        "trace": traceback.format_exc() if e else None
    }