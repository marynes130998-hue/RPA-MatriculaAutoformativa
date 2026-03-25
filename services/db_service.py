from db.connection import get_connection
import pandas as pd
from db.queries import *

def execute_query(query, params=None, return_id=False):
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if return_id:
        result = cursor.fetchone()
        conn.commit()
        return int(result[0]) if result else None
 
    conn.commit()
    cursor.close()
    conn.close()

    return None

def execute_query_df(query, params):
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        raise RuntimeError(f"Error ejecutando query: {query[:100]}") from e
    finally:
        conn.close()

def crear_ejecucion(id_oferta, grupo, nro_matriculas):
    id_ejecucion = execute_query(
        INSERT_EJECUCION,
        (id_oferta, grupo, 1),  # PENDIENTE
        return_id=True
    )

    id_log = execute_query(
        INSERT_LOG_EJECUCION,
        (id_ejecucion, nro_matriculas, 1),  # PENDIENTE
        return_id=True
    )

    return id_ejecucion, id_log

def iniciar_ejecucion(id_ejecucion, id_log, nro_matriculas):
    execute_query(UPDATE_EJECUCION_ESTADO, (2, id_ejecucion))  # EN_EJECUCION
    execute_query(UPDATE_LOG_EJECUCION_ESTADO, (nro_matriculas, 2, id_log))

def iniciar_subproceso(id_log, id_subproceso, nro_matriculas):
    execute_query(INSERT_LOG_DETALLE_PENDIENTE, (id_log, id_subproceso, nro_matriculas))
    execute_query(INSERT_LOG_DETALLE_EJECUCION, (id_log, id_subproceso, nro_matriculas))

def finalizar_subproceso_ok(id_log, id_subproceso, nro_matriculas):
    execute_query(
        INSERT_LOG_DETALLE_OK,
        (id_log, id_subproceso, nro_matriculas)
    )

def finalizar_subproceso_error(id_log, id_subproceso, id_error, observacion, nro_matriculas):
    execute_query(
        INSERT_LOG_DETALLE_ERROR,
        (id_log, id_subproceso, nro_matriculas, id_error, observacion)
    )

def finalizar_ejecucion_ok(id_ejecucion, id_log, total_matriculas):
    execute_query(UPDATE_EJECUCION_FIN, (3, id_ejecucion))  # COMPLETADO

    execute_query(
        UPDATE_LOG_EJECUCION_OK,
        (total_matriculas, id_log)
    )

def finalizar_ejecucion_error(id_ejecucion, id_log, id_error, observacion, nro_matriculas):
    execute_query(UPDATE_EJECUCION_FIN, (4, id_ejecucion))  # ERROR

    execute_query(
        UPDATE_LOG_EJECUCION_ERROR,
        (nro_matriculas, id_error, observacion, id_log)
    )