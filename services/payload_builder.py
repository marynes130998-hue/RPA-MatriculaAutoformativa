from services.common import normalizar_documento

#construir el payload (estructura de datos) del usuario
def construir_payload_usuario(row):
    return {
        "documento": normalizar_documento(getattr(row, "usuario_documento", "")),
        "nombres": str(getattr(row, "nombres", "") or "").strip(),
        "apellido_paterno": str(getattr(row, "apellido_paterno", "") or "").strip(),
        "apellido_materno": str(getattr(row, "apellido_materno", "") or "").strip(),
        "correo_electronico": str(getattr(row, "correo_electronico", "") or "").strip(),
        "telefono": str(getattr(row, "telefono", "") or "").strip(),
    }