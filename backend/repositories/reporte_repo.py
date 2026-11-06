GOLES_LOCAL = """
	COALESCE(SUM(CASE
		WHEN (pp.id_equipo = p.id_equipo_local     AND g.autogol = FALSE)
		  OR (pp.id_equipo = p.id_equipo_visitante AND g.autogol = TRUE) THEN 1
		ELSE 0 END), 0)"""

GOLES_VISITANTE = """
	COALESCE(SUM(CASE
		WHEN (pp.id_equipo = p.id_equipo_visitante AND g.autogol = FALSE)
		  OR (pp.id_equipo = p.id_equipo_local     AND g.autogol = TRUE) THEN 1
		ELSE 0 END), 0)"""


def _consultar(conexion, sql, parametros=()):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute(sql, parametros)
	return cursor.fetchall()


def posiciones(conexion, id_torneo):
	return _consultar(conexion, f"""
		WITH resultado AS (
			SELECT p.id_partido, p.id_equipo_local, p.id_equipo_visitante,
			       {GOLES_LOCAL} AS goles_local,
			       {GOLES_VISITANTE} AS goles_visitante
			FROM partido p
			LEFT JOIN gol g ON g.id_partido = p.id_partido
			LEFT JOIN planilla_partido pp ON pp.id_partido = g.id_partido
			                             AND pp.ci_jugador = g.ci_jugador
			WHERE p.id_torneo = %s AND p.estado = 'jugado'
			GROUP BY p.id_partido, p.id_equipo_local, p.id_equipo_visitante
		),
		por_equipo AS (
			SELECT id_equipo_local AS id_equipo, goles_local AS gf, goles_visitante AS gc FROM resultado
			UNION ALL
			SELECT id_equipo_visitante, goles_visitante, goles_local FROM resultado
		)
		SELECT e.id_equipo, e.nombre AS equipo,
		       COUNT(pe.id_equipo) AS jugados,
		       COALESCE(SUM(pe.gf > pe.gc), 0) AS ganados,
		       COALESCE(SUM(pe.gf = pe.gc), 0) AS empatados,
		       COALESCE(SUM(pe.gf < pe.gc), 0) AS perdidos,
		       COALESCE(SUM(pe.gf), 0) AS goles_favor,
		       COALESCE(SUM(pe.gc), 0) AS goles_contra,
		       COALESCE(SUM(pe.gf - pe.gc), 0) AS diferencia,
		       COALESCE(SUM(CASE WHEN pe.gf > pe.gc THEN 3 WHEN pe.gf = pe.gc THEN 1 ELSE 0 END), 0) AS puntos
		FROM equipo e
		LEFT JOIN por_equipo pe ON pe.id_equipo = e.id_equipo
		WHERE e.id_torneo = %s
		GROUP BY e.id_equipo, e.nombre
		ORDER BY puntos DESC, diferencia DESC, goles_favor DESC, e.nombre
	""", (id_torneo, id_torneo))


def goleadores(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT j.ci, j.nombre, j.apellido, e.nombre AS equipo, COUNT(*) AS goles
		FROM gol g
		JOIN partido p ON p.id_partido = g.id_partido
		JOIN planilla_partido pp ON pp.id_partido = g.id_partido
		                        AND pp.ci_jugador = g.ci_jugador
		JOIN equipo e  ON e.id_equipo = pp.id_equipo
		JOIN jugador j ON j.ci = g.ci_jugador
		WHERE p.id_torneo = %s AND g.autogol = FALSE
		GROUP BY j.ci, j.nombre, j.apellido, e.nombre
		ORDER BY goles DESC, j.apellido, j.nombre
		LIMIT 10
	""", (id_torneo,))


def fair_play(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT e.id_equipo, e.nombre AS equipo,
		       COALESCE(SUM(t.color = 'amarilla'), 0) AS amarillas,
		       COALESCE(SUM(t.color = 'roja'), 0) AS rojas,
		       COALESCE(SUM(CASE t.color WHEN 'amarilla' THEN 1 WHEN 'roja' THEN 3 ELSE 0 END), 0) AS puntaje
		FROM equipo e
		LEFT JOIN planilla_partido pp ON pp.id_equipo = e.id_equipo
		LEFT JOIN tarjeta t ON t.id_partido = pp.id_partido
		                   AND t.ci_jugador = pp.ci_jugador
		WHERE e.id_torneo = %s
		GROUP BY e.id_equipo, e.nombre
		ORDER BY puntaje, e.nombre
	""", (id_torneo,))


