"""
Test: 1) crear DNI 72621626, 2) intentar crearlo de nuevo (duplicado).
Ejecutar desde la raiz del proyecto: python test_sifods.py
"""
import json
import warnings
warnings.filterwarnings("ignore")
from config.config import URL_RENIEC, URL_PERFIL_DOCENTE
from services.sifods_api import consultar_reniec, mapear_datos, crear_docente

DNI_PRUEBA = "72621626"

print(f"URL_RENIEC        : {URL_RENIEC}")
print(f"URL_PERFIL_DOCENTE: {URL_PERFIL_DOCENTE}")

# Obtener datos RENIEC y payload
datos_reniec = consultar_reniec(DNI_PRUEBA)
payload = mapear_datos(datos_reniec, correo="oscarsantacruzh@gmail.com", usuario="47900071")
print("\nPayload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

# ============================================================
# PRUEBA 1: Crear usuario (no existe)
# ============================================================
print("\n========== PRUEBA 1: Crear usuario nuevo ==========")
try:
    resp = crear_docente(payload)
    print(f"Resultado: {json.dumps(resp, indent=2, ensure_ascii=False)}")
except RuntimeError as e:
    print(f"ERROR: {e}")

# ============================================================
# PRUEBA 2: Intentar crear el mismo usuario (duplicado)
# ============================================================
print("\n========== PRUEBA 2: Crear usuario duplicado ==========")
try:
    resp2 = crear_docente(payload)
    print(f"Resultado: {json.dumps(resp2, indent=2, ensure_ascii=False)}")
except RuntimeError as e:
    print(f"ERROR (esperado): {e}")
