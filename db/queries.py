# ================================================================
# VERIFICAR USUARIOS EXISTENTES EN SIFODS DESDE BD
# Retorna los documentos que YA existen en la tabla de docentes.
# Se usa con formato dinámico: .format(placeholders="?,?,?")
# ================================================================
QUERY_VERIFICAR_USUARIOS_SIFODS = """
    SELECT DOCUMENTO_IDENTIDAD
    FROM [db_sifods_bi].[dm].[stge_sfds_docente_general]
    WHERE DOCUMENTO_IDENTIDAD IN ({placeholders})
"""

# ==============================================================
# OBTENER REGISTROS DE OFERTA, GRUPO Y PARTICIPANTE A MATRICULAR
# ==============================================================
QUERY_OBTENER_INFO_CURSO = """
    SELECT
    *
    FROM MATRICULA.tb_pendientes_matricula
"""

# ================================================================
# OBTENER CANTIDAD DE MATRICULADOS POR CURSO DESDE TABLA DE SIFODS
# ================================================================
QUERY_OBTENER_NRO_MATRICULADOS_CURSO = """
    SELECT COUNT(DISTINCT ID_PARTICIPANTE) AS nro_matriculados
    FROM MATRICULA.tb_pendientes_matricula
    WHERE cur_id = ?
"""

# =================================================================================
# OBTENER INFORMACIÓN DE LOS PARTICIPANTES POR CURSO PARA ENVIAR REPORTE POR CORREO
# =================================================================================
QUERY_INFO_PARTICIPANTE = """
    SELECT USUARIO_DOCUMENTO, NOMBRES, APELLIDO_PATERNO, APELLIDO_MATERNO,
    CORREO_ELECTRONICO FROM MATRICULA.tb_pendientes_matricula
    WHERE curid_sifods = ?
"""

# ================================================================================================
# OBTENER INFORMACIÓN DE LOS PARTICIPANTES DE UN PROGRAMA POR CURSO PARA ENVIAR REPORTE POR CORREO
# ================================================================================================
QUERY_INFO_PARTICIPANTE_PROGRAMA = """
    SELECT USUARIO_DOCUMENTO, NOMBRES, APELLIDO_PATERNO, APELLIDO_MATERNO,
    CORREO_ELECTRONICO FROM MATRICULA.tb_pendientes_matricula
    WHERE ID_OFERTA_FORMATIVA = ?
"""

# =========================
# EJECUCION
# =========================
INSERT_EJECUCION = """
INSERT INTO MATRICULA.ejecucion (
    id_robot,
    id_oferta,
    grupo,
    id_estado,
    fecha_inicio
)
OUTPUT INSERTED.id_ejecucion
VALUES (1, ?, ?, ?, GETDATE());
"""

UPDATE_EJECUCION_ESTADO = """
UPDATE MATRICULA.ejecucion
SET id_estado = ?
WHERE id_ejecucion = ?;
"""

UPDATE_EJECUCION_FIN = """
UPDATE MATRICULA.ejecucion
SET id_estado = ?, fecha_fin = GETDATE()
WHERE id_ejecucion = ?;
"""

# =========================
# LOG_EJECUCION
# =========================
INSERT_LOG_EJECUCION = """
INSERT INTO MATRICULA.log_ejecucion (
    id_ejecucion,
    nro_matriculas,
    id_estado,
    fecha_inicio
)
OUTPUT INSERTED.id_log
VALUES (?, ?, ?, GETDATE());
"""

UPDATE_LOG_EJECUCION_ESTADO = """
UPDATE MATRICULA.log_ejecucion
SET 
    nro_matriculas = ?,
    id_estado = ?
WHERE id_log = ?;
"""

UPDATE_LOG_EJECUCION_OK = """
UPDATE MATRICULA.log_ejecucion
SET 
    nro_matriculas = ?,
    id_estado = 3,
    fecha_fin = GETDATE()
WHERE id_log = ?;
"""

UPDATE_LOG_EJECUCION_ERROR = """
UPDATE MATRICULA.log_ejecucion
SET
    nro_matriculas = ?,
    id_estado = 4,
    id_error = ?,
    observacion = ?,
    fecha_fin = GETDATE()
WHERE id_log = ?;
"""

# =========================
# LOG_DETALLE
# =========================
INSERT_LOG_DETALLE_PENDIENTE = """
INSERT INTO MATRICULA.log_detalle (
    id_log,
    id_robot,
    id_subproceso,
    nro_matriculas,
    id_estado,
    fecha_inicio
)
OUTPUT INSERTED.id_detalle
VALUES (?, 1, ?, ?, 1, GETDATE());
"""

INSERT_LOG_DETALLE_EJECUCION = """
INSERT INTO MATRICULA.log_detalle (
    id_log,
    id_robot,
    id_subproceso,
    nro_matriculas,
    id_estado,
    fecha_inicio
)
OUTPUT INSERTED.id_detalle
VALUES (?, 1, ?, ?, 2, GETDATE());
"""

INSERT_LOG_DETALLE_OK = """
INSERT INTO MATRICULA.log_detalle (
    id_log,
    id_robot,
    id_subproceso,
    nro_matriculas,
    id_estado,
    fecha_fin
)
OUTPUT INSERTED.id_detalle
VALUES (?, 1, ?, ?, 3, GETDATE());
"""

INSERT_LOG_DETALLE_ERROR = """
INSERT INTO MATRICULA.log_detalle (
    id_log,
    id_robot,
    id_subproceso,
    nro_matriculas,
    id_estado,
    id_error,
    observacion,
    fecha_fin
)
OUTPUT INSERTED.id_detalle
VALUES (?, 1, ?, ?, 4, ?, ?, GETDATE());
"""