from config.conexion import Conexion
from models.cliente import Cliente

class AuthRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def guardar_usuario(self, nombre, apellido, tipo_documento, numero_documento, telefono, codigo, correo, password):
        cursor = self.conexion.cursor()

        cursor.execute("""INSERT INTO cliente(nombre, apellido, tipo_documento, numero_documento, telefono, correo, contrasena)
	                    VALUES (%s, %s, %s, %s, %s, %s, %s)""", (nombre, apellido, tipo_documento, numero_documento, telefono, correo, password))

        self.conexion.commit()
        cursor.close()

        return True

    def buscar_por_correo(self, correo):
        cursor = self.conexion.cursor()

        cursor.execute("SELECT * FROM cliente WHERE correo = %s", (correo,))

        fila = cursor.fetchone()

        usuario = Cliente(
            fila[0], #usuario.id
            fila[1], #usuario.nombre y asi con todos los demas
            fila[2],
            fila[3],
            fila[4],
            fila[5],
            fila[6],
            fila[7],
            fila[8],
            fila[9],
            fila[10],
            fila[11],
            fila[12],
            fila[13],
            fila[14]
        )

        cursor.close()

        return usuario
        
        