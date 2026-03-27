# ==============================================================
# OBTENER REGISTROS DE OFERTA, GRUPO Y PARTICIPANTE A MATRICULAR
# ==============================================================
QUERY_OBTENER_INFO_CURSO = """
    SELECT
    *
    FROM Participante
"""

# ================================================================
# OBTENER CANTIDAD DE MATRICULADOS POR CURSO DESDE TABLA DE SIFODS
# ================================================================
QUERY_OBTENER_NRO_MATRICULADOS_CURSO = """
    SELECT COUNT(DISTINCT id_participante) AS nro_matriculados
    FROM Participante
    WHERE cur_id = ?
"""

# =================================================================================
# OBTENER INFORMACIÓN DE LOS PARTICIPANTES POR CURSO PARA ENVIAR REPORTE POR CORREO
# =================================================================================
QUERY_INFO_PARTICIPANTE = """
    SELECT usuario_documento, nombres, apellido_paterno, apellido_materno,
    correo_electronico, telefono FROM Participante
    WHERE cur_id = ?
"""

# ================================================================================================
# OBTENER INFORMACIÓN DE LOS PARTICIPANTES DE UN PROGRAMA POR CURSO PARA ENVIAR REPORTE POR CORREO
# ================================================================================================
QUERY_INFO_PARTICIPANTE_PROGRAMA = """
    SELECT usuario_documento, nombres, apellido_paterno, apellido_materno,
    correo_electronico, telefono FROM Participante
    WHERE id_oferta = ?
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