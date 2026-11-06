from datetime import date
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector
from db import conectar
from auth import usuario_actual, solo_admin, ROL_A_DB
from errores import error_de_regla
from repositories import partido_repo


class PartidoNuevo(BaseModel):
  id_torneo: int
  numero_fecha: int = Field(ge=1, le=127)
  id_equipo_local: int
  id_equipo_visitante: int
  dia: date
  id_turno: int
  nombre_cancha: str = Field(min_length=1, max_length=50)
  id_complejo: int


class Reprogramacion(BaseModel):
  dia: date
  id_turno: int
  nombre_cancha: str = Field(min_length=1, max_length=50)
  id_complejo: int
  motivo: str = Field(min_length=1, max_length=200)

router = APIRouter(prefix="/partidos", tags=["Partidos"])



@router.get("")
def listar_fixture(id_torneo: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    if not partido_repo.existe_torneo(conexion, id_torneo):
      raise HTTPException(status_code=404, detail="No existe un torneo con ese id")
    return partido_repo.listar_por_torneo(conexion, id_torneo)
  finally:
    conexion.close()

@router.post("", status_code=201)
def programar_partido(datos: PartidoNuevo, usuario = Depends(solo_admin)):
  if datos.id_equipo_local == datos.id_equipo_visitante:
    raise HTTPException(status_code=400, detail="Un equipo no puede jugar contra sí mismo")
  conexion = conectar()
  try:
    if not partido_repo.existe_torneo(conexion, datos.id_torneo):
      raise HTTPException(status_code=404, detail="No existe un torneo con ese id")
    id_nuevo = partido_repo.crear(conexion, datos.id_torneo, datos.numero_fecha,
                                  datos.id_equipo_local, datos.id_equipo_visitante,
                                  datos.dia, datos.id_turno, datos.nombre_cancha,
                                  datos.id_complejo)
    return {"id_partido": id_nuevo, **datos.model_dump(), "estado": "programado"}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="La cancha ya está ocupada en ese día y turno")
    if error.errno == 1452:
      raise HTTPException(status_code=400, detail="El turno o la cancha no existen, o un equipo no pertenece a ese torneo")
    raise
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()

@router.patch("/{id_partido}/cancelar")
def cancelar_partido(id_partido: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if partido_repo.obtener(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    partido_repo.cambiar_estado(conexion, id_partido, "cancelado")
    return partido_repo.obtener(conexion, id_partido)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()

@router.patch("/{id_partido}/jugado")
def marcar_jugado(id_partido: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if partido_repo.obtener(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    partido_repo.cambiar_estado(conexion, id_partido, "jugado")
    return partido_repo.obtener(conexion, id_partido)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()

@router.patch("/{id_partido}/postergar")
def postergar_partido(id_partido: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if partido_repo.obtener(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    partido_repo.cambiar_estado(conexion, id_partido, "postergado")
    return partido_repo.obtener(conexion, id_partido)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()


@router.patch("/{id_partido}/reprogramar")
def reprogramar_partido(id_partido: int, datos: Reprogramacion, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if partido_repo.obtener(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    partido_repo.reprogramar(conexion, id_partido, datos.dia, datos.id_turno,
                             datos.nombre_cancha, datos.id_complejo, datos.motivo)
    return partido_repo.obtener(conexion, id_partido)
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="La cancha ya está ocupada en ese día y turno")
    if error.errno == 1452:
      raise HTTPException(status_code=400, detail="El turno o la cancha no existen")
    raise
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()

@router.delete("/{id_partido}", status_code=204)
def eliminar_partido(id_partido: int, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if partido_repo.obtener(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    partido_repo.eliminar(conexion, id_partido)
  except mysql.connector.IntegrityError as error:
    if error.errno in (1451, 1217):
      raise HTTPException(status_code=409, detail="No se puede borrar, el partido tiene datos asociados")
    raise
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()