from db import conectar
from repositories import usuario_repo
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector
import bcrypt
from auth import crear_token

class UsuarioLogin(BaseModel):
  correo: str = Field(min_length=1, max_length=100 )
  contrasena: str = Field(min_length=1, max_length=100 )

router = APIRouter(prefix="/login", tags=["Login"])


@router.post("", status_code=200)
def crear_login(datos : UsuarioLogin):
  conexion =  conectar("AUTH")
  try:
    usuario = usuario_repo.obtener(conexion, datos.correo)
    if usuario is None or not bcrypt.checkpw(datos.contrasena.encode(), usuario["contrasena"].encode()):
      raise HTTPException(status_code=404, detail="No existe un usuario con ese correo")
    return {"token": crear_token(usuario["correo"], usuario["rol"]), "rol": usuario["rol"]}
  finally:
    conexion.close()

