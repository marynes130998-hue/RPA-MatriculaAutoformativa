from repositorios.moodle_repository import get_moodle_enrolled_count
from repositorios.sifods_repository import get_sifods_enrolled_count
from services.log_service import logging
from services.db_service import *
from services.error_service import map_exception
from services.email_service import send_email_exito
from services.email_service import send_email_error

def validacion_matricula(id_map, row, validaciones):
    logger = logging.getLogger("Subproceso 4 - Validacion Matricula")

    try:
        logger.info("INICIO SUBPROCESO 4 - VALIDACION MATRICULA")

        course_id = row.curid_sifods
        id_oferta = row.ID_OFERTA_FORMATIVA
        nombre_oferta = row.NOMBRE_OFERTA
        nombre_grupo = row.NOMBRE_GRUPO
        tipo_oferta = row.tipo_oferta #PENDIENTE DE MODIFICAR AL AGREGAR A LA QUERY_INFO_PARTICIPANTE

        # ==============================================================
        # INSERTAR REGISTROS DE LOS CURSOS COMO PENDIENTE Y EN_EJECUCION
        # ==============================================================
        id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
        iniciar_subproceso(id_log, 4, 0)
            
        sifods_count = get_sifods_enrolled_count(course_id)
        moodle_count = get_moodle_enrolled_count(course_id)

        if sifods_count == moodle_count:
            status = "OK"

            finalizar_subproceso_ok(id_log, 4, moodle_count)
            finalizar_ejecucion_ok(id_ejecucion, id_log, moodle_count)
            logger.info(f"Validación correcta de matrícula {id_oferta} - {nombre_grupo}")

        else:
            status = "NOK"

            finalizar_subproceso_error(id_log, 4, 6, "Validación incorrecta de matrícula", moodle_count)
            finalizar_ejecucion_error(id_ejecucion, id_log, 6, "Validación incorrecta de matrícula", moodle_count)
            logger.error(f"Validación incorrecta de matrícula {id_oferta} - {nombre_grupo}")

        logger.info("FIN SUBPROCESO 4 - VALIDACION MATRICULA")

        validaciones.append({
            "course_id": course_id,
            "id_oferta": id_oferta,
            "nombre_oferta": nombre_oferta,
            "grupo": nombre_grupo,
            "tipo_oferta": tipo_oferta,
            "resultado": status,
            "correo_enviado": "NO"
        })
    
        return {
                "status": status,
                "validaciones": validaciones
            }
    
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
        finalizar_subproceso_error(id_log, 4, error_info["id"], str(e), 0)
        finalizar_ejecucion_error(id_ejecucion, id_log, error_info["id"], str(e), 0)

        send_email_error(error_info)

        validaciones.append({
            "course_id": course_id,
            "id_oferta": id_oferta,
            "nombre_oferta": nombre_oferta,
            "grupo": nombre_grupo,
            "tipo_oferta": tipo_oferta,
            "resultado": "ERROR",
            "correo_enviado": "NO"
        })

        return {
                "status": "ERROR",
                "validaciones": validaciones
            }

def enviar_correo(validaciones):
    logger = logging.getLogger("Subproceso 4 - Envío Correo")

    try:
        logger.info("INICIO SUBPROCESO 4 - ENVIO CORREO")

        if not validaciones:
            logger.warning("No hay validaciones para enviar correo a interesados")
            return

        if all(v["resultado"] == "ERROR" for v in validaciones):
            logger.error("Todos los cursos fallaron, no se envía correo")
            return

        for registro in validaciones:
            tipo_oferta = registro["tipo_oferta"].upper()
            resultado = registro["resultado"]
            id_oferta = registro["id_oferta"]
            correo_enviado = registro["correo_enviado"]

            if tipo_oferta == "CURSO" and resultado == "OK" :
                send_email_exito(registro)
                registro["correo_enviado"] = "SÍ"
            elif tipo_oferta == "PROGRAMA" and correo_enviado == "NO":
                validacion_OK = all(registro["resultado"] == "OK" for registro in validaciones
                if registro["id_oferta"] == id_oferta
                )
                if validacion_OK:
                    send_email_exito(registro)
                    for registro in validaciones:
                        if registro.get("id_oferta") == id_oferta:
                            registro["correo_enviado"] = "SÍ"

        logger.info("FIN SUBPROCESO 4 - ENVIO CORREO")

        return
    
    except Exception as e:
        logger.info(str(e))

        raise