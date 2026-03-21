from db import queries
from services.db_service import ejecutar_query

def get_sifods_enrolled_count(course_id):

    resultado = ejecutar_query(queries.QUERY_OBTENER_NRO_MATRICULADOS_CURSO, course_id)
    cantidad_matriculados = resultado[0] if resultado else 0

    return cantidad_matriculados