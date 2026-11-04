from fastapi import FastAPI

from routes import facultades

app = FastAPI()

app.include_router(facultades.router)