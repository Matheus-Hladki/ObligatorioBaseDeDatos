def plazo_partido(conexion, id_partido):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("""
		SELECT p.estado,
		       TIMESTAMP(p.dia, t.hora_fin) + INTERVAL 48 HOUR
		         < UTC_TIMESTAMP() - INTERVAL 3 HOUR AS vencido
		FROM partido p
		JOIN turno t ON t.id_turno = p.id_turno
		WHERE p.id_partido = %s
	""", (id_partido,))
	return cursor.fetchone()


def listar(conexion, id_partido):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("""
		SELECT pp.ci_jugador, j.nombre, j.apellido,
		       pp.id_equipo, e.nombre AS equipo, ejt.numero_camiseta
		FROM planilla_partido pp
		JOIN jugador j ON j.ci = pp.ci_jugador
		JOIN equipo e  ON e.id_equipo = pp.id_equipo
		JOIN partido p ON p.id_partido = pp.id_partido
		JOIN equipo_jugador_torneo ejt ON ejt.ci_jugador = pp.ci_jugador
		                              AND ejt.id_torneo  = p.id_torneo
		WHERE pp.id_partido = %s
		ORDER BY e.nombre, ejt.numero_camiseta
	""", (id_partido,))
	return cursor.fetchall()


def esta_en_planilla(conexion, id_partido, ci_jugador):
	cursor = conexion.cursor()
	cursor.execute("SELECT 1 FROM planilla_partido WHERE id_partido = %s AND ci_jugador = %s",
	               (id_partido, ci_jugador))
	return cursor.fetchone() is not None


def agregar(conexion, id_partido, ci_jugador, id_equipo):
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO planilla_partido (id_partido, ci_jugador, id_equipo) VALUES (%s, %s, %s)",
	               (id_partido, ci_jugador, id_equipo))
	conexion.commit()


def quitar(conexion, id_partido, ci_jugador):
	cursor = conexion.cursor()
	try:
		cursor.execute("DELETE FROM tarjeta WHERE id_partido = %s AND ci_jugador = %s",
		               (id_partido, ci_jugador))
		cursor.execute("DELETE FROM planilla_partido WHERE id_partido = %s AND ci_jugador = %s",
		               (id_partido, ci_jugador))
		conexion.commit()
	except Exception:
		conexion.rollback()
		raise