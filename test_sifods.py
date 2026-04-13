"""
Simulacion de todas las funciones del Subproceso 2.
Ejecutar desde la raiz del proyecto: python test_sifods.py
"""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd

# DNIs de prueba:
#   43363864 -> ya existe en SIFODS y Moodle
#   72621626 -> NO existe en SIFODS ni Moodle (para probar creacion)
DATA = [
    {
        "USUARIO_DOCUMENTO": "43363864",
        "NOMBRES":           "JOSEPH GIOVANNI",
        "APELLIDO_PATERNO":  "MAMANI",
        "APELLIDO_MATERNO":  "BARBAITO",
        "CORREO_LECTRONICO": "josephgiovannix@gmail.com",
    },
    {
        "USUARIO_DOCUMENTO": "72621626",
        "NOMBRES":           "ALESSANDRA VALERIA",
        "APELLIDO_PATERNO":  "MURGA",
        "APELLIDO_MATERNO":  "RIMAC",
        "CORREO_LECTRONICO": "oscarsantacruzh@gmail.com",
    },
]

df_total = pd.DataFrame(DATA)

print("=" * 60)
print("DataFrame de prueba:")
print(df_total.to_string(index=False))
print("=" * 60)

# ============================================================
# IMPORTAR FUNCIONES DEL SUBPROCESO 2
# ============================================================
from services.utils import (
    validar_usuarios_sifods,
    crear_usuarios_faltantes,
    validar_usuarios_moodle,
    crear_usuarios_moodle,
)

# ============================================================
# PASO 1: Validar usuarios en SIFODS
# ============================================================
print("\n[PASO 1] Validar usuarios en SIFODS")
inscritos, existentes_sifods, faltantes_sifods = validar_usuarios_sifods(df_total)
print(f"  Inscritos   : {inscritos}")
print(f"  Existentes  : {existentes_sifods}")
print(f"  Faltantes   : {faltantes_sifods}")

# ============================================================
# PASO 2: Crear usuarios faltantes en SIFODS
# ============================================================
print("\n[PASO 2] Crear usuarios faltantes en SIFODS")
if faltantes_sifods:
    total_sifods = crear_usuarios_faltantes(df_total, faltantes_sifods)
    print(f"  Creados: {total_sifods}/{len(faltantes_sifods)}")
else:
    print("  No hay usuarios faltantes en SIFODS")

# ============================================================
# PASO 3: Validar usuarios en Moodle — respuesta RAW
# ============================================================
print("\n[PASO 3] Validar usuarios en Moodle")
import requests, json
from config.config import BASE_URL_MOODLE, MOODLE_TOKEN
_ENDPOINT = f"{BASE_URL_MOODLE}/webservice/rest/server.php"

lista_docs = df_total["USUARIO_DOCUMENTO"].astype(str).tolist()
params_val = {
    "wstoken": MOODLE_TOKEN,
    "wsfunction": "core_user_get_users_by_field",
    "moodlewsrestformat": "json",
    "field": "username",
}
for idx, doc in enumerate(lista_docs):
    params_val[f"values[{idx}]"] = doc

r3 = requests.get(_ENDPOINT, params=params_val, timeout=30, verify=False)
print(f"  HTTP Status: {r3.status_code}")
print("  Respuesta RAW:")
try:
    print(json.dumps(r3.json(), indent=2, ensure_ascii=False))
except Exception:
    print(r3.text[:500])

_, existentes_moodle, faltantes_moodle = validar_usuarios_moodle(df_total)
print(f"  Existentes  : {existentes_moodle}")
print(f"  Faltantes   : {faltantes_moodle}")

# ============================================================
# PASO 4: Crear usuarios faltantes en Moodle — respuesta RAW
# ============================================================
print("\n[PASO 4] Crear usuarios faltantes en Moodle")
if faltantes_moodle:
    df_faltantes = (
        df_total[df_total["USUARIO_DOCUMENTO"].astype(str).str.strip().isin(faltantes_moodle)]
        .drop_duplicates(subset=["USUARIO_DOCUMENTO"])
    )
    for row in df_faltantes.itertuples(index=False):
        dni    = str(row.USUARIO_DOCUMENTO).strip()
        params_create = {
            "wstoken": MOODLE_TOKEN,
            "wsfunction": "core_user_create_users",
            "moodlewsrestformat": "json",
            "users[0][username]":  dni,
            "users[0][password]":  dni,
            "users[0][firstname]": str(row.NOMBRES).strip(),
            "users[0][lastname]":  f"{row.APELLIDO_PATERNO} {row.APELLIDO_MATERNO}".strip(),
            "users[0][email]":     str(row.CORREO_LECTRONICO).strip() or f"{dni}@minedu.gob.pe",
            "users[0][idnumber]":  dni,
            "users[0][auth]":      "manual",
        }
        r4 = requests.post(_ENDPOINT, data=params_create, timeout=30, verify=False)
        print(f"  DNI {dni} — HTTP Status: {r4.status_code}")
        print("  Respuesta RAW:")
        try:
            print(json.dumps(r4.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(r4.text[:500])

    total_moodle = crear_usuarios_moodle(df_total, faltantes_moodle)
    print(f"\n  Total creados via funcion: {total_moodle}/{len(faltantes_moodle)}")
else:
    print("  No hay usuarios faltantes en Moodle")

print("\n" + "=" * 60)
print("Resumen:")
print(f"  SIFODS  — existentes: {len(existentes_sifods)}, faltantes: {len(faltantes_sifods)}")
print(f"  Moodle  — existentes: {len(existentes_moodle)}, faltantes: {len(faltantes_moodle)}")
print("=" * 60)
