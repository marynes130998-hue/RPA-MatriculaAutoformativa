from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *
from services.utils import *

def ejecutar_subproceso2(registros, id_map, df_cursos, df_total):
    logger = logging.getLogger("Subproceso 2")

    try:
        logger.info("INICIO SUBPROCESO 2")

        # ==============================================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE y EN_EJECUCION
        # ==============================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            iniciar_subproceso(id_log, 2, 0)

        # 1. Validar usuarios en SIFODS
        documentos_inscritos, documentos_existentes, documentos_faltantes = validar_usuarios_sifods(df_total)

        # 2. Crear usuarios faltantes en SIFODS
        total_creados_sifods = crear_usuarios_faltantes(df_total, documentos_faltantes)

        # 3. Validar usuarios en Moodle
        _, existentes_moodle, faltantes_moodle = validar_usuarios_moodle(df_total)

        # 4. Crear usuarios faltantes en Moodle
        total_creados_moodle = crear_usuarios_moodle(df_total, faltantes_moodle)

        # ==================================================================
        # LUEGO DEL PASO N, INSERTAR REGISTROS DE LOS CURSOS COMO COMPLETADO
        # ==================================================================
        for id_oferta, grupo in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_ok(id_log, 2, 0)

        logger.info("FIN SUBPROCESO 2")

        return {
                    "documentos_inscritos":      len(documentos_inscritos),
                    "documentos_existentes":     len(documentos_existentes),
                    "documentos_faltantes":      len(documentos_faltantes),
                    "usuarios_creados_sifods":   total_creados_sifods,
                    "existentes_moodle":         len(existentes_moodle),
                    "faltantes_moodle":          len(faltantes_moodle),
                    "usuarios_creados_moodle":   total_creados_moodle,
                }

    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, error_info["id"])
            for row in df_cursos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_subproceso_error(id_log, 2, id_error, str(e), 0)
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)
        raise