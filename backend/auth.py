from datetime import datetime, timedelta, timezone
import os
import jwt
from dotenv import load_dotenv
from fastapi.security import HTTPBearer
from fastapi import HTTPException, Depends

load_dotenv()

seguridad = HTTPBearer()

ROL_A_DB = {"administrador": "ADMIN", "planillero": "PLANILLERO"}


def crear_token(correo, rol):
  vence = datetime.now(timezone.utc) + timedelta(hours=8) # 8 horas = una jornada de trabajo
  datos = {"correo":correo, "rol":rol, "exp":vence}
  token = jwt.encode(datos, (os.getenv("JWT_SECRET")), algorithm="HS256")
  return token

def usuario_actual(credenciales = Depends(seguridad)):
  try:
    return jwt.decode(credenciales.credentials, os.getenv("JWT_SECRET"), algorithms=["HS256"])
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Sesión inválida o vencida")
  
def solo_admin(usuario = Depends(usuario_actual)):
  if usuario["rol"] != "administrador":
    raise HTTPException(status_code=403, detail="Solo un administrador puede hacer esto")
  return usuario