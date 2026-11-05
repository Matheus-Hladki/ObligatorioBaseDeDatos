from fastapi import APIRouter, HTTPException, Depends, Query
from db import conectar
from auth import solo_admin
from repositories import reporte_repo, partido_repo

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def reporte_de_torneo(funcion, id_torneo, *extra):
  conexion = conectar()
  try:
    if not partido_repo.existe_torneo(conexion, id_torneo):
      raise HTTPException(status_code=404, detail="No existe un torneo con ese id")
    return funcion(conexion, id_torneo, *extra)
  finally:
    conexion.close()


@router.get("/posiciones")
def posiciones(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.posiciones, id_torneo)


@router.get("/goleadores")
def goleadores(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.goleadores, id_torneo)


@router.get("/fair-play")
def fair_play(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.fair_play, id_torneo)


@router.get("/promedio-goles")
def promedio_goles(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.promedio_goles, id_torneo)


@router.get("/canchas")
def canchas_mas_usadas(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.canchas_mas_usadas, id_torneo)


@router.get("/turnos")
def turnos_mas_usados(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.turnos_mas_usados, id_torneo)


@router.get("/jugadores-por-facultad")
def jugadores_por_facultad(usuario = Depends(solo_admin)):
  conexion = conectar()
  try:
    return reporte_repo.jugadores_por_facultad_y_tipo(conexion)
  finally:
    conexion.close()


@router.get("/jugadores-sin-planilla")
def jugadores_sin_planilla(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.jugadores_sin_planilla, id_torneo)


@router.get("/sanciones")
def sanciones_por_equipo(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.sanciones_por_equipo_y_motivo, id_torneo)


@router.get("/estado-partidos")
def estado_partidos(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.estado_partidos, id_torneo)


@router.get("/resultados")
def resultados(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.resultados, id_torneo)


@router.get("/suspendidos")
def suspendidos(id_torneo: int, numero_fecha: int = Query(ge=1, le=127), usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.suspendidos_en_fecha, id_torneo, numero_fecha)


@router.get("/reprogramaciones")
def reprogramaciones(id_torneo: int, usuario = Depends(solo_admin)):
  return reporte_de_torneo(reporte_repo.historial_reprogramaciones, id_torneo)
