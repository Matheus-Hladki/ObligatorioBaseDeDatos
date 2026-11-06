from fastapi import FastAPI

from routes import facultades
from routes import login
from routes import turnos
from routes import usuarios
from routes import complejos
from routes import jugadores
from routes import canchas
from routes import torneos

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)
app.include_router(turnos.router)
app.include_router(usuarios.router)
app.include_router(complejos.router)
app.include_router(jugadores.router)
app.include_router(canchas.router)
app.include_router(torneos.router)
