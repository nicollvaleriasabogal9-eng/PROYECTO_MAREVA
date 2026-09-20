import psycopg
import os
from dotenv import load_dotenv


load_dotenv()

class Conexion():

    #Las credenciales de la base de datos correspondiente se deben poner en el .env 
    def __init__(self):
        self.conexion = psycopg.connect( 
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

    
    def obtener_conexion(self):
        return self.conexion





