import pandas as pd
import json
import requests
from collections import defaultdict
from db import queries, connection
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from config.settings import *
from config.config import *

moodle_url = BASE_URL_MOODLE
moodle_apikey = MOODLE_TOKEN


def obtener_grupos_curso(moodle_url, moodle_apikey, course_id):
    endpoint = f"{moodle_url}/webservice/rest/server.php"
    params = {
        'wstoken': moodle_apikey,
        'wsfunction': 'core_group_get_course_groups',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        grupos = response.json()
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


def crear_grupo_faltante(moodle_url, moodle_apikey, course_id, group_name):
    endpoint = f"{moodle_url}/webservice/rest/server.php"
    params = {
        "wstoken": moodle_apikey,
        "wsfunction": "core_group_create_groups",
        "moodlewsrestformat": "json",
        "groups[0][courseid]": course_id,
        "groups[0][name]": group_name,
        "groups[0][description]": "",
    }
    try:
        response = requests.post(endpoint, data=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "exception" in data:
            raise RuntimeError(f"Moodle API: {data.get('message')}")
        return data[0]["id"]
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout creando grupo '{group_name}' en curso {course_id}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Error de conexión creando grupo '{group_name}' en curso {course_id}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Error HTTP creando grupo '{group_name}': {e}")
    except (IndexError, KeyError):
        raise RuntimeError(f"Respuesta inesperada al crear grupo '{group_name}'")
    except Exception as e:
        raise RuntimeError(f"Error inesperado creando grupo '{group_name}': {e}")


def matricular_estudiante(moodle_url, moodle_apikey, course_id, user_id, role_id):
    endpoint = f"{moodle_url}/webservice/rest/server.php"
    params = {
        "wstoken": moodle_apikey,
        "wsfunction": "enrol_manual_enrol_users",
        "moodlewsrestformat": "json",
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id,
    }
    try:
        response = requests.post(endpoint, data=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "exception" in data:
            raise RuntimeError(f"Moodle API: {data.get('message')}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout matriculando user_id {user_id} en curso {course_id}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Error de conexión matriculando user_id {user_id} en curso {course_id}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Error HTTP matriculando user_id {user_id}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado matriculando user_id {user_id}: {e}")


def asignar_estudiante_grupo(moodle_url, moodle_apikey, group_id, user_id):
    endpoint = f"{moodle_url}/webservice/rest/server.php"
    params = {
        "wstoken": moodle_apikey,
        "wsfunction": "core_group_add_group_members",
        "moodlewsrestformat": "json",
        "members[0][groupid]": group_id,
        "members[0][userid]": user_id,
    }
    try:
        response = requests.post(endpoint, data=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "exception" in data:
            raise RuntimeError(f"Moodle API: {data.get('message')}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout asignando user_id {user_id} al grupo {group_id}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Error de conexión asignando user_id {user_id} al grupo {group_id}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Error HTTP asignando user_id {user_id}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado asignando user_id {user_id}: {e}")


def verificar_grupo(moodle_url, moodle_apikey, group_id):
    endpoint = f"{moodle_url}/webservice/rest/server.php"
    params = {
        "wstoken": moodle_apikey,
        "wsfunction": "core_group_get_group_members",
        "moodlewsrestformat": "json",
        "groupids[0]": group_id,
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "exception" in data:
            raise RuntimeError(f"Moodle API: {data.get('message')}")
        return data
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout verificando grupo {group_id}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Error de conexión verificando grupo {group_id}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Error HTTP verificando grupo {group_id}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado verificando grupo {group_id}: {e}")


def ejecutar_matricula(registros, id_map, df_cursos, df_total):
    logger = logging.getLogger("Subproceso 3")
    try:
        logger.info("INICIO SUBPROCESO 3")

        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            iniciar_subproceso(id_log, 3, 0)

        cursos_unicos = df_cursos[["curid_sifods"]].drop_duplicates()
        total_por_grupo = defaultdict(int)

        for curso_row in cursos_unicos.itertuples(index=False):
            course_id = curso_row.curid_sifods
            df_curso_cursos = df_cursos[df_cursos["curid_sifods"] == course_id]
            df_curso_participantes = df_total[df_total["curid_sifods"] == course_id]

            grupos_existentes = obtener_grupos_curso(moodle_url, moodle_apikey, course_id)
            if grupos_existentes is None:
                raise RuntimeError(f"No se pudieron obtener grupos para el curso {course_id}")
            grupos_existentes_por_nombre = {g["name"]: g["id"] for g in grupos_existentes}
            logger.info(f"Curso {course_id} | Grupos existentes: {list(grupos_existentes_por_nombre.keys())}")

            grupo_id_map = {}
            for row in df_curso_cursos.itertuples(index=False):
                group_name = row.NOMBRE_GRUPO
                if group_name in grupos_existentes_por_nombre:
                    group_id = grupos_existentes_por_nombre[group_name]
                    logger.info(f"Curso {course_id} | Grupo '{group_name}' ya existe (id={group_id})")
                else:
                    group_id = crear_grupo_faltante(moodle_url, moodle_apikey, course_id, group_name)
                    logger.info(f"Curso {course_id} | Grupo '{group_name}' creado (id={group_id})")
                grupo_id_map[(row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO)] = group_id

            for part_row in df_curso_participantes.itertuples(index=False):
                documento = str(getattr(part_row, "USUARIO_DOCUMENTO", "")).strip()
                oferta = getattr(part_row, "ID_OFERTA_FORMATIVA", None)
                grupo_nombre = getattr(part_row, "NOMBRE_GRUPO", None)
                user_id = getattr(part_row, "userid", None)

                if not user_id:
                    logger.warning(f"Curso {course_id} | Documento {documento} sin userid en BD, se omite")
                    continue

                user_id = int(user_id)
                course_id = int(course_id)
                group_id = grupo_id_map.get((oferta, grupo_nombre))
                if group_id is None:
                    logger.warning(f"Curso {course_id} | Sin group_id para oferta {oferta} grupo {grupo_nombre}, se omite")
                    continue

                try:
                    matricular_estudiante(moodle_url, moodle_apikey, course_id, user_id, ROL_ESTUDIANTE)
                    asignar_estudiante_grupo(moodle_url, moodle_apikey, group_id, user_id)
                    total_por_grupo[(oferta, grupo_nombre)] += 1
                    logger.info(f"Curso {course_id} | DNI {documento} matriculado y asignado a '{grupo_nombre}' OK")
                except Exception as e:
                    logger.error(f"Curso {course_id} | Error matriculando DNI {documento}: {e}")

            for (oferta, grupo_nombre), group_id in grupo_id_map.items():
                try:
                    miembros = verificar_grupo(moodle_url, moodle_apikey, group_id)
                    nro_miembros = len(miembros[0]["userids"]) if miembros and len(miembros) > 0 and "userids" in miembros[0] else 0
                    logger.info(f"Curso {course_id} | Grupo '{grupo_nombre}' (id={group_id}) tiene {nro_miembros} miembros")
                except Exception as e:
                    logger.error(f"Curso {course_id} | Error verificando grupo '{grupo_nombre}': {e}")

        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            nro = total_por_grupo.get((id_oferta, grupo), 0)
            finalizar_subproceso_ok(id_log, 3, nro)

        logger.info("FIN SUBPROCESO 3")
        return None

    except Exception as e:
        error_info = map_exception(e)
        logger.info(str(e))

        registros_error = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, error_info["id"])
            for row in df_cursos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros_error:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_error(id_log, 3, id_error, str(e), 0)
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)
        raise
