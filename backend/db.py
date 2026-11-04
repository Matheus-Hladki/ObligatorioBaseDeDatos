import os

from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_ADMIN_USER"),
        password=os.getenv("DB_ADMIN_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
