# ============================================================
# BASE DE DATOS
# ============================================================
SERVER = "localhost"
DATABASE = "db_automatizacion"

# ============================================================
# MOODLE
# ============================================================
MOODLE_URL = "https://campusvirtual-sifods.minedu.gob.pe/webservice/rest/server.php"
MOODLE_TOKEN = "365d5e601bd29d6e983e643c513dfb0d"

# ============================================================
# GMAIL
# ============================================================
# Destinatarios para correo error API
EMAIL_DESTINATARIOS = ["marynes130998@gmail.com"]
# Configuración del correo éxito
# settings.py
EMAIL_CONFIG = {
    "subject_text": "Estimados,",
    "intro_text": "Respecto a lo mencionado, se remite el siguiente cuadro con el detalle de los estudiantes matriculados, para su revisión y conocimiento:",
    "footer_text": "Se envía el detalle en el Excel adjunto.",
    "signature": [
        "Saludos cordiales,",
        "Equipo de Automatización",
        "DIFODS TI"
    ],
    "table": {
        "header_1": "OBSERVACIÓN TI",
        "header_2": "CANTIDAD",
        "total_label": "MATRICULADOS",
        "row_color": "#6fbf3a"
    }
}

# ============================================================
# API
# ============================================================
# Destinatarios para correo error API
nro_limit = 2000

# ============================================================
# CONFIGURACIÓN DEL ROBOT
# ============================================================
ROL_ESTUDIANTE = 5
MAX_REINTENTOS = 3