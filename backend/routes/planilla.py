from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector
from db import conectar
from auth import usuario_actual, ROL_A_DB
from errores import error_de_regla
from repositories import planilla_repo

class JugadorPlanilla(BaseModel):
  ci_jugador: str = Field(pattern=r"^[0-9]{7,8}$")
  id_equipo: int

router = APIRouter(prefix="/partidos", tags=["Planilla"])


def verificar_plazo(conexion, id_partido):
  partido = planilla_repo.plazo_partido(conexion, id_partido)
  if partido is None:
    raise HTTPException(status_code=404, detail="No existe un partido con ese id")
  if partido["vencido"]:
    raise HTTPException(status_code=400, detail="Pasaron más de 48 horas desde el partido; la planilla ya no se puede modificar")


@router.get("/{id_partido}/planilla")
def listar_planilla(id_partido: int, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    if planilla_repo.plazo_partido(conexion, id_partido) is None:
      raise HTTPException(status_code=404, detail="No existe un partido con ese id")
    return planilla_repo.listar(conexion, id_partido)
  finally:
    conexion.close()


@router.post("/{id_partido}/planilla", status_code=201)
def agregar_jugador(id_partido: int, datos: JugadorPlanilla, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    verificar_plazo(conexion, id_partido)
    planilla_repo.agregar(conexion, id_partido, datos.ci_jugador, datos.id_equipo)
    return {"id_partido": id_partido, **datos.model_dump()}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1062:
      raise HTTPException(status_code=409, detail="El jugador ya está en la planilla de este partido")
    if error.errno == 1452:
      raise HTTPException(status_code=400, detail="El jugador o el equipo no existen")
    raise
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()


@router.delete("/{id_partido}/planilla/{ci_jugador}", status_code=204)
def quitar_jugador(id_partido: int, ci_jugador: str, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    verificar_plazo(conexion, id_partido)
    if not planilla_repo.esta_en_planilla(conexion, id_partido, ci_jugador):
      raise HTTPException(status_code=404, detail="El jugador no está en la planilla de este partido")
    planilla_repo.quitar(conexion, id_partido, ci_jugador)
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()