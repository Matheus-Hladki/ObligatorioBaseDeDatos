from fastapi import APIRouter, HTTPException, Depends
from db import conectar
from auth import usuario_actual, ROL_A_DB
from repositories import partido_repo

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