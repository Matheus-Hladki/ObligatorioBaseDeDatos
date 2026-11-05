from db import conectar
from repositories import usuario_repo
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import bcrypt
from typing import Literal
from auth import  solo_admin
import mysql.connector



class UsuarioNuevo(BaseModel):
  correo: str = Field(min_length=1, max_length=100)
  contrasena: str = Field(min_length=1, max_length=100)
  rol: Literal["administrador", "planillero"]

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("", status_code=201)
def crear_usuario(datos:  UsuarioNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    usuario_repo.crear(conexion, datos.correo, bcrypt.hashpw(datos.contrasena.encode(), bcrypt.gensalt()).decode(), datos.rol)
    return{"correo" : datos.correo, "rol": datos.rol}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="Ya existe un usuario con ese correo")
    raise
  finally:
    conexion.close()
