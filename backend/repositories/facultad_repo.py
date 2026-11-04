def listar(conexion):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("SELECT id_facultad, nombre FROM facultad ORDER BY nombre")
	return cursor.fetchall()