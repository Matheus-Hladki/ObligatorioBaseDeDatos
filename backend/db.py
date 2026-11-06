import os

from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

def conectar(role="ADMIN"):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv(f"DB_{role}_USER"),
        password=os.getenv(f"DB_{role}_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        collation="utf8mb4_spanish_ci",
    )
