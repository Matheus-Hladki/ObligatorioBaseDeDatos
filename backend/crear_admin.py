from getpass import getpass
import bcrypt
from db import conectar
from repositories import usuario_repo
import mysql.connector



correo = input("Correo: ")
contrasena = getpass("Contraseña: ")

contrasena_hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()

conexion = conectar()

try:
  usuario_repo.crear(conexion, correo, contrasena_hash, "administrador")
  print("Salio Bien")
except mysql.connector.IntegrityError as error:
  if error.errno == 1062:
    print("Ya existe una cuenta con ese correo")
  else:
    raise
finally:
  conexion.close()