def promedio_goles_por_fecha(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT p.numero_fecha,
		       COUNT(DISTINCT p.id_partido) AS partidos,
		       COUNT(g.id_gol) AS goles,
		       ROUND(COUNT(g.id_gol) / COUNT(DISTINCT p.id_partido), 2) AS promedio
		FROM partido p
		LEFT JOIN gol g ON g.id_partido = p.id_partido
		WHERE p.id_torneo = %s AND p.estado = 'jugado'
		GROUP BY p.numero_fecha
		ORDER BY p.numero_fecha
	""", (id_torneo,))


def promedio_goles_edicion(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT COUNT(DISTINCT p.id_partido) AS partidos,
		       COUNT(g.id_gol) AS goles,
		       ROUND(COUNT(g.id_gol) / COUNT(DISTINCT p.id_partido), 2) AS promedio
		FROM partido p
		LEFT JOIN gol g ON g.id_partido = p.id_partido
		WHERE p.id_torneo = %s AND p.estado = 'jugado'
	""", (id_torneo,))[0]


def promedio_goles(conexion, id_torneo):
	return {
		"por_fecha": promedio_goles_por_fecha(conexion, id_torneo),
		"edicion": promedio_goles_edicion(conexion, id_torneo),
	}


def canchas_mas_usadas(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT p.nombre_cancha, p.id_complejo, c.nombre AS complejo, COUNT(*) AS partidos
		FROM partido p
		JOIN complejo c ON c.id_complejo = p.id_complejo
		WHERE p.id_torneo = %s AND p.estado <> 'cancelado'
		GROUP BY p.nombre_cancha, p.id_complejo, c.nombre
		ORDER BY partidos DESC, c.nombre, p.nombre_cancha
	""", (id_torneo,))


def turnos_mas_usados(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT t.id_turno,
		       CAST(t.hora_inicio AS CHAR) AS hora_inicio,
		       CAST(t.hora_fin AS CHAR) AS hora_fin,
		       COUNT(*) AS partidos
		FROM partido p
		JOIN turno t ON t.id_turno = p.id_turno
		WHERE p.id_torneo = %s AND p.estado <> 'cancelado'
		GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
		ORDER BY partidos DESC, t.hora_inicio
	""", (id_torneo,))


def jugadores_por_facultad_y_tipo(conexion):
	return _consultar(conexion, """
		SELECT f.id_facultad, f.nombre AS facultad, j.tipo, COUNT(*) AS cantidad
		FROM jugador j
		JOIN facultad f ON f.id_facultad = j.id_facultad
		GROUP BY f.id_facultad, f.nombre, j.tipo
		ORDER BY f.nombre, j.tipo
	""")


def jugadores_sin_planilla(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT j.ci, j.nombre, j.apellido, e.nombre AS equipo, ejt.numero_camiseta
		FROM equipo_jugador_torneo ejt
		JOIN jugador j ON j.ci = ejt.ci_jugador
		JOIN equipo e  ON e.id_equipo = ejt.id_equipo
		WHERE ejt.id_torneo = %s
		  AND NOT EXISTS (
		      SELECT 1 FROM planilla_partido pp
		      WHERE pp.ci_jugador = ejt.ci_jugador
		        AND pp.id_equipo  = ejt.id_equipo
		  )
		ORDER BY e.nombre, j.apellido, j.nombre
	""", (id_torneo,))


def sanciones_por_equipo_y_motivo(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT e.id_equipo, e.nombre AS equipo, s.motivo, COUNT(*) AS cantidad
		FROM sancion_jugador s
		JOIN equipo_jugador_torneo ejt ON ejt.ci_jugador = s.ci_jugador
		                              AND ejt.id_torneo  = s.id_torneo
		JOIN equipo e ON e.id_equipo = ejt.id_equipo
		WHERE s.id_torneo = %s
		GROUP BY e.id_equipo, e.nombre, s.motivo
		ORDER BY e.nombre, s.motivo
	""", (id_torneo,))


