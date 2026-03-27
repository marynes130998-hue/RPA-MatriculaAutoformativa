from db import queries
from services.db_service import execute_query

def get_sifods_enrolled_count(course_id):

    cantidad_matriculados = execute_query(queries.QUERY_OBTENER_NRO_MATRICULADOS_CURSO, 
        (course_id,), return_id=True) or 0

    return cantidad_matriculados