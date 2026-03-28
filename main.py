from subp1.subproceso1 import obtener_inscritos
from subp2.subproceso2 import ejecutar_subproceso2
from subp3.subproceso3 import ejecutar_matricula
from subp4.subproceso4 import validacion_matricula, enviar_correo
from services.email_service import send_email_error, send_email_info, send_email_no_data
from services.log_service import logging
from services.error_service import map_exception
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

            if df_total.empty:
                send_email_no_data()
                return

            # Subproceso 2
            registros, id_map, df_total, df_cursos = obtener_inscritos_mock()
            ejecutar_subproceso2(registros, id_map, df_cursos, df_total)

            #Subproceso 3
            ejecutar_matricula(registros, id_map, df_cursos, df_total)

            validaciones = []
            for row in df_cursos.itertuples(index=False):
                #Subproceso 4 - Parte 1
                result = validacion_matricula(id_map, row, validaciones)
                
                if result["status"] == "NOK" or result["status"] == "ERROR":
                    todo_ok = False

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

            logger.error(f"Se terminó ejecución del robot erróneamente")

            send_email_error(error_info)

            continue

    logger.info(f"Se terminó ejecución del robot correctamente")

if __name__ == "__main__":
    main()