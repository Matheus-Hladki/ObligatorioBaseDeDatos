from db import conectar
from repositories import usuario_repo
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector
import bcrypt


router = APIRouter(prefix="/login", tags=["Login"])


@router.post("", status_code=201)
def crear_login(correo, contrasena):
  conexion =  conectar("AUTH")
  # try:
  #   if usuario_repo.obtener(conexion, correo) is None or bcrypt.checkpw():
  #     raise HTTPException(status_code=404, detail="No existe un usuario con ese correo")
    
# Queda a medio hacer, sigo mañana