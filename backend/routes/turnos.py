from db import conectar
from repositories import turno_repo
from fastapi import APIRouter, Depends
from auth import usuario_actual, ROL_A_DB

router = APIRouter(prefix="/turnos", tags=["Turnos"])


@router.get("")
def listar_turnos(usuario = Depends(usuario_actual)):
  conexion = conectar(ROL_A_DB[usuario["rol"]])
  try:
    return turno_repo.listar(conexion)
  finally:
    conexion.close()