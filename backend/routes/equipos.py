from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector

from db import conectar
from repositories import equipo_repo, torneo_repo
from auth import usuario_actual, solo_admin, ROL_A_DB
from errores import error_de_regla


class JugadorDelPlantel(BaseModel):
  ci_jugador: str = Field(pattern=r"^\d{7,8}$")
  numero_camiseta: int = Field(ge=1, le=99)


class EquipoDatos(BaseModel):
  nombre: str = Field(min_length=1, max_length=100)
  id_facultad: int


class EquipoNuevo(EquipoDatos):
  id_torneo: int
  jugadores: list[JugadorDelPlantel] = []
  ci_capitan: Optional[str] = None


class CapitanNuevo(BaseModel):
  ci_capitan: str = Field(pattern=r"^\d{7,8}$")


router = APIRouter(prefix="/equipos", tags=["Equipos y planteles"])


def error_de_integridad(error):
  if error.errno == 1062:
    if "uq_equipo_nombre_torneo" in error.msg:
      raise HTTPException(status_code=409, detail="Ya existe un equipo con ese nombre en el torneo")
    if "uq_ejt_camiseta" in error.msg:
      raise HTTPException(status_code=409, detail="Ese número de camiseta ya está usado en el equipo")
    raise HTTPException(status_code=409, detail="El jugador ya integra un equipo en este torneo")
  if error.errno in (1452, 1216):
    raise HTTPException(status_code=400, detail="El torneo, la facultad o el jugador indicado no existe")
  raise error


def manejar_error(conexion, error):
  conexion.rollback()
  if isinstance(error, mysql.connector.IntegrityError):
    error_de_integridad(error)
  error_de_regla(error)


def verificar_capitan(conexion, id_equipo, ci_capitan):
  plantel = equipo_repo.listar_plantel(conexion, id_equipo)
  if ci_capitan not in [jugador["ci_jugador"] for jugador in plantel]:
    raise HTTPException(status_code=400, detail="El capitán tiene que ser un jugador del plantel del equipo")


def detalle(conexion, id_equipo):
  equipo = equipo_repo.obtener(conexion, id_equipo)
  if equipo is None:
    raise HTTPException(status_code=404, detail="No se encontró un equipo con ese id")
  equipo["jugadores"] = equipo_repo.listar_plantel(conexion, id_equipo)
  return equipo


@router.get("")
def listar_equipos(id_torneo: Optional[int] = None, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return equipo_repo.listar(conexion, id_torneo)
  finally:
    conexion.close()


@router.get("/{id_equipo}")
def obtener_equipo(id_equipo: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return detalle(conexion, id_equipo)
  finally:
    conexion.close()


@router.post("", status_code=201)
def crear_equipo(datos: EquipoNuevo, usuario = Depends(solo_admin)):
  if datos.ci_capitan is not None and datos.ci_capitan not in [j.ci_jugador for j in datos.jugadores]:
    raise HTTPException(status_code=400, detail="El capitán tiene que ser un jugador del plantel del equipo")
  conexion = conectar()
  try:
    id_equipo = equipo_repo.crear(conexion, datos.nombre, datos.id_torneo, datos.id_facultad)
    for jugador in datos.jugadores:
      equipo_repo.agregar_jugador(conexion, id_equipo, datos.id_torneo, jugador.ci_jugador, jugador.numero_camiseta)
    if datos.ci_capitan is not None:
      equipo_repo.designar_capitan(conexion, id_equipo, datos.ci_capitan)
    conexion.commit()
    return detalle(conexion, id_equipo)
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()


@router.put("/{id_equipo}")
def actualizar_equipo(id_equipo: int, datos: EquipoDatos, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    detalle(conexion, id_equipo)
    equipo_repo.actualizar(conexion, id_equipo, datos.nombre, datos.id_facultad)
    conexion.commit()
    return detalle(conexion, id_equipo)
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()


@router.patch("/{id_equipo}/capitan")
def designar_capitan(id_equipo: int, datos: CapitanNuevo, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    detalle(conexion, id_equipo)
    verificar_capitan(conexion, id_equipo, datos.ci_capitan)
    equipo_repo.designar_capitan(conexion, id_equipo, datos.ci_capitan)
    conexion.commit()
    return detalle(conexion, id_equipo)
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()


@router.post("/{id_equipo}/jugadores", status_code=201)
def agregar_jugador(id_equipo: int, datos: JugadorDelPlantel, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    equipo = detalle(conexion, id_equipo)
    equipo_repo.agregar_jugador(conexion, id_equipo, equipo["id_torneo"], datos.ci_jugador, datos.numero_camiseta)
    conexion.commit()
    return detalle(conexion, id_equipo)
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()


@router.delete("/{id_equipo}/jugadores/{ci_jugador}", status_code=204)
def quitar_jugador(id_equipo: int, ci_jugador: str, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    detalle(conexion, id_equipo)
    if equipo_repo.quitar_jugador(conexion, id_equipo, ci_jugador) == 0:
      raise HTTPException(status_code=404, detail="Ese jugador no está en el plantel del equipo")
    conexion.commit()
  except mysql.connector.IntegrityError as error:
    conexion.rollback()
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="Es el capitán del equipo: primero designe otro capitán")
    raise
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()


@router.delete("/{id_equipo}", status_code=204)
def eliminar_equipo(id_equipo: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    equipo = detalle(conexion, id_equipo)
    if torneo_repo.obtener(conexion, equipo["id_torneo"])["estado"] != "inscripción":
      raise HTTPException(status_code=409, detail="Solo se pueden borrar equipos con el torneo en etapa de inscripción")
    equipo_repo.designar_capitan(conexion, id_equipo, None)
    equipo_repo.eliminar(conexion, id_equipo)
    conexion.commit()
  except mysql.connector.IntegrityError as error:
    conexion.rollback()
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar: el equipo tiene partidos")
    raise
  except mysql.connector.DatabaseError as error:
    manejar_error(conexion, error)
  finally:
    conexion.close()