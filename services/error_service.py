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
    if isinstance(e, pyodbc.OperationalError):
        return build_error(
            "DATABASE_ERROR",
            1,
            e
        )

    elif isinstance(e, pyodbc.ProgrammingError):
        return build_error(
            "DATABASE_ERROR",
            1,
            e
        )
    
    elif isinstance(e, pyodbc.InterfaceError):
        return build_error(
            "DATABASE_ERROR",
            1,
            e
        )
    
    # -----------------------------
    # API (MOODLE - SIFODS)
    # -----------------------------
    elif isinstance(e, requests.exceptions.Timeout):
        return build_error(
                "API_ERROR", 
                2,
                e
        )

    elif isinstance(e, requests.exceptions.ConnectionError):
        return build_error(
                "API_ERROR",
                2,
                e
        )

    elif isinstance(e, requests.exceptions.HTTPError):
        return build_error(
                "API_ERROR",
                2,
                e
        )

    # -----------------------------
    # GMAIL API
    # -----------------------------
    elif isinstance(e, HttpError):
        return build_error(
            "GMAIL_API_ERROR", 
            3,
            e
        )

    # -----------------------------
    # NETWORK / INFRASTRUCTURE
    # -----------------------------
    elif isinstance(e, socket.gaierror):
        return build_error(
            "INFRASTRUCTURE_ERROR",
            4,
            e
        )

    elif isinstance(e, ConnectionError):
        return build_error(
            "INFRASTRUCTURE_ERROR",
            4,
            e
        )
    
    # -----------------------------
    # EXCEL (LECTURA / ESCRITURA)
    # -----------------------------
    elif isinstance(e, FileNotFoundError):
        return build_error(
            "EXCEL_ERROR", 
            5,
            e
        )

    elif isinstance(e, PermissionError):
        return build_error(
            "EXCEL_ERROR", 
            5,
            e
        )

    
    # -------------------------------------------------
    # ERRORES PROPIOS DE PYTHON (VARIABLES, FUNCIONES)
    # -------------------------------------------------
    elif isinstance(e, KeyError):
        return build_error(
            "DATA_STRUCTURE_ERROR",
            6,
            e
        )
    
    elif isinstance(e, pd.errors.EmptyDataError):
        return build_error(
            "DATA_STRUCTURE_ERROR",
            6,
            e
        )

    elif isinstance(e, ValueError):
        return build_error(
            "DATA_STRUCTURE_ERROR", 
            6,
            e
        )
    
    elif isinstance(e, AttributeError):
        return build_error(
            "APPLICATION_ERROR",
            7,
            e
        )
    
    elif isinstance(e, TypeError):
        return build_error(
            "APPLICATION_ERROR",
            7,
            e
        )
    
    elif isinstance(e, IndexError):
        return build_error(
            "DATA_STRUCTURE_ERROR",
            6,
            e
        )

    elif "BUSINESS_RULE_ERROR" in str(e):
        return build_error(
            "BUSINESS_RULE_ERROR",
            8,
            e
        )

    # -----------------------------
    # ERROR DESCONOCIDO
    # -----------------------------
    else:
        return build_error(
            "APPLICATION_ERROR",
            8,
            e
        )


def build_error(categoria, id_error, e=None):
    return {
        "categoria": categoria,
        "id": id_error,
        "detalle": str(e) if e else None,
        "trace": traceback.format_exc() if e else None
    }