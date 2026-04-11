import requests
from services.log_service import logging
from config.config import (
    SIFODS_API_TIMEOUT,
    URL_RENIEC,
    URL_PERFIL_DOCENTE,
)

logger = logging.getLogger("SIFODS API")

# APIs solo accesibles por red interna — no requieren token
_HEADERS = {"Content-Type": "application/json"}


# ============================================================
# HELPERS — DESENCRIPTADO
# ============================================================

def _desencriptar_reniec(param_encriptado):
    """
    Desencripta la respuesta de cualquier endpoint de la API RENIEC
    (sifods-comunes-api-cap) usando su endpoint de seguridad.

    POST {URL_RENIEC}/api/v1/servicio/comunes/seguridad/desencriptar/
    Body:  {"_param": "<valor encriptado>"}
    Retorna: dict con los datos en texto plano.
    """
    endpoint = f"{URL_RENIEC.rstrip('/')}/api/v1/servicio/comunes/seguridad/desencriptar"

    response = requests.post(
        endpoint,
        json={"_param": param_encriptado},
        headers=_HEADERS,
        timeout=SIFODS_API_TIMEOUT,
        verify=False,
    )
    response.raise_for_status()
    return response.json()


def _desencriptar_perfil_docente(param_encriptado):
    """
    Desencripta la respuesta de cualquier endpoint de la API Perfil Docente
    (sifods-perfildocente-api-cap) usando su endpoint de seguridad.

    POST {URL_PERFIL_DOCENTE}/api/v1/servicio/perfil/docente/seguridad/desencriptar/
    Body:  {"_param": "<valor encriptado>"}
    Retorna: dict con los datos en texto plano.
    """
    endpoint = f"{URL_PERFIL_DOCENTE.rstrip('/')}/api/v1/servicio/perfil/docente/seguridad/desencriptar"

    response = requests.post(
        endpoint,
        json={"_param": param_encriptado},
        headers=_HEADERS,
        timeout=SIFODS_API_TIMEOUT,
        verify=False,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# PASO 1 — CONSULTAR RENIEC
# ============================================================

def consultar_reniec(dni):
    """
    Consulta los datos de un docente en RENIEC y desencripta la respuesta.

    Flujo:
      1. GET consultaReniecDni?dni={dni}  →  {"_param": "encrypted..."}
      2. POST desencriptar/               →  {"nombres": ..., "dni": ..., ...}

    Parámetros:
        dni (str): Documento de identidad del docente.

    Retorna:
        dict: Datos del docente en texto plano.

    Lanza:
        RuntimeError: Ante error HTTP o respuesta inválida.
    """
    endpoint = f"{URL_RENIEC.rstrip('/')}/api/v1/servicio/comunes/reniec/consultaReniecDni"

    try:
        # Paso 1 — Obtener respuesta encriptada
        response = requests.get(
            endpoint,
            params={"dni": dni},
            headers=_HEADERS,
            timeout=SIFODS_API_TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()

        # Paso 2 — Desencriptar si la respuesta viene como _param
        if "_param" in data:
            data = _desencriptar_reniec(data["_param"])

        # Paso 3 — Extraer el dict de datos reales del wrapper {result, messages, data}
        if "data" in data and isinstance(data["data"], dict):
            if not data.get("result"):
                raise RuntimeError(f"RENIEC | Error en respuesta para DNI {dni}: {data.get('messages')}")
            data = data["data"]

        logger.info(f"RENIEC | DNI {dni} consultado y desencriptado OK")
        return data

    except requests.exceptions.Timeout:
        raise RuntimeError(f"RENIEC | Timeout al consultar DNI {dni}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"RENIEC | Error de conexión al consultar DNI {dni}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"RENIEC | Error HTTP {response.status_code} para DNI {dni}: {e}")
    except ValueError:
        raise RuntimeError(f"RENIEC | Respuesta no es JSON válido para DNI {dni}")


# ============================================================
# PASO 2 — MAPEAR DATOS RENIEC → PERFIL DOCENTE SIFODS
# ============================================================

def _formatear_fecha(fecha_str):
    """
    Convierte fecha DD/MM/YYYY (formato RENIEC) a ISO 8601 requerido por grabar.
    Retorna None si no se puede parsear.
    """
    from datetime import datetime
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(fecha_str.strip(), fmt).strftime("%Y-%m-%dT00:00:00")
        except (ValueError, AttributeError):
            continue
    return None


def mapear_datos(datos_reniec, correo="", direccion="", usuario=""):
    """
    Transforma la respuesta desencriptada de RENIEC al payload
    requerido por DocenteGeneralCreateCommand (endpoint grabar).

    Campos mapeados desde RENIEC:
        numeroDni        -> documentoIdentidad
        nombres          -> nombres
        apellidoPaterno  -> apellidoPaterno
        apellidoMaterno  -> apellidoMaterno
        direccion        -> direccion
        sexoId           -> tipoSexoId
        fechaNacimiento  -> fechaNacimiento (convertida a ISO 8601)

    Parámetros:
        datos_reniec (dict): Datos desencriptados de RENIEC.
        correo       (str) : Correo electrónico (desde BD).
        direccion    (str) : Dirección fallback si RENIEC no la devuelve.
        usuario      (str) : Usuario que registra.

    Retorna:
        dict: Payload listo para enviar a grabar.
    """
    fecha_raw = datos_reniec.get("fechaNacimiento", "")
    return {
        "id":                           0,
        "tipoDocumentoIdentidadId":     datos_reniec.get("tipoDocumentoIdentidadComunesId"),
        "documentoIdentidad":           str(datos_reniec.get("numeroDni", "")).strip(),
        "nombres":                      str(datos_reniec.get("nombres", "")).strip(),
        "apellidoPaterno":              str(datos_reniec.get("apellidoPaterno", "")).strip(),
        "apellidoMaterno":              str(datos_reniec.get("apellidoMaterno", "")).strip(),
        "correoElectronico":            correo,
        "direccion":                    str(datos_reniec.get("direccion", direccion)).strip(),
        "telefonoFijo":                 "",
        "telefonoMovil":                "",
        "fechaNacimiento":              _formatear_fecha(fecha_raw),
        "tipoSexoId":                   datos_reniec.get("tipoSexoComunesId"),
        "estado":                       1,
        "usuario":                      usuario,
        "idAcceso":                     0,
        "idInstitucion":                1,
    }


# ============================================================
# PASO 3 — CREAR DOCENTE EN SIFODS
# ============================================================

def crear_docente(datos_docente):
    """
    Crea un docente en SIFODS. El payload se envía en texto plano.
    Si la respuesta viene encriptada, la desencripta automáticamente.

    POST {URL_PERFIL_DOCENTE}/api/v1/servicio/perfil/docente/docente/grabar

    Parámetros:
        datos_docente (dict): Payload mapeado por mapear_datos().

    Retorna:
        dict: Respuesta desencriptada de la API.

    Lanza:
        RuntimeError: Ante error HTTP o respuesta inválida.
    """
    endpoint = f"{URL_PERFIL_DOCENTE.rstrip('/')}/api/v1/servicio/perfil/docente/docente/grabar"
    dni = datos_docente.get("documentoIdentidad", "?")

    try:
        response = requests.post(
            endpoint,
            json=datos_docente,
            headers=_HEADERS,
            timeout=SIFODS_API_TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()

        # Desencriptar si la respuesta viene como _param
        if "_param" in data:
            data = _desencriptar_perfil_docente(data["_param"])

        if not data.get("result", True):
            raise RuntimeError(f"SIFODS | Error al crear docente DNI {dni}: {data.get('messages')}")

        logger.info(f"SIFODS | Docente DNI {dni} creado OK (id={data.get('data')})")
        return data

    except requests.exceptions.Timeout:
        raise RuntimeError(f"SIFODS | Timeout al crear docente DNI {dni}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"SIFODS | Error de conexión al crear docente DNI {dni}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"SIFODS | Error HTTP {response.status_code} para DNI {dni}: {e}")
    except ValueError:
        raise RuntimeError(f"SIFODS | Respuesta no es JSON válido para DNI {dni}")


# ============================================================
# FLUJO COMPLETO: RENIEC → MAPEO → CREAR EN SIFODS
# ============================================================

def crear_usuarios_sifods(df_faltantes):
    """
    Para cada usuario faltante en SIFODS:
      1. Consulta y desencripta sus datos desde RENIEC.
      2. Mapea la respuesta al payload del perfil docente.
      3. Crea el docente en SIFODS vía API.

    Parámetros:
        df_faltantes (DataFrame): Filas con columnas USUARIO_DOCUMENTO,
                                  CORREO_LECTRONICO, etc.

    Retorna:
        int: Total de docentes creados exitosamente.
    """
    if df_faltantes is None or df_faltantes.empty:
        return 0

    total_creados = 0

    for row in df_faltantes.itertuples(index=False):
        dni    = str(getattr(row, "USUARIO_DOCUMENTO", "")).strip()
        correo = str(getattr(row, "CORREO_LECTRONICO", "") or "").strip()

        if not dni:
            logger.warning("Fila sin DNI, se omite")
            continue

        try:
            datos_reniec = consultar_reniec(dni)
            payload      = mapear_datos(datos_reniec, correo=correo, usuario="47900071")
            crear_docente(payload)
            total_creados += 1

        except RuntimeError as e:
            logger.error(f"Error procesando DNI {dni}: {e}")

    logger.info(f"SIFODS | Total docentes creados: {total_creados}/{len(df_faltantes)}")
    return total_creados
