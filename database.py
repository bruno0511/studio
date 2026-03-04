import os
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )

def executar_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params or ())

    resultado = None
    if fetch:
        resultado = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return resultado