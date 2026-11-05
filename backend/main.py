from fastapi import FastAPI

from routes import facultades
from routes import login

app = FastAPI()

app.include_router(facultades.router)
app.include_router(login.router)