from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector

from db import conectar
from repositories import torneo_repo
from auth import usuario_actual, solo_admin, ROL_A_DB
from errores import error_de_regla


class TorneoDatos(BaseModel):
  nombre: str = Field(min_length=1, max_length=100)
  anio: int = Field(ge=2000, le=2100)
  semestre: Literal[1, 2]
  fecha_inicio: date
  fecha_fin: date


class EstadoNuevo(BaseModel):
  estado: Literal["inscripción", "en curso", "finalizado"]


router = APIRouter(prefix="/torneos", tags=["Torneos"])


def validar_fechas(datos):
  if datos.fecha_fin < datos.fecha_inicio:
    raise HTTPException(status_code=400, detail="La fecha de fin no puede ser anterior a la de inicio")


def error_de_integridad(error):
  if error.errno == 1062:
    raise HTTPException(status_code=409, detail="Ya existe un torneo para ese año y semestre")
  raise error


def verificar_torneo(conexion, id_torneo):
  if torneo_repo.obtener(conexion, id_torneo) is None:
    raise HTTPException(status_code=404, detail="No se encontró un torneo con ese id")


@router.get("")
def listar_torneos(usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return torneo_repo.listar(conexion)
  finally:
    conexion.close()


@router.get("/{id_torneo}")
def obtener_torneo(id_torneo: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    verificar_torneo(conexion, id_torneo)
    return torneo_repo.obtener(conexion, id_torneo)
  finally:
    conexion.close()


@router.post("", status_code=201)
def crear_torneo(datos: TorneoDatos, usuario = Depends(solo_admin)):
  validar_fechas(datos)
  conexion = conectar()
  try:
    id_nuevo = torneo_repo.crear(conexion, datos.nombre, datos.anio, datos.semestre, datos.fecha_inicio, datos.fecha_fin)
    return torneo_repo.obtener(conexion, id_nuevo)
  except mysql.connector.IntegrityError as error:
    error_de_integridad(error)
  finally:
    conexion.close()


@router.put("/{id_torneo}")
def actualizar_torneo(id_torneo: int, datos: TorneoDatos, usuario = Depends(solo_admin)):
  validar_fechas(datos)
  conexion = conectar()
  try:
    verificar_torneo(conexion, id_torneo)
    torneo_repo.actualizar(conexion, id_torneo, datos.nombre, datos.anio, datos.semestre, datos.fecha_inicio, datos.fecha_fin)
    return torneo_repo.obtener(conexion, id_torneo)
  except mysql.connector.IntegrityError as error:
    error_de_integridad(error)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()


@router.patch("/{id_torneo}/estado")
def cambiar_estado_torneo(id_torneo: int, datos: EstadoNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    verificar_torneo(conexion, id_torneo)
    torneo_repo.cambiar_estado(conexion, id_torneo, datos.estado)
    return torneo_repo.obtener(conexion, id_torneo)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()