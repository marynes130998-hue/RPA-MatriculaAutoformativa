import requests
""" from config.settings import MOODLE_URL, MOODLE_TOKEN """
from config.config import *

def moodle_api_get_enrolled_users(course_id, offset, limit):
    
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json",
        "courseid": course_id,

        # CAMPOS NECESARIOS 
        "options[0][name]": "userfields",
        "options[0][value]": "username, roles",

        # PAGINACION
        "options[1][name]": "limitfrom",
        "options[1][value]": offset,

        "options[2][name]": "limitnumber",
        "options[2][value]": limit, 
    }

    # --- Validar llamada a MOODLE API ---
    try:
        response = requests.get(BASE_URL_MOODLE, params)
        response.raise_for_status()

    except requests.exceptions.Timeout as e:
        print(str(e))
        raise RuntimeError("Timeout en API Moodle") from e

    except requests.exceptions.ConnectionError as e:
        print(str(e))
        raise RuntimeError("Error de conexión con Moodle") from e

    except requests.exceptions.HTTPError as e:
        print(str(e))
        raise RuntimeError(f"Error HTTP Moodle: {response.status_code}") from e

    except requests.exceptions.RequestException as e:
        print(str(e))
        raise RuntimeError("Error general en request a Moodle") from e

    # --- Validar JSON ---
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Respuesta no es JSON válido")

    # --- Validar error lógico de Moodle ---
    if isinstance(data, dict) and "exception" in data:
        raise RuntimeError(f"Error Moodle: {data.get('message')}")

    return data