import bcrypt, mysql.connector
from db import conectar
from repositories import usuario_repo

USUARIOS = [("admin@correo.ucu.edu.uy", "adminUCU", "administrador"),
            ("planilleros@correo.ucu.edu.uy", "planillerosUCU", "planillero")]
con = conectar()
for correo, clave, rol in USUARIOS:
    try:
        usuario_repo.crear(con, correo, bcrypt.hashpw(clave.encode(), bcrypt.gensalt()).decode(), rol)
    except mysql.connector.IntegrityError as e:
        if e.errno != 1062:
            raise
con.close()