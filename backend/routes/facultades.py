from db import conectar
from repositories import facultad_repo
from fastapi import APIRouter

router = APIRouter(prefix="/facultades", tags=["Facultades"])

@router.get("")
def listar_facultades():
  conexion = conectar()
  try:
    return facultad_repo.listar(conexion)
  finally:
    conexion.close()