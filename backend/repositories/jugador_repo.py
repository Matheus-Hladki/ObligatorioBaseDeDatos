def listar(conexion):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT j.ci, j.nombre, j.apellido, j.email, j.fecha_nacimiento, j.id_facultad, f.nombre AS facultad, j.tipo "
        "FROM jugador j JOIN facultad f ON f.id_facultad = j.id_facultad "
        "ORDER BY j.apellido, j.nombre"
    )
    return cursor.fetchall()

def obtener(conexion, ci):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT j.ci, j.nombre, j.apellido, j.email, j.fecha_nacimiento, j.id_facultad, f.nombre AS facultad, j.tipo "
        "FROM jugador j JOIN facultad f ON f.id_facultad = j.id_facultad "
        "WHERE j.ci = %s",
        (ci,)
    )
    return cursor.fetchone()

def crear(conexion, ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo):
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO jugador (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
    )
    conexion.commit()

def actualizar(conexion, ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo):
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE jugador SET nombre = %s, apellido = %s, email = %s, fecha_nacimiento = %s, id_facultad = %s, tipo = %s "
        "WHERE ci = %s",
        (nombre, apellido, email, fecha_nacimiento, id_facultad, tipo, ci)
    )
    conexion.commit()

def eliminar(conexion, ci):
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM jugador WHERE ci = %s", (ci,))
    conexion.commit()