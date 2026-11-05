from datetime import datetime, timedelta, timezone
import os
import jwt
from dotenv import load_dotenv

load_dotenv()

def crear_token(correo, rol):
  vence = datetime.now(timezone.utc) + timedelta(hours=8) # 8 horas = una jornada de trabajo
  datos = {"correo":correo, "rol":rol, "exp":vence}
  token = jwt.encode(datos, (os.getenv("JWT_SECRET")), algorithm="HS256")
  return token

