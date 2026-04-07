import requests
from config.config import (
    SIFODS_API_BASE_URL,
    SIFODS_API_TOKEN,
    SIFODS_API_TIMEOUT,
    SIFODS_API_BATCH_SIZE,
)


def _build_headers():
    headers = {"Content-Type": "application/json"}
    if SIFODS_API_TOKEN:
        headers["Authorization"] = f"Bearer {SIFODS_API_TOKEN}"
    return headers


def _chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _validate_base_url():
    if not SIFODS_API_BASE_URL:
        raise RuntimeError(
            "API SIFODS no configurada. Definir SIFODS_API_BASE_URL en config/settings.py"
        )


# def consultar_documentos_existentes(documentos):
#     """
#     Consulta existencia de usuarios por documento en API SIFODS.

#     Contrato esperado (ajustable según API real):
#       POST {base_url}/usuarios/existencia
#       body: {"documentos": ["123", ...]}
#       response: {"documentos_existentes": ["123", ...]}
#     """
#     if not documentos:
#         return set()

#     _validate_base_url()

#     endpoint = f"{SIFODS_API_BASE_URL.rstrip('/')}/usuarios/existencia"
#     headers = _build_headers()

#     existentes = set()

#     for batch in _chunked(documentos, SIFODS_API_BATCH_SIZE):
#         resp = requests.post(
#             endpoint,
#             json={"documentos": batch},
#             headers=headers,
#             timeout=SIFODS_API_TIMEOUT,verify=False
#         )
#         resp.raise_for_status()
#         data = resp.json()

#         docs = (
#             data.get("documentos_existentes")
#             or data.get("documentos")
#             or data.get("data")
#             or []
#         )

#         if isinstance(docs, list):
#             for d in docs:
#                 if isinstance(d, dict):
#                     doc = d.get("documento") or d.get("dni") or d.get("username")
#                     if doc:
#                         existentes.add(str(doc).strip())
#                 else:
#                     existentes.add(str(d).strip())

#     return existentes


def crear_usuarios_sifods(usuarios):
    """
    Crea usuarios faltantes en API SIFODS.

    Contrato esperado (ajustable según API real):
      POST {base_url}/usuarios
      body: {"usuarios": [{...}, ...]}
    """
    if not usuarios:
        return 0

    _validate_base_url()

    endpoint = f"{SIFODS_API_BASE_URL.rstrip('/')}/usuarios"
    headers = _build_headers()

    total_creados = 0

    for batch in _chunked(usuarios, SIFODS_API_BATCH_SIZE):
        resp = requests.post(
            endpoint,
            json={"usuarios": batch},
            headers=headers,
            timeout=SIFODS_API_TIMEOUT,verify=False
        )
        resp.raise_for_status()

        try:
            data = resp.json()
            creados = (
                data.get("creados")
                or data.get("usuarios_creados")
                or data.get("data")
                or []
            )

            if isinstance(creados, int):
                total_creados += creados
            elif isinstance(creados, list):
                total_creados += len(creados)
            else:
                total_creados += len(batch)

        except ValueError:
            # Si la API no retorna JSON, asumimos éxito por código HTTP.
            total_creados += len(batch)

    return total_creados
