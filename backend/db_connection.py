import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    config = {
        'user': os.environ.get("DB_USER"),
        'password': os.environ.get("DB_PASSWORD"),
        'host': os.environ.get("DB_HOST"),
        'port': int(os.environ.get("DB_PORT", 3306)),  # <-- Añade el puerto
        'database': os.environ.get("DB_NAME")
    }
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None
