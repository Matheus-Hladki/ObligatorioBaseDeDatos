def listar(conexion):
  cursor = conexion.cursor(dictionary=True)
  cursor.execute("SELECT id_turno, TIME_FORMAT(hora_inicio, '%H:%i') AS hora_inicio, TIME_FORMAT(hora_fin, '%H:%i') AS hora_fin FROM turno ORDER BY hora_inicio")
  return cursor.fetchall()