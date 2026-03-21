from subp1.subproceso1 import obtener_inscritos
from subp2.subproceso2 import crear_usuarios
from subp3.subproceso3 import ejecutar_matricula
from subp4.subproceso4 import validacion_matricula
from services.email_service import send_email_exito, send_email_error
from services.log_service import logging
from services.error_service import map_exception
from services.db_service import *

def main():
    logger = logging.getLogger("Main")
    try:
        logger.info(f"Se inició ejecución del robot")

        # Subproceso 1
        registros, id_map, df_total, df_cursos, df_unicos = obtener_inscritos()

        # Subproceso 2
        crear_usuarios(registros, id_map, df_unicos)

        # Subproceso 3
        ejecutar_matricula(registros, id_map, df_unicos, df_total)

        for _,row in df_cursos.iterrows():
            course_id = row["cur_id"]
            id_oferta = row["id_oferta"]
            nombre_oferta = row["nombre_oferta"]
            nombre_grupo = row["nombre_grupo"]

            # Subproceso 4
            result = validacion_matricula(id_map, course_id, id_oferta, nombre_grupo)

            if (result["status"] == "OK"):
                logger.info(f"Validación correcta de la matrícula del curso{course_id}")
                send_email_exito(nombre_oferta, nombre_grupo, course_id)
            else:
                logger.info(f"Validación incorrecta de la matrícula del curso {course_id}")

        logger.info(f"Se terminó ejecución del robot correctamente")

    except Exception as e:
        error_info = map_exception(e)

        registros = [
            (row.id_oferta, row.nombre_grupo, error_info["id"])
            for row in df_unicos.itertuples(index=False)
        ]

        for id_oferta, grupo, id_error in registros:
            id_ejecucion, id_log = id_map[(id_oferta, grupo)]
            finalizar_ejecucion_error(id_ejecucion, id_log, id_error, str(e), 0)

        logger.error(f"Se terminó ejecución del robot erróneamente")

        send_email_error(error_info)

        return

if __name__ == "__main__":
    main()