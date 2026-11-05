from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector

from db import conectar
from repositories import jugador_repo
from auth import usuario_actual, solo_admin, ROL_A_DB
from errores import error_de_regla


class JugadorDatos(BaseModel):
  nombre: str = Field(min_length=1, max_length=50)
  apellido: str = Field(min_length=1, max_length=50)
  email: str = Field(min_length=3, max_length=100)
  fecha_nacimiento: date
  id_facultad: int
  tipo: Literal["grado", "posgrado", "docente", "funcionario"]


class JugadorNuevo(JugadorDatos):
  ci: str = Field(pattern=r"^\d{7,8}$")


router = APIRouter(prefix="/jugadores", tags=["Jugadores"])


def error_de_integridad(error):
  if error.errno == 1062:
    if "uq_jugador_email" in error.msg:
      raise HTTPException(status_code=409, detail="Ya existe un jugador con ese email")
    raise HTTPException(status_code=409, detail="Ya existe un jugador con esa cédula")
  if error.errno in (1452, 1216):
    raise HTTPException(status_code=400, detail="La facultad indicada no existe")
  raise error


@router.get("")
def listar_jugadores(usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return jugador_repo.listar(conexion)
  finally:
    conexion.close()


@router.get("/{ci}")
def obtener_jugador(ci: str, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    jugador = jugador_repo.obtener(conexion, ci)
    if jugador is None:
      raise HTTPException(status_code=404, detail="No se encontró un jugador con esa cédula")
    return jugador
  finally:
    conexion.close()


@router.post("", status_code=201)
def crear_jugador(datos: JugadorNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    jugador_repo.crear(conexion, datos.ci, datos.nombre, datos.apellido, datos.email,
                       datos.fecha_nacimiento, datos.id_facultad, datos.tipo)
    return jugador_repo.obtener(conexion, datos.ci)
  except mysql.connector.IntegrityError as error:
    error_de_integridad(error)
  finally:
    conexion.close()


@router.put("/{ci}")
def actualizar_jugador(ci: str, datos: JugadorDatos, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if jugador_repo.obtener(conexion, ci) is None:
      raise HTTPException(status_code=404, detail="No se encontró un jugador con esa cédula")
    jugador_repo.actualizar(conexion, ci, datos.nombre, datos.apellido, datos.email,
                            datos.fecha_nacimiento, datos.id_facultad, datos.tipo)
    return jugador_repo.obtener(conexion, ci)
  except mysql.connector.IntegrityError as error:
    error_de_integridad(error)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()


@router.delete("/{ci}", status_code=204)
def eliminar_jugador(ci: str, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if jugador_repo.obtener(conexion, ci) is None:
      raise HTTPException(status_code=404, detail="No se encontró un jugador con esa cédula")
    jugador_repo.eliminar(conexion, ci)
  except mysql.connector.IntegrityError as error:
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar: el jugador integra un plantel, figura en planillas o tiene sanciones")
    raise
  finally:
    conexion.close()