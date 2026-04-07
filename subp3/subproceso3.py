import pandas as pd
from db import queries, connection
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from config.settings import *
from config.config import *
import requests

moodle_url = BASE_URL_MOODLE
moodle_apikey = MOODLE_TOKEN
course_id = 1562

url = f"{moodle_url}/webservice/rest/server.php"

def obtener_grupos_curso(moodle_url, moodle_apikey, course_id):
    """
    Obtiene los grupos de un curso en Moodle
    
    Args:
        moodle_url (str): URL base de Moodle
        moodle_apikey (str): API key de Moodle
        course_id (int): ID del curso
    
    Returns:
        list: Lista de grupos o None si hay error
    """
    url = f"{moodle_url}/webservice/rest/server.php"
    
    params = {
        'wstoken': moodle_apikey,
        'wsfunction': 'core_group_get_course_groups',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        grupos = response.json()
        
        # Verificar si hay error de Moodle
        if isinstance(grupos, dict) and 'exception' in grupos:
            print(f"Error de Moodle: {grupos.get('message', 'Error desconocido')}")
            return None
        
        return grupos
        
    except requests.exceptions.Timeout:
        print("Error: Tiempo de espera agotado")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar con el servidor")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Respuesta no es JSON válido")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None


def ejecutar_matricula(registros, id_map, df_cursos, df_total):
    logger = logging.getLogger("Subproceso 3")

    try:
        logger.info(f"INICIO SUBPROCESO 3")

        # ==============================================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE y EN_EJECUCION
        # ==============================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            iniciar_subproceso(id_log, 3, 0)

        # ==============================================================
        # PASO 1: Verificar grupos creados core_group_get_course_groups 
        # ==============================================================
        
        grupos = obtener_grupos_curso(moodle_url, moodle_apikey, course_id)

        print("Grupos obtenidos del curso:")
        for grupo in grupos:
            print(f" - {grupo['name']}")
        # ==============================================================
        # PASO 2: Crear grupos en core_group_create_groups
        # ==============================================================

        # ==============================================================
        # PASO 3: Matricular estudiantes en core_enrol_manual_enrol_users
        # ==============================================================

        # ==============================================================
        # PASO 4: Asignar estudiantes en core_group_add_group_members
        # ==============================================================

        # ==============================================================
        # PASO 5: Verificar estudiantes matriculados core_group_get_group_members
        # ==============================================================


        

        # ==================================================================
        # LUEGO DEL PASO N, INSERTAR REGISTROS DE LOS CURSOS COMO COMPLETADO
        # ==================================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_ok(id_log, 3, 0)

        logger.info(f"FIN SUBPROCESO 3")

        return None
    
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, error_info["id"])
            for row in df_cursos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_error(id_log, 3, id_error, str(e), 0)
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)
        raise