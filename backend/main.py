from fastapi import FastAPI

from routes import facultades
from routes import login
from backend.routes import turnos

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)
app.include_router(turnos.router)