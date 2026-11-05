from fastapi import FastAPI

from routes import facultades
from routes import login
from routes import turnos
from routes import usuarios
from routes import complejos

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)
app.include_router(turnos.router)
app.include_router(usuarios.router)
app.include_router(complejos.router)
