from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector
from db import conectar
from auth import usuario_actual, solo_admin, ROL_A_DB
from errores import error_de_regla
from repositories import sancion_repo, partido_repo

class SancionNueva(BaseModel):
  ci_jugador: str = Field(pattern=r"^[0-9]{7,8}$")
  id_torneo: int
  numero_fecha_inicio: int = Field(ge=1, le=127)
  cantidad_fechas: int = Field(ge=1, le=127)

router = APIRouter(prefix="/sanciones", tags=["Sanciones"])


@router.get("")
def listar_sanciones(id_torneo: int, ci_jugador: str | None = None, usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    if not partido_repo.existe_torneo(conexion, id_torneo):
      raise HTTPException(status_code=404, detail="No existe un torneo con ese id")
    return sancion_repo.listar(conexion, id_torneo, ci_jugador)
  finally:
    conexion.close()


@router.post("", status_code=201)
def cargar_sancion(datos: SancionNueva, usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    if not partido_repo.existe_torneo(conexion, datos.id_torneo):
      raise HTTPException(status_code=404, detail="No existe un torneo con ese id")
    id_nuevo = sancion_repo.crear_disciplinaria(conexion, datos.ci_jugador, datos.id_torneo,
                                                datos.numero_fecha_inicio, datos.cantidad_fechas)
    return {"id_sancion": id_nuevo, **datos.model_dump(), "motivo": "disciplinaria"}
  except mysql.connector.IntegrityError as error:
    if error.errno == 1452:
      raise HTTPException(status_code=400, detail="No existe un jugador con esa cédula")
    raise
  except mysql.connector.DatabaseError as error:
    error_de_regla(error)
  finally:
    conexion.close()