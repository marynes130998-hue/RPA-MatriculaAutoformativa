import pandas as pd
from db import queries, connection
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *

def obtener_inscritos():
    logger = logging.getLogger("Subproceso 1")

    try:
        logger.info(f"INICIO SUBPROCESO 1")

        conn = connection.get_connection()
        df_total = pd.read_sql(queries.QUERY_OBTENER_INFO_CURSO, conn)
        conn.close()

        if df_total.empty:
            logger.warning("No hay data para procesar")
            return None, None, df_total, None

        # ===============================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE
        # ===============================================
        df_cursos = df_total[["cur_id", "id_oferta","nombre_oferta","nombre_grupo", "tipo_oferta"]].drop_duplicates()

        registros = [
            (row.id_oferta, row.nombre_grupo)
            for row in df_cursos.itertuples(index=False)
        ]

        id_map = {}

        for id_oferta, grupo in registros:
            id_ejecucion, id_log = crear_ejecucion(id_oferta, grupo, 0)
            iniciar_ejecucion(id_ejecucion, id_log, 0)

            id_map[(id_oferta, grupo)] = (id_ejecucion, id_log)

        # ====================================================================
        # LUEGO DEL PASO 1, INSERTAR REGISTROS DE LOS CURSOS COMO EN_EJECUCION
        # ====================================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            iniciar_subproceso(id_log, 1, 0)
        
        # ==================================================================
        # LUEGO DEL PASO N, INSERTAR REGISTROS DE LOS CURSOS COMO COMPLETADO
        # ==================================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_ok(id_log, 1, 0)

        logger.info(f"FIN SUBPROCESO 1")

        return registros, id_map, df_total, df_cursos
    
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        registros = [
            (row.id_oferta, row.nombre_grupo, error_info["id"])
            for row in df_cursos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_error(id_log, 1, id_error, str(e), 0)
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)
        raise