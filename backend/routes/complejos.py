from db import conectar
from repositories import complejo_repo
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector
from auth import usuario_actual, solo_admin, ROL_A_DB

class ComplejoNuevo(BaseModel):
  nombre: str = Field(min_length=1, max_length=100)
  direccion: str = Field(min_length=1, max_length=150)
  departamento: str = Field(min_length=1, max_length=50)

router = APIRouter(prefix="/complejos", tags=["Complejos"])

@router.get("")
def listar_complejos(usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return complejo_repo.listar(conexion)
  finally:
    conexion.close()


@router.post("", status_code=201)
def crear_complejo(datos: ComplejoNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    id_nuevo = complejo_repo.crear(conexion, datos.nombre, datos.direccion, datos.departamento)
    return{"id_complejo": id_nuevo, "nombre": datos.nombre, "direccion": datos.direccion, "departamento": datos.departamento}
  finally:
    conexion.close()

@router.get("/{id_complejo}")
def obtener_complejo(id_complejo: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    complejo = complejo_repo.obtener(conexion, id_complejo)
    if complejo is None:
      raise HTTPException(status_code=404, detail="No se encontro un complejo con ese id")
    return complejo
  finally:
    conexion.close()

@router.put("/{id_complejo}")
def actualizar_complejo(id_complejo: int, datos: ComplejoNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if complejo_repo.obtener(conexion, id_complejo) is None:
      raise HTTPException(status_code=404, detail="No se encontro un complejo con ese id")
    complejo_repo.actualizar(conexion, id_complejo, datos.nombre, datos.direccion, datos.departamento)
    return{"id_complejo" : id_complejo, "nombre": datos.nombre, "direccion": datos.direccion, "departamento": datos.departamento}
  finally:
    conexion.close()

@router.delete("/{id_complejo}", status_code=204)
def eliminar_complejo(id_complejo: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if complejo_repo.obtener(conexion, id_complejo) is None:
      raise HTTPException(status_code=404, detail="No se encontro un complejo con ese id")
    complejo_repo.eliminar(conexion, id_complejo)
  except mysql.connector.IntegrityError as error:
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar, el complejo tiene canchas con partidos")
    raise
  finally:
    conexion.close()