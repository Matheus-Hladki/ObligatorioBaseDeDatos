COLUMNAS = (
    "SELECT c.nombre_cancha, c.id_complejo, co.nombre AS complejo, c.superficie, c.techada "
    "FROM cancha c JOIN complejo co ON co.id_complejo = c.id_complejo "
)

def a_bool(fila):
    if fila is not None:
        fila["techada"] = bool(fila["techada"])
    return fila

def listar_todas(conexion):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(COLUMNAS + "ORDER BY co.nombre, c.nombre_cancha")
    return [a_bool(fila) for fila in cursor.fetchall()]

def listar_por_complejo(conexion, id_complejo):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(COLUMNAS + "WHERE c.id_complejo = %s ORDER BY c.nombre_cancha", (id_complejo,))
    return [a_bool(fila) for fila in cursor.fetchall()]

def obtener(conexion, id_complejo, nombre_cancha):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(COLUMNAS + "WHERE c.id_complejo = %s AND c.nombre_cancha = %s", (id_complejo, nombre_cancha))
    return a_bool(cursor.fetchone())

def crear(conexion, id_complejo, nombre_cancha, superficie, techada):
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO cancha (nombre_cancha, id_complejo, superficie, techada) VALUES (%s, %s, %s, %s)",
        (nombre_cancha, id_complejo, superficie, techada)
    )
    conexion.commit()

def actualizar(conexion, id_complejo, nombre_cancha, superficie, techada):
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE cancha SET superficie = %s, techada = %s WHERE id_complejo = %s AND nombre_cancha = %s",
        (superficie, techada, id_complejo, nombre_cancha)
    )
    conexion.commit()

def eliminar(conexion, id_complejo, nombre_cancha):
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM cancha WHERE id_complejo = %s AND nombre_cancha = %s", (id_complejo, nombre_cancha))
    conexion.commit()