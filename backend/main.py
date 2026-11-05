from fastapi import FastAPI

from routes import facultades
from routes import login
from routes import partidos
from routes import planilla
from routes import sancion

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)
app.include_router(partidos.router)
app.include_router(planilla.router)
app.include_router(sancion.router)