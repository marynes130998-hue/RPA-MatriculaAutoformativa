from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from services.sifods_api import crear_usuarios_sifods
from services.payload_builder import construir_payload_usuario
from services.common import *
from db.connection import get_connection
from db.queries import QUERY_VERIFICAR_USUARIOS_SIFODS


# Cantidad de inscritos por oferta/grupo para trazabilidad de estados
def obtener_conteo_por_grupo(df_total):
    return (
        df_total.groupby(["ID_OFERTA_FORMATIVA", "NOMBRE_GRUPO"])["USUARIO_DOCUMENTO"]
        .nunique()
        .to_dict()
    )


# ==============================================================
# INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE y EN_EJECUCION
# ==============================================================
def iniciar_subproceso2(registros, id_map, conteo_por_grupo):
    for id_oferta, grupo in registros:
        id_ejecucion, id_log = id_map[(id_oferta, grupo)]
        nro_inscritos = int(conteo_por_grupo.get((id_oferta, grupo), 0))
        iniciar_subproceso(id_log, 2, nro_inscritos)


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

    # Construir placeholders dinámicos para el IN (?,?,?...)
    lista_docs = list(documentos_inscritos)
    placeholders = ",".join(["?" for _ in lista_docs])
    query = QUERY_VERIFICAR_USUARIOS_SIFODS.format(placeholders=placeholders)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(lista_docs))  # pyodbc requiere tuple, no list
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

    usuarios_a_crear = [
        construir_payload_usuario(row)
        for row in df_faltantes.itertuples(index=False)
    ]

    return crear_usuarios_sifods(usuarios_a_crear)


def finalizar_subproceso2(registros, id_map, conteo_por_grupo):

    for id_oferta, grupo in registros:
        id_ejecucion, id_log = id_map[(id_oferta, grupo)]
        nro_inscritos = int(conteo_por_grupo.get((id_oferta, grupo), 0))
        finalizar_subproceso_ok(id_log, 2, nro_inscritos)
