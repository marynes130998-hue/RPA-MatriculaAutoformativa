from services.moodle_API import call_moodle_api
from config.settings import nro_limit, ROL_ESTUDIANTE

def get_moodle_enrolled_count(course_id):
    total_estudiantes = 0
    offset = 0
    limit = nro_limit
    MAX_PAGINAS = 1000
    paginas = 0
    
    try:
        while paginas < MAX_PAGINAS:
            users = call_moodle_api("core_enrol_get_enrolled_users", course_id, offset, limit)

            if not users:
                break
            
            # filtrar roleid estudiante
            total_estudiantes += sum(
                1 for u in users
                if any(r["roleid"] == ROL_ESTUDIANTE for r in u.get("roles", []))
            )

            # avanzar página
            offset += limit
            paginas += 1
        
        if paginas == MAX_PAGINAS:
            raise RuntimeError("Posible loop infinito en paginación Moodle")

        return total_estudiantes
    
    except Exception as e:
        raise RuntimeError(f"Error consultando Moodle para course_id = {course_id}") from e