from fastapi import FastAPI

from routes import facultades
from routes import login
from routes import turnos
from routes import usuarios
from routes import complejos
from routes import jugadores
from routes import canchas
from routes import torneos
from routes import equipos
from routes import partidos
from routes import planilla
from routes import sancion
from routes import reportes

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)
app.include_router(turnos.router)
app.include_router(usuarios.router)
app.include_router(complejos.router)
app.include_router(jugadores.router)
app.include_router(canchas.router)
app.include_router(torneos.router)
app.include_router(equipos.router)
app.include_router(partidos.router)
app.include_router(planilla.router)
app.include_router(sancion.router)
app.include_router(reportes.router)
