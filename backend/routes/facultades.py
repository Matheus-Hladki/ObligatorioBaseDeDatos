from db import conectar
from repositories import facultad_repo
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector

class FacultadNueva(BaseModel):
  nombre: str = Field(min_length=1, max_length=100)

router = APIRouter(prefix="/facultades", tags=["Facultades"])

@router.get("")
def listar_facultades():
  conexion = conectar()
  try:
    return facultad_repo.listar(conexion)
  finally:
    conexion.close()

@router.post("", status_code=201)
def crear_facultad(datos: FacultadNueva):
  conexion = conectar()
  try:
    id_nuevo = facultad_repo.crear(conexion, datos.nombre)
    return{"id_facultad": id_nuevo, "nombre": datos.nombre}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="Ya existe una facultad con ese nombre")
    raise
  finally:
    conexion.close()

@router.get("/{id_facultad}")
def obtener_facultad(id_facultad: int):
  conexion = conectar()
  try:
    facultad = facultad_repo.obtener(conexion, id_facultad)
    if facultad is None:
      raise HTTPException(status_code=404, detail="No se encontro una facultad con ese id")
    return facultad
  finally:
    conexion.close()

@router.put("/{id_facultad}")
def actualizar_facultad(id_facultad: int, datos: FacultadNueva):
  conexion = conectar()
  try:
    if facultad_repo.obtener(conexion, id_facultad) is None:
      raise HTTPException(status_code=404, detail="No se encontro una facultad con ese id")
    facultad_repo.actualizar(conexion, id_facultad, datos.nombre)
    return{"id_facultad" : id_facultad, "nombre": datos.nombre}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="Ya existe una facultad con ese nombre")
    raise
  finally:
    conexion.close()

@router.delete("/{id_facultad}", status_code=204)
def eliminar_facultad(id_facultad: int):
  conexion = conectar()
  try:
    if facultad_repo.obtener(conexion, id_facultad) is None:
      raise HTTPException(status_code=404, detail="No se encontro una facultad con ese id")
    facultad_repo.eliminar(conexion, id_facultad)
  except mysql.connector.IntegrityError as error:
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar, la facultad tiene jugadores")
    raise
  finally:
    conexion.close()



