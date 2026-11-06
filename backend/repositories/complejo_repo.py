def listar(conexion):
	cursor = conexion.cursor(dictionary=True)
	cursor.execute("SELECT id_complejo, nombre, direccion, departamento FROM complejo ORDER BY nombre")
	return cursor.fetchall()

def crear(conexion, nombre, direccion, departamento):
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO complejo (nombre, direccion, departamento) VALUES (%s, %s, %s)", (nombre, direccion, departamento))
	conexion.commit()
	return cursor.lastrowid

def obtener(conexion, id_complejo):
	cursor = conexion.cursor(dictionary = True)
	cursor.execute("SELECT id_complejo, nombre, direccion, departamento FROM complejo WHERE id_complejo = %s", (id_complejo,))
	return cursor.fetchone()

def actualizar(conexion, id_complejo, nombre, direccion, departamento):
	cursor = conexion.cursor()
	cursor.execute("UPDATE complejo SET nombre = %s, direccion = %s, departamento = %s WHERE id_complejo = %s", (nombre, direccion, departamento, id_complejo))
	conexion.commit()

def eliminar(conexion, id_complejo):
	cursor = conexion.cursor()
	cursor.execute("DELETE FROM complejo WHERE id_complejo = %s", (id_complejo,))
	conexion.commit()