from subp1.subproceso1 import obtener_inscritos

from subp2.subproceso2 import ejecutar_subproceso2
from subp2.subproceso2 import crear_usuarios

from subp3.subproceso3 import ejecutar_matricula
from subp4.subproceso4 import validacion_matricula, enviar_correo
from services.email_service import send_email_error, send_email_info
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import finalizar_ejecucion_error
from config.settings import MAX_REINTENTOS

from data_simulada.simulacion_data import obtener_inscritos_mock
def main():
    logger = logging.getLogger("Main")
    logger.info(f"Se inició ejecución del robot")

    intento = 0

    while intento < MAX_REINTENTOS:
        intento += 1
        logger.info(f"INTENTO GLOBAL N° {intento}")

        todo_ok = True

        try:
            # Subproceso 1
            registros, id_map, df_total, df_cursos = obtener_inscritos()

            # Subproceso 2
            registros, id_map, df_total, df_cursos = obtener_inscritos_mock()

            ejecutar_subproceso2(registros, id_map, df_cursos, df_total)

            #Subproceso 3
            ejecutar_matricula(registros, id_map, df_cursos, df_total)

            validaciones = []


            for row in df_cursos.itertuples(index=False):
                #Subproceso 4 - Parte 1
                result = validacion_matricula(id_map, row, validaciones)

            for row in df_cursos.itertuples(index=False):
                course_id = row.cur_id

                # Subproceso 4 - Parte 1
                result = validacion_matricula(id_map, row, validaciones)


                if result["status"] == "NOK":
                    todo_ok = False
                elif result["status"] == "ERROR":
                    id_oferta = row.id_oferta
                    nombre_grupo = row.nombre_grupo
                    
                    id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
                    finalizar_ejecucion_error(id_ejecucion, id_log, result["error_id"], result["excepcion"], 0)
                    return

            # Subproceso 4 - Parte 2
            enviar_correo(validaciones)

            # Información a Equipo
            send_email_info(validaciones)

            if todo_ok:
                logger.info("Todas las matrículas fueron validadas correctamente")
                break
            else:
                if intento < MAX_REINTENTOS:
                    logger.warning("Hay matrículas de cursos con error, se reintentará")
                else:
                    logger.warning("Hay matrículas de cursos con error, se llegó al máximo de reintentos")

            registros, id_map, df_total, df_cursos = obtener_inscritos()

            # Subproceso 2
            crear_usuarios(registros, id_map, df_cursos)

            # Subproceso 3
            ejecutar_matricula(registros, id_map, df_cursos, df_total)

            validaciones = []

            for row in df_cursos.itertuples(index=False):
                # Subproceso 4 - Parte 1
                result = validacion_matricula(id_map, row, validaciones)

                if result["status"] == "NOK":
                    todo_ok = False
                elif result["status"] == "ERROR":
                    id_oferta = row.id_oferta
                    nombre_grupo = row.nombre_grupo
                    
                    id_ejecucion, id_log = id_map[(id_oferta, nombre_grupo)]
                    finalizar_ejecucion_error(id_ejecucion, id_log, result["error_id"], result["excepcion"], 0)
                    return

            # Subproceso 4 - Parte 2
            enviar_correo(validaciones)

            # Información a Equipo
            send_email_info(validaciones)

            if todo_ok:
                logger.info("Todas las matrículas fueron validadas correctamente")
                break
            else:
                if intento < MAX_REINTENTOS:
                    logger.warning("Hay matrículas de cursos con error, se reintentará")
                else:
                    logger.warning("Hay matrículas de cursos con error, se llegó al máximo de reintentos")


        except Exception as e:
            error_info = map_exception(e)

            registros = [
                (row.id_oferta, row.nombre_grupo, error_info["id"])
                for row in df_cursos.itertuples(index=False)
            ]

            for id_oferta, grupo, id_error in registros:
                id_ejecucion, id_log = id_map[(id_oferta, grupo)]
                finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)

            logger.error(f"Se terminó ejecución del robot erróneamente")

            send_email_error(error_info)

            return

    logger.info(f"Se terminó ejecución del robot correctamente")

if __name__ == "__main__":
    main()