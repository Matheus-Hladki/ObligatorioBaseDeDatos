def listar(conexion, id_torneo, ci_jugador):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("""
		SELECT s.id_sancion, s.ci_jugador, j.nombre, j.apellido,
		       s.id_torneo, s.motivo, s.numero_fecha_inicio, s.cantidad_fechas,
		       s.numero_fecha_inicio + s.cantidad_fechas - 1 AS numero_fecha_fin,
		       s.id_tarjeta
		FROM sancion_jugador s
		JOIN jugador j ON j.ci = s.ci_jugador
		WHERE s.id_torneo = %s
		  AND (%s IS NULL OR s.ci_jugador = %s)
		ORDER BY s.numero_fecha_inicio, j.apellido, j.nombre
	""", (id_torneo, ci_jugador, ci_jugador))
	return cursor.fetchall()


def crear_disciplinaria(conexion, ci_jugador, id_torneo, numero_fecha_inicio, cantidad_fechas):
	cursor = conexion.cursor()
	cursor.execute("""
		INSERT INTO sancion_jugador (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
		VALUES (%s, %s, 'disciplinaria', %s, %s)
	""", (ci_jugador, id_torneo, numero_fecha_inicio, cantidad_fechas))
	conexion.commit()
	return cursor.lastrowid