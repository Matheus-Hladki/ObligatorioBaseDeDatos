def listar(conexion):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("SELECT id_facultad, nombre FROM facultad ORDER BY nombre")
	return cursor.fetchall()

def crear(conexion, nombre):
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO facultad (nombre) VALUES (%s)", (nombre,))
	conexion.commit()
	return cursor.lastrowid

def obtener(conexion, id_facultad):
	cursor = conexion.cursor(dictionary = True)
	cursor.execute("SELECT id_facultad, nombre FROM facultad WHERE id_facultad = %s", (id_facultad,))
	return cursor.fetchone()

def actualizar(conexion, id_facultad, nombre):
	cursor = conexion.cursor()
	cursor.execute("UPDATE facultad SET nombre = %s WHERE id_facultad = %s", (nombre, id_facultad))
	conexion.commit()

def eliminar(conexion, id_facultad):
	cursor = conexion.cursor()
	cursor.execute("DELETE FROM facultad WHERE id_facultad = %s", (id_facultad,))
	conexion.commit()

