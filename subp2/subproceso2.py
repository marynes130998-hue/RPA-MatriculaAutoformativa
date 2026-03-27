<<<<<<< HEAD
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from services.sifods_api import consultar_documentos_existentes, crear_usuarios_sifods
from services.utils import *

def ejecutar_subproceso2(registros, id_map, df_cursos, df_total):

    logger = logging.getLogger("Subproceso 2")

    try:

        logger.info("INICIO SUBPROCESO 2")
        
        # 1. Obtener conteo
        conteo_por_grupo = obtener_conteo_por_grupo(df_total)
        
        # 2. Iniciar subproceso
        iniciar_subproceso2(registros, id_map, conteo_por_grupo)

        # 3. Validar usuarios
        documentos_inscritos, documentos_existentes, documentos_faltantes = validar_usuarios_sifods(df_total)

        # 4. Crear usuarios faltantes
        total_creados = crear_usuarios_faltantes(df_total, documentos_faltantes)

        # 5. Finalizar subproceso OK
        finalizar_subproceso2(registros, id_map, conteo_por_grupo)

        logger.info("FIN SUBPROCESO 2")

        return {
                    "documentos_inscritos": len(documentos_inscritos),
                    "documentos_existentes": len(documentos_existentes),
                    "documentos_faltantes": len(documentos_faltantes),
                    "usuarios_creados": total_creados,
                }

    except Exception as e:

            error_info = map_exception(e)

            logger.error(str(e))

            registros_error = [
                (row.id_oferta, row.nombre_grupo, error_info["id"])
                for row in df_cursos.itertuples(index=False)
            ]

            for id_oferta, grupo, id_error in registros_error:
                id_ejecucion, id_log = id_map[(id_oferta, grupo)]
                finalizar_subproceso_error(id_log, 2, id_error, str(e), 0)

            raise
=======
import pandas as pd
from db import queries, connection
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *

def crear_usuarios(registros, id_map, df_cursos):
    logger = logging.getLogger("Subproceso 2")

    try:
        logger.info(f"INICIO SUBPROCESO 2")

        # ==============================================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE y EN_EJECUCION
        # ==============================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            iniciar_subproceso(id_log, 2, 0)

        # ==================================================================
        # LUEGO DEL PASO N, INSERTAR REGISTROS DE LOS CURSOS COMO COMPLETADO
        # ==================================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_ok(id_log, 2, 0)

        logger.info(f"FIN SUBPROCESO 2")

        return None
    
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        registros = [
            (row.id_oferta, row.nombre_grupo, error_info["id"])
            for row in df_cursos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_error(id_log, 2, id_error, str(e), 0)

        raise
>>>>>>> 4ce25c6c44941afea40a2778625ec5b3d9f2642f
