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

# API SIFODS (Subproceso 2)
# Nota: ajustar según contrato real del servicio
# - Endpoint validación existencia: {SIFODS_API_BASE_URL}/usuarios/existencia
#   Body esperado: {"documentos": ["12345678", ...]}
#   Respuesta esperada: {"documentos_existentes": ["12345678", ...]}
# - Endpoint creación: {SIFODS_API_BASE_URL}/usuarios
#   Body esperado: {"usuarios": [{...}, ...]}
SIFODS_API_BASE_URL = ""
SIFODS_API_TOKEN = ""
SIFODS_API_TIMEOUT = 30
SIFODS_API_BATCH_SIZE = 500

# ============================================================
# CONFIGURACIÓN DEL ROBOT
# ============================================================
ROL_ESTUDIANTE = 5
MAX_REINTENTOS = 3


#=============================================================
# CONFIGURACION VARIABLES DE ENV
#=============================================================
ENV = "CAP"   # DEV / PROD

if ENV == "CAP":
    BASE_URL_ACCIONES_FORMATIVAS = "https://sifods-accionesformativasmoodle-api-cap.minedu.gob.pe"
    BASE_URL_ADMINISTRADOR_PLATAFORMA = "https://sifods-administradorplataforma-api-cap.minedu.gob.pe"
    BASE_URL_MOODLE = "https://campusvirtual-sifods.minedu.gob.pe"

elif ENV == "PROD":
    BASE_URL_ACCIONES_FORMATIVAS = "https://sifods-accionesformativasmoodle-api.minedu.gob.pe"
    BASE_URL_ADMINISTRADOR_PLATAFORMA = "https://sifods-administradorplataforma-api.minedu.gob.pe"
    BASE_URL_MOODLE = "https://campusvirtual-sifods.minedu.gob.pe"


import os
from dotenv import load_dotenv #seguridad de credenciales

load_dotenv()

ENV = os.getenv("ENV")

SIFODS_URL_DEV = os.getenv("SIFODS_URL_DEV")
SIFODS_URL_PROD = os.getenv("SIFODS_URL_PROD")

SIFODS_TOKEN_DEV = os.getenv("SIFODS_TOKEN_DEV")
SIFODS_TOKEN_PROD = os.getenv("SIFODS_TOKEN_PROD")

