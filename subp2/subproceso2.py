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
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)
        raise