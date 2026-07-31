import psycopg

class Conexion():

    def __init__(self):
        self.conexion = psycopg.connect(
            host="localhost",
            dbname="dbmareva",
            user="postgres",
            password="1234",
            port=5432
        )

    def obtener_conexion(self):
        return self.conexion





