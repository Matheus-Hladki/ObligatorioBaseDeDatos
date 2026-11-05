def listar_por_torneo(conexion, id_torneo):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("""
		SELECT p.id_partido, p.numero_fecha, p.dia, p.estado,
		       p.id_equipo_local,     el.nombre AS equipo_local,
		       p.id_equipo_visitante, ev.nombre AS equipo_visitante,
		       p.id_turno, CAST(t.hora_inicio AS CHAR) AS hora_inicio, CAST(t.hora_fin    AS CHAR) AS hora_fin,
		       p.nombre_cancha, p.id_complejo, c.nombre AS complejo
		FROM partido p
		JOIN equipo el  ON el.id_equipo  = p.id_equipo_local
		JOIN equipo ev  ON ev.id_equipo  = p.id_equipo_visitante
		JOIN turno t    ON t.id_turno    = p.id_turno
		JOIN complejo c ON c.id_complejo = p.id_complejo
		WHERE p.id_torneo = %s
		ORDER BY p.numero_fecha, p.dia, t.hora_inicio
	""", (id_torneo,))
	return cursor.fetchall()


def existe_torneo(conexion, id_torneo):
	cursor = conexion.cursor()
	cursor.execute("SELECT 1 FROM torneo WHERE id_torneo = %s", (id_torneo,))
	return cursor.fetchone() is not None

def crear(conexion, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
          dia, id_turno, nombre_cancha, id_complejo):
	cursor = conexion.cursor()
	cursor.execute("""
		INSERT INTO partido (id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
		                     dia, id_turno, nombre_cancha, id_complejo)
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
	""", (id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
	      dia, id_turno, nombre_cancha, id_complejo))
	conexion.commit()
	return cursor.lastrowid

def obtener(conexion, id_partido):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("""
		SELECT id_partido, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
		       dia, id_turno, nombre_cancha, id_complejo, estado
		FROM partido
		WHERE id_partido = %s
	""", (id_partido,))
	return cursor.fetchone()

def cambiar_estado(conexion, id_partido, estado):
	cursor = conexion.cursor()
	cursor.execute("UPDATE partido SET estado = %s WHERE id_partido = %s", (estado, id_partido))
	conexion.commit()