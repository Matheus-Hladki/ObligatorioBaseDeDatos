# Creo archivo para probar funcionamiento basico

from fastapi import FastAPI

app = FastAPI()

@app.get("/hola")
def hola():
    return {"mensaje": "funciona"}