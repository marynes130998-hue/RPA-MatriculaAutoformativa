from repositorios.moodle_repository import get_moodle_enrolled_count
from repositorios.sifods_repository import get_sifods_enrolled_count
from services.log_service import logging
from services.db_service import *
from services.error_service import map_exception

def validacion_matricula(id_map, course_id, id_oferta, nombre_grupo):
    logger = logging.getLogger("Subproceso 4")

    try:
        logger.info("INICIO SUBPROCESO 4")

        # ==============================================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE Y EN_EJECUCION
        # ==============================================================
        id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
        iniciar_subproceso(id_log, 4, 0)
            
        sifods_count = get_sifods_enrolled_count(course_id)
        moodle_count = get_moodle_enrolled_count(course_id)

        if sifods_count == moodle_count:
            result = {
                "status": "OK",
                "difference": 0
            }

            finalizar_subproceso_ok(id_log, 4, moodle_count)
            finalizar_ejecucion_ok(id_ejecucion, id_log, moodle_count)
            logger.info(f"Validación correcta de matrícula {id_oferta} - {nombre_grupo}")

        else:
            result = {
                "status": "DIFFERENT",
                "difference": sifods_count - moodle_count
            }

            finalizar_subproceso_error(id_log, 4, 6, "Validación incorrecta de matrícula", moodle_count)
            finalizar_ejecucion_error(id_ejecucion, id_log, 6, "Validación incorrecta de matrícula", moodle_count)
            logger.error(f"Validación incorrecta de matrícula {id_oferta} - {nombre_grupo}")

        logger.info("FIN SUBPROCESO 4")

        return {
            "course_id": course_id,
            "sifods": sifods_count,
            "moodle": moodle_count,
            "difference": result["difference"],
            "status": result["status"]
        }
    
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
        finalizar_subproceso_error(id_log, 4, error_info["id"], str(e), 0)

        raise