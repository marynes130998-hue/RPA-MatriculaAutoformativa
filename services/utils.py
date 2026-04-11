from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from services.sifods_api import crear_usuarios_sifods
from services.common import *
from db.connection import get_connection
from db.queries import QUERY_VERIFICAR_USUARIOS_SIFODS

# ==============================================================
# INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE y EN_EJECUCION
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

    # Embebemos los valores directamente como literales en el IN.
    # Esto evita el límite de 2100 parámetros de pyodbc/SQL Server.
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

# Crear faltantes en SIFODS via API
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

    # Pasa el DataFrame directamente: sifods_api consulta RENIEC por cada DNI
    return crear_usuarios_sifods(df_faltantes)