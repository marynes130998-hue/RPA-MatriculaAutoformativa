import pandas as pd

def obtener_inscritos_mock():

    # Registros
    registros = [
        (659, "GRUPO 01"),
        (659, "GRUPO 02")
    ]

    # id_map
    id_map = {
        (659, "GRUPO 01"): (1001, 2001),
        (659, "GRUPO 02"): (1002, 2002)
    }

    # Participantes Grupo 01
    data_g1 = [
        {
            "id_oferta": 659,
            "nombre_grupo": "GRUPO 01",
            "usuario_documento": f"7000000{i}",
            "nombres": f"Nombre{i}",
            "apellido_paterno": f"ApellidoP{i}",
            "apellido_materno": f"ApellidoM{i}",
            "correo_electronico": f"usuario{i}@gmail.com",
            "telefono": f"9000000{i}"
        }
        for i in range(1, 11)
    ]

    # Participantes Grupo 02
    data_g2 = [
        {
            "id_oferta": 659,
            "nombre_grupo": "GRUPO 02",
            "usuario_documento": f"8000000{i}",
            "nombres": f"Nombre{i+10}",
            "apellido_paterno": f"ApellidoP{i+10}",
            "apellido_materno": f"ApellidoM{i+10}",
            "correo_electronico": f"usuario{i+10}@gmail.com",
            "telefono": f"9000001{i}"
        }
        for i in range(1, 11)
    ]

    # df_total
    df_total = pd.DataFrame(data_g1 + data_g2)

    # df_cursos
    df_cursos = pd.DataFrame([
        {
            "id_oferta": 659,
            "nombre_grupo": "GRUPO 01",
            "cur_id": 100
        },
        {
            "id_oferta": 659,
            "nombre_grupo": "GRUPO 02",
            "cur_id": 101
        }
    ])

    return registros, id_map, df_total, df_cursos