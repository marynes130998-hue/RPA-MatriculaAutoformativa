# RPA - Matrícula Autoformativa (SIFODS)

Automatización del proceso de matrícula para ofertas autoformativas, integrando validaciones entre **SIFODS** y **Moodle**, registro de trazabilidad en base de datos y envío de correos de notificación/reporte.

## Descripción general

Este proyecto implementa un flujo RPA en Python dividido por subprocesos:

1. **Subproceso 1**: Obtiene inscritos desde BD y crea/inicia registros de ejecución.
2. **Subproceso 2**: Valida usuarios en SIFODS y crea los faltantes vía API.
3. **Subproceso 3**: Ejecuta la matrícula (estructura preparada para implementación/ajustes).
4. **Subproceso 4**: Valida cantidad de matriculados entre SIFODS y Moodle y envía correos de éxito/información.

Además, maneja errores centralizados, reintentos globales y notificaciones por correo cuando ocurre una falla.

---

## Estructura del proyecto

```text
RPA-MatriculaAutoformativa/
├── main.py
├── config/
│   ├── config.py
│   └── settings.py
├── db/
│   ├── connection.py
│   └── queries.py
├── repositorios/
│   ├── moodle_repository.py
│   └── sifods_repository.py
├── services/
│   ├── db_service.py
│   ├── email_service.py
│   ├── error_service.py
│   ├── log_service.py
│   ├── moodle_API.py
│   ├── payload_builder.py
│   ├── sifods_api.py
│   └── utils.py
├── subp1/subproceso1.py
├── subp2/subproceso2.py
├── subp3/subproceso3.py
├── subp4/subproceso4.py
├── data_simulada/simulacion_data.py
├── recursos/destinatarios_correo.xlsx
└── logs/
```

---

## Requisitos

- **Python 3.10+**
- Windows (usa autenticación integrada para SQL Server en la conexión actual)
- **ODBC Driver 17 for SQL Server**
- Acceso a:
  - Base de datos SQL Server
  - API de SIFODS
  - Moodle (según repositorios/servicios)
  - API de Gmail (para envío de correo)

### Dependencias Python usadas

Instala (según tu entorno) al menos:

- `pandas`
- `pyodbc`
- `requests`
- `python-dotenv`
- `google-api-python-client`
- `google-auth`
- `google-auth-oauthlib`
- `openpyxl`
- `xlsxwriter`

> Recomendado: crear un `requirements.txt` para fijar versiones en tu equipo/entorno CI.

---

## Configuración

### 1) Variables y settings

Revisar/ajustar `config/settings.py`:

- Conexión BD (`SERVER`, `DATABASE`)
- Endpoints/tokens de SIFODS y Moodle
- Configuración de correos (`EMAIL_DESTINATARIOS`, `EMAIL_CONFIG`)
- Parámetros de ejecución (`MAX_REINTENTOS`, lotes, timeouts)

`config/config.py` selecciona `BASE_URL` y `TOKEN` según `ENV`.

### 2) Archivo `.env`

Define al menos:

```env
ENV=DEV
SIFODS_URL_DEV=
SIFODS_URL_PROD=
SIFODS_TOKEN_DEV=
SIFODS_TOKEN_PROD=
```

### 3) Credenciales de Gmail

Para `email_service.py` se requiere:

- `enviarcorreo.json` (credenciales OAuth de Google)
- `token.json` (se genera tras la primera autenticación)

### 4) Destinatarios por oferta/grupo

Archivo: `recursos/destinatarios_correo.xlsx`

Debe contener columnas esperadas por el servicio de correo (`oferta`, `grupo`, `destinatarios`).

---

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

El flujo principal:

- inicia ejecución,
- procesa subprocesos,
- registra estados en BD,
- aplica reintentos globales,
- y envía correos en caso de error/resultado.

---

## Notas importantes

- La conexión BD actual usa `Trusted_Connection=yes` (autenticación Windows).
- Existen partes del flujo en evolución (por ejemplo, llamadas comentadas en `main.py` según entorno/pruebas).
- Si trabajas en equipo, evita incluir tokens/credenciales reales en el repositorio.

---

## Sugerencias de mejora

- Incorporar `requirements.txt` o `pyproject.toml`.
- Agregar pruebas unitarias por subproceso y servicios.
- Separar configuración sensible completamente en variables de entorno.
- Agregar un diagrama de flujo técnico del proceso completo.
