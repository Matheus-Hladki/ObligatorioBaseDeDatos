from fastapi import HTTPException


def error_de_regla(error):
    if error.errno == 1644:
        raise HTTPException(status_code=400, detail=error.msg)
    raise error