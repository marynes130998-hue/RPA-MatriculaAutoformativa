
#limpiar y estandarizar el documento del usuario
def normalizar_documento(valor):
    if valor is None:
        return ""
    return str(valor).strip()