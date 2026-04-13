import requests
from services.log_service import logging

from services.db_service import *
from services.sifods_api import crear_usuarios_sifods
from services.common import *
from db.connection import get_connection
from db.queries import QUERY_VERIFICAR_USUARIOS_SIFODS
from config.config import BASE_URL_MOODLE, MOODLE_TOKEN

logger = logging.getLogger("Utils")

_MOODLE_ENDPOINT = f"{BASE_URL_MOODLE}/webservice/rest/server.php"


# ==============================================================
# VALIDAR USUARIOS EN SIFODS (BD)
# ==============================================================
def validar_usuarios_sifods(df_total):
    """
    Verifica qué usuarios ya existen en SIFODS consultando directamente
    la tabla [db_sifods_bi].[dm].[stge_sfds_docente_general] por BD.

    Retorna:
        documentos_inscritos  (set): Todos los documentos a matricular.
        documentos_existentes (set): Los que ya existen en SIFODS.
        documentos_faltantes  (set): Los que NO existen y deben crearse.
    """
    documentos_inscritos = {
        normalizar_documento(doc)
        for doc in df_total["USUARIO_DOCUMENTO"].dropna().tolist()
        if normalizar_documento(doc)
    }

    if not documentos_inscritos:
        return set(), set(), set()

    lista_docs = list(documentos_inscritos)
    valores_sql = ",".join(f"'{doc}'" for doc in lista_docs)
    query = QUERY_VERIFICAR_USUARIOS_SIFODS.format(valores=valores_sql)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    filas = cursor.fetchall()
    conn.close()

    documentos_existentes = {str(fila[0]).strip() for fila in filas}
    documentos_faltantes = documentos_inscritos - documentos_existentes

    return documentos_inscritos, documentos_existentes, documentos_faltantes


# ==============================================================
# CREAR USUARIOS FALTANTES EN SIFODS (API)
# ==============================================================
def crear_usuarios_faltantes(df_total, documentos_faltantes):

    if not documentos_faltantes:
        return 0

    df_faltantes = (
        df_total[
            df_total["USUARIO_DOCUMENTO"].astype(str).str.strip().isin(documentos_faltantes)
        ]
        .drop_duplicates(subset=["USUARIO_DOCUMENTO"])
        .copy()
    )

    return crear_usuarios_sifods(df_faltantes)


# ==============================================================
# VALIDAR USUARIOS EN MOODLE (API)
# ==============================================================
def validar_usuarios_moodle(df_total):
    """
    Verifica qué usuarios ya existen en Moodle consultando por username
    (que en SIFODS equivale al USUARIO_DOCUMENTO/DNI).

    Retorna:
        documentos_inscritos  (set): Todos los documentos a matricular.
        documentos_existentes (set): Los que ya tienen cuenta en Moodle.
        documentos_faltantes  (set): Los que NO tienen cuenta y deben crearse.
    """
    documentos_inscritos = {
        normalizar_documento(doc)
        for doc in df_total["USUARIO_DOCUMENTO"].dropna().tolist()
        if normalizar_documento(doc)
    }

    if not documentos_inscritos:
        return set(), set(), set()

    documentos_existentes = set()
    lista_docs = list(documentos_inscritos)

    # Moodle permite consultar hasta 50 usuarios por llamada con get_users_by_field
    BATCH = 50
    for i in range(0, len(lista_docs), BATCH):
        lote = lista_docs[i:i + BATCH]
        params = {
            "wstoken": MOODLE_TOKEN,
            "wsfunction": "core_user_get_users_by_field",
            "moodlewsrestformat": "json",
            "field": "username",
        }
        for idx, doc in enumerate(lote):
            params[f"values[{idx}]"] = doc

        try:
            response = requests.get(_MOODLE_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "exception" in data:
                raise RuntimeError(f"Moodle API: {data.get('message')}")

            for user in data:
                documentos_existentes.add(str(user.get("username", "")).strip())

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Moodle | Error consultando usuarios: {e}")

    documentos_faltantes = documentos_inscritos - documentos_existentes
    logger.info(
        f"Moodle | Inscritos: {len(documentos_inscritos)} | "
        f"Existentes: {len(documentos_existentes)} | "
        f"Faltantes: {len(documentos_faltantes)}"
    )
    return documentos_inscritos, documentos_existentes, documentos_faltantes


# ==============================================================
# CREAR USUARIOS FALTANTES EN MOODLE (API)
# ==============================================================
def crear_usuarios_moodle(df_total, documentos_faltantes):
    """
    Crea en Moodle los usuarios que no tienen cuenta.
    Username y password se establecen como el DNI del docente.
    El correo se toma de CORREO_LECTRONICO.

    Retorna:
        int: Total de usuarios creados exitosamente.
    """
    if not documentos_faltantes:
        return 0

    df_faltantes = (
        df_total[
            df_total["USUARIO_DOCUMENTO"].astype(str).str.strip().isin(documentos_faltantes)
        ]
        .drop_duplicates(subset=["USUARIO_DOCUMENTO"])
        .copy()
    )

    total_creados = 0

    for row in df_faltantes.itertuples(index=False):
        dni      = str(getattr(row, "USUARIO_DOCUMENTO", "")).strip()
        nombres  = str(getattr(row, "NOMBRES", "") or "").strip()
        ap_pat   = str(getattr(row, "APELLIDO_PATERNO", "") or "").strip()
        ap_mat   = str(getattr(row, "APELLIDO_MATERNO", "") or "").strip()
        correo   = str(getattr(row, "CORREO_LECTRONICO", "") or "").strip()

        if not dni:
            continue

        params = {
            "wstoken": MOODLE_TOKEN,
            "wsfunction": "core_user_create_users",
            "moodlewsrestformat": "json",
            "users[0][username]":  dni,
            "users[0][password]":  dni,
            "users[0][firstname]": nombres,
            "users[0][lastname]":  f"{ap_pat} {ap_mat}".strip(),
            "users[0][email]":     correo if correo else f"{dni}@minedu.gob.pe",#modificar
            "users[0][idnumber]":  dni,
            "users[0][auth]":      "manual",
        }

        try:
            response = requests.post(_MOODLE_ENDPOINT, data=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "exception" in data:
                raise RuntimeError(f"Moodle API: {data.get('message')}")

            logger.info(f"Moodle | Usuario DNI {dni} creado OK (id={data[0].get('id')})")
            total_creados += 1

        except RuntimeError as e:
            logger.error(f"Moodle | Error creando DNI {dni}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Moodle | Error de red para DNI {dni}: {e}")

    logger.info(f"Moodle | Total usuarios creados: {total_creados}/{len(df_faltantes)}")
    return total_creados
