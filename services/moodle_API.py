import requests
from config.settings import MOODLE_URL, MOODLE_TOKEN

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

    try:
        response = requests.get(MOODLE_URL, params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(str(e))
        raise RuntimeError("Error en llamada a Moodle") from e
    
    try:
        return response.json()
    except ValueError:
        raise RuntimeError("Respuesta no es JSON válido")