def crear(conexion, correo, contrasena_hash, rol):
  cursor = conexion.cursor()
  cursor.execute("INSERT INTO login (correo, contrasena, rol) VALUES (%s, %s, %s)", (correo, contrasena_hash, rol))
  conexion.commit()

def obtener(conexion, correo):
  cursor = conexion.cursor(dictionary = True)
  cursor.execute("SELECT correo, contrasena, rol FROM login WHERE correo=%s",(correo,))
  return cursor.fetchone()
