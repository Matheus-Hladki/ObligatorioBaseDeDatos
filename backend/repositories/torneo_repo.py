def listar(conexion):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("SELECT id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin, estado FROM torneo ORDER BY anio, semestre")
	return cursor.fetchall()

def crear(conexion, nombre, anio, semestre, fecha_inicio, fecha_fin):
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO torneo (nombre, anio, semestre, fecha_inicio, fecha_fin) VALUES (%s,%s,%s,%s,%s)", (nombre, anio, semestre, fecha_inicio, fecha_fin))
	conexion.commit()
	return cursor.lastrowid

def obtener(conexion, id_torneo):
	cursor = conexion.cursor(dictionary = True)
	cursor.execute("SELECT id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin, estado FROM torneo WHERE id_torneo = %s", (id_torneo,))
	return cursor.fetchone()

def actualizar(conexion, id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin):
	cursor = conexion.cursor()
	cursor.execute("UPDATE torneo SET nombre = %s, anio = %s, semestre = %s, fecha_inicio = %s, fecha_fin = %s WHERE id_torneo = %s", (nombre, anio, semestre, fecha_inicio, fecha_fin, id_torneo))
	conexion.commit()

def cambiar_estado(conexion, id_torneo, estado):
	cursor = conexion.cursor()
	cursor.execute("UPDATE torneo SET estado = %s WHERE id_torneo = %s", (estado, id_torneo))
	conexion.commit()

