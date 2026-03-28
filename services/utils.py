from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from services.sifods_api import consultar_documentos_existentes, crear_usuarios_sifods
from services.payload_builder import construir_payload_usuario
from services.common import *

#nueva funcion==============================================================

# Cantidad de inscritos por oferta/grupo para trazabilidad de estados
def obtener_conteo_por_grupo(df_total):
    return (
        df_total.groupby(["id_oferta", "nombre_grupo"])["usuario_documento"]
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


#validar usuarios en sifods
def validar_usuarios_sifods(df_total):

    documentos_inscritos = {
        normalizar_documento(doc)
        for doc in df_total["usuario_documento"].dropna().tolist()
        if normalizar_documento(doc)
    }

    documentos_existentes = consultar_documentos_existentes(list(documentos_inscritos))
    documentos_faltantes = documentos_inscritos - set(documentos_existentes)

    return documentos_inscritos, documentos_existentes, documentos_faltantes

#crear faltantes en sifods
def crear_usuarios_faltantes(df_total, documentos_faltantes):

    if not documentos_faltantes:
        return 0

    df_faltantes = (
        df_total[
            df_total["usuario_documento"].astype(str).str.strip().isin(documentos_faltantes)
        ]
        .drop_duplicates(subset=["usuario_documento"])
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