def estado_partidos(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT total, jugados, postergados, cancelados,
		       ROUND(100 * jugados     / total, 2) AS porcentaje_jugados,
		       ROUND(100 * postergados / total, 2) AS porcentaje_postergados,
		       ROUND(100 * cancelados  / total, 2) AS porcentaje_cancelados
		FROM (
			SELECT COUNT(*) AS total,
			       COALESCE(SUM(p.estado = 'jugado'), 0) AS jugados,
			       COALESCE(SUM(p.estado = 'cancelado'), 0) AS cancelados,
			       COALESCE(SUM(p.estado = 'postergado' OR EXISTS (
			           SELECT 1 FROM partido_reprogramacion r
			           WHERE r.id_partido = p.id_partido
			             AND r.estado_anterior = 'postergado'
			       )), 0) AS postergados
			FROM partido p
			WHERE p.id_torneo = %s
		) conteo
	""", (id_torneo,))[0]


def resultados(conexion, id_torneo):
	return _consultar(conexion, f"""
		SELECT p.id_partido, p.numero_fecha, p.dia,
		       el.nombre AS equipo_local, ev.nombre AS equipo_visitante,
		       {GOLES_LOCAL} AS goles_local,
		       {GOLES_VISITANTE} AS goles_visitante
		FROM partido p
		JOIN equipo el ON el.id_equipo = p.id_equipo_local
		JOIN equipo ev ON ev.id_equipo = p.id_equipo_visitante
		LEFT JOIN gol g ON g.id_partido = p.id_partido
		LEFT JOIN planilla_partido pp ON pp.id_partido = g.id_partido
		                             AND pp.ci_jugador = g.ci_jugador
		WHERE p.id_torneo = %s AND p.estado = 'jugado'
		GROUP BY p.id_partido, p.numero_fecha, p.dia, el.nombre, ev.nombre
		ORDER BY p.numero_fecha, p.dia, p.id_partido
	""", (id_torneo,))


def suspendidos_en_fecha(conexion, id_torneo, numero_fecha):
	return _consultar(conexion, """
		SELECT s.ci_jugador, j.nombre, j.apellido, e.nombre AS equipo, s.motivo,
		       s.numero_fecha_inicio,
		       s.numero_fecha_inicio + s.cantidad_fechas - 1 AS numero_fecha_fin
		FROM sancion_jugador s
		JOIN jugador j ON j.ci = s.ci_jugador
		LEFT JOIN equipo_jugador_torneo ejt ON ejt.ci_jugador = s.ci_jugador
		                                   AND ejt.id_torneo  = s.id_torneo
		LEFT JOIN equipo e ON e.id_equipo = ejt.id_equipo
		WHERE s.id_torneo = %s
		  AND %s BETWEEN s.numero_fecha_inicio
		             AND s.numero_fecha_inicio + s.cantidad_fechas - 1
		ORDER BY e.nombre, j.apellido, j.nombre
	""", (id_torneo, numero_fecha))


def historial_reprogramaciones(conexion, id_torneo):
	return _consultar(conexion, """
		SELECT r.id_reprogramacion, r.id_partido, p.numero_fecha,
		       el.nombre AS equipo_local, ev.nombre AS equipo_visitante,
		       r.dia_anterior, CAST(t.hora_inicio AS CHAR) AS hora_inicio_anterior,
		       r.nombre_cancha_anterior, r.estado_anterior, r.motivo, r.fecha_registro,
		       p.dia AS dia_actual, p.estado AS estado_actual
		FROM partido_reprogramacion r
		JOIN partido p ON p.id_partido = r.id_partido
		JOIN equipo el ON el.id_equipo = p.id_equipo_local
		JOIN equipo ev ON ev.id_equipo = p.id_equipo_visitante
		JOIN turno t   ON t.id_turno   = r.id_turno_anterior
		WHERE p.id_torneo = %s
		ORDER BY r.fecha_registro DESC, r.id_reprogramacion DESC
	""", (id_torneo,))
