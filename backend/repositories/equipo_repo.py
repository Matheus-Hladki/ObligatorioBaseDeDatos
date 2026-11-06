COLUMNAS = (
    "SELECT e.id_equipo, e.nombre, e.id_torneo, t.nombre AS torneo, e.id_facultad, f.nombre AS facultad, "
    "e.ci_capitan, CONCAT(j.nombre, ' ', j.apellido) AS capitan, "
    "(SELECT COUNT(*) FROM equipo_jugador_torneo x WHERE x.id_equipo = e.id_equipo) AS cantidad_jugadores "
    "FROM equipo e "
    "JOIN torneo t ON t.id_torneo = e.id_torneo "
    "JOIN facultad f ON f.id_facultad = e.id_facultad "
    "LEFT JOIN jugador j ON j.ci = e.ci_capitan "
)

def listar(conexion, id_torneo=None):
    cursor = conexion.cursor(dictionary=True)
    if id_torneo is None:
        cursor.execute(COLUMNAS + "ORDER BY e.id_torneo, e.nombre")
    else:
        cursor.execute(COLUMNAS + "WHERE e.id_torneo = %s ORDER BY e.nombre", (id_torneo,))
    return cursor.fetchall()

def obtener(conexion, id_equipo):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(COLUMNAS + "WHERE e.id_equipo = %s", (id_equipo,))
    return cursor.fetchone()

def listar_plantel(conexion, id_equipo):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.ci_jugador, j.nombre, j.apellido, j.tipo, p.numero_camiseta "
        "FROM equipo_jugador_torneo p JOIN jugador j ON j.ci = p.ci_jugador "
        "WHERE p.id_equipo = %s ORDER BY p.numero_camiseta",
        (id_equipo,)
    )
    return cursor.fetchall()

def crear(conexion, nombre, id_torneo, id_facultad):
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO equipo (nombre, id_torneo, id_facultad) VALUES (%s, %s, %s)",
        (nombre, id_torneo, id_facultad)
    )
    return cursor.lastrowid

def actualizar(conexion, id_equipo, nombre, id_facultad):
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE equipo SET nombre = %s, id_facultad = %s WHERE id_equipo = %s",
        (nombre, id_facultad, id_equipo)
    )

def designar_capitan(conexion, id_equipo, ci_capitan):
    cursor = conexion.cursor()
    cursor.execute("UPDATE equipo SET ci_capitan = %s WHERE id_equipo = %s", (ci_capitan, id_equipo))

def agregar_jugador(conexion, id_equipo, id_torneo, ci_jugador, numero_camiseta):
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO equipo_jugador_torneo (id_equipo, ci_jugador, id_torneo, numero_camiseta) "
        "VALUES (%s, %s, %s, %s)",
        (id_equipo, ci_jugador, id_torneo, numero_camiseta)
    )

def quitar_jugador(conexion, id_equipo, ci_jugador):
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM equipo_jugador_torneo WHERE id_equipo = %s AND ci_jugador = %s",
        (id_equipo, ci_jugador)
    )
    return cursor.rowcount

def eliminar(conexion, id_equipo):
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM equipo_jugador_torneo WHERE id_equipo = %s", (id_equipo,))
    cursor.execute("DELETE FROM equipo WHERE id_equipo = %s", (id_equipo,))