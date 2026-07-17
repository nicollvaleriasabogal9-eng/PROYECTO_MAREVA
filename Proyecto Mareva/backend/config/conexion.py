import psycopg

class Conexion():
    
    def conectar():
        conexion = psycopg.connect(
        host="localhost",
        dbname="dbmareva",
        user="postgres",
        password="1234",
        port=5432
    )
        return conexion





