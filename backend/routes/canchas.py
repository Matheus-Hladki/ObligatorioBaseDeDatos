from typing import Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector

from db import conectar
from repositories import cancha_repo, complejo_repo
from auth import usuario_actual, solo_admin, ROL_A_DB


class CanchaDatos(BaseModel):
  superficie: Literal["sintético", "parquet"]
  techada: bool = False


class CanchaNueva(CanchaDatos):
  nombre_cancha: str = Field(min_length=1, max_length=50)


router = APIRouter(tags=["Canchas"])


def verificar_complejo(conexion, id_complejo):
  if complejo_repo.obtener(conexion, id_complejo) is None:
    raise HTTPException(status_code=404, detail="No se encontró un complejo con ese id")


@router.get("/canchas")
def listar_todas_las_canchas(usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return cancha_repo.listar_todas(conexion)
  finally:
    conexion.close()


@router.get("/complejos/{id_complejo}/canchas")
def listar_canchas_del_complejo(id_complejo: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    verificar_complejo(conexion, id_complejo)
    return cancha_repo.listar_por_complejo(conexion, id_complejo)
  finally:
    conexion.close()


@router.get("/complejos/{id_complejo}/canchas/{nombre_cancha}")
def obtener_cancha(id_complejo: int, nombre_cancha: str, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    cancha = cancha_repo.obtener(conexion, id_complejo, nombre_cancha)
    if cancha is None:
      raise HTTPException(status_code=404, detail="No se encontró esa cancha en ese complejo")
    return cancha
  finally:
    conexion.close()


@router.post("/complejos/{id_complejo}/canchas", status_code=201)
def crear_cancha(id_complejo: int, datos: CanchaNueva, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    verificar_complejo(conexion, id_complejo)
    cancha_repo.crear(conexion, id_complejo, datos.nombre_cancha, datos.superficie, datos.techada)
    return cancha_repo.obtener(conexion, id_complejo, datos.nombre_cancha)
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="Ese complejo ya tiene una cancha con ese nombre")
    raise
  finally:
    conexion.close()


@router.put("/complejos/{id_complejo}/canchas/{nombre_cancha}")
def actualizar_cancha(id_complejo: int, nombre_cancha: str, datos: CanchaDatos, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if cancha_repo.obtener(conexion, id_complejo, nombre_cancha) is None:
      raise HTTPException(status_code=404, detail="No se encontró esa cancha en ese complejo")
    cancha_repo.actualizar(conexion, id_complejo, nombre_cancha, datos.superficie, datos.techada)
    return cancha_repo.obtener(conexion, id_complejo, nombre_cancha)
  finally:
    conexion.close()


@router.delete("/complejos/{id_complejo}/canchas/{nombre_cancha}", status_code=204)
def eliminar_cancha(id_complejo: int, nombre_cancha: str, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if cancha_repo.obtener(conexion, id_complejo, nombre_cancha) is None:
      raise HTTPException(status_code=404, detail="No se encontró esa cancha en ese complejo")
    cancha_repo.eliminar(conexion, id_complejo, nombre_cancha)
  except mysql.connector.IntegrityError as error:
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar: la cancha tiene partidos asignados")
    raise
  finally:
    conexion.close()