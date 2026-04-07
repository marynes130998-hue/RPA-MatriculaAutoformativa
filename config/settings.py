import os
from dotenv import load_dotenv #seguridad de credenciales

load_dotenv() 

# ============================================================
# BASE DE DATOS
# ============================================================
SERVER = "PCPOPRDIFOD132"
DATABASE = "db_automatizacion"

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
# API MOODLE
# ============================================================
# Límite por llamada
nro_limit = 2000


# ============================================================
# API SIFODS (Subproceso 2)
# ============================================================
# Nota: ajustar según contrato real del servicio
# - Endpoint validación existencia: {SIFODS_API_BASE_URL}/usuarios/existencia
#   Body esperado: {"documentos": ["12345678", ...]}
#   Respuesta esperada: {"documentos_existentes": ["12345678", ...]}
# - Endpoint creación: {SIFODS_API_BASE_URL}/usuarios
#   Body esperado: {"usuarios": [{...}, ...]}
# # SIFODS_API_BASE_URL = ""
# # SIFODS_API_TOKEN = ""
# # SIFODS_API_TIMEOUT = 30
# # SIFODS_API_BATCH_SIZE = 500

# ============================================================
# CONFIGURACIÓN DEL ROBOT
# ============================================================
ROL_ESTUDIANTE = 5
MAX_REINTENTOS = 3

#=============================================================
# DEFINICION DE ENVIRONMENT PARA URL DE APIS
#=============================================================
ENV = os.getenv("ENV")

#SIFODS
BASE_URL_SIFODS_ACCIONES_FORMATIVAS_CAP = os.getenv("BASE_URL_SIFODS_ACCIONES_FORMATIVAS_CAP")
BASE_URL_SIFODS_ADMINISTRADOR_PLATAFORMA_CAP = os.getenv("BASE_URL_SIFODS_ADMINISTRADOR_PLATAFORMA_CAP")

BASE_URL_SIFODS_ACCIONES_FORMATIVAS_PROD = os.getenv("BASE_URL_SIFODS_ACCIONES_FORMATIVAS_PROD")
BASE_URL_SIFODS_ADMINISTRADOR_PLATAFORMA_PROD = os.getenv("BASE_URL_ADMINISTRADOR_PLATAFORMA_PROD")

#MOODLE
BASE_URL_MOODLE_PROD = os.getenv("BASE_URL_MOODLE_PROD")
BASE_URL_MOODLE_CAP = os.getenv("BASE_URL_MOODLE_CAP")

MOODLE_TOKEN_DEV=os.getenv("MOODLE_TOKEN_DEV")
MOODLE_TOKEN_PROD=os.getenv("MOODLE_TOKEN_PROD")
