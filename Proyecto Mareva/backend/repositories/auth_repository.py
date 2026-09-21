from config.conexion import Conexion
from models.cliente import Cliente
from werkzeug.security import generate_password_hash
from psycopg.errors import UniqueViolation


class AuthRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()
    # Guarda un nuevo usuario en la base de datos
    def guardar_usuario(self, nombre, apellido, tipo_documento, numero_documento, telefono, codigo, correo, password, acepta_politica_no_reembolso=False):
        cursor = self.conexion.cursor() 
        password_hash = generate_password_hash(password)# encripta la contraseña antes de guardarla en la base de datos

        try:
            cursor.execute("""INSERT INTO cliente(nombre, apellido, tipo_documento, numero_documento, telefono, correo, contrasena, acepta_politica_no_reembolso, fecha_aceptacion_politica, version_politica)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, '1.0')""",
                            (nombre, apellido, tipo_documento, numero_documento, telefono, correo, password_hash, acepta_politica_no_reembolso))

            self.conexion.commit()
            cursor.close()
            return {"ok": True}

        except UniqueViolation as e:
            self.conexion.rollback()
            cursor.close()
            # Manejo de errores de violación de unicidad para correo y número de documento
            mensaje = str(e)
            if "cliente_correo_key" in mensaje:
                return {"ok": False, "campo": "correo", "error": "Ese correo ya está registrado."}
            elif "cliente_numero_documento_key" in mensaje:
                return {"ok": False, "campo": "numero_documento", "error": "Ese número de documento ya está registrado."}
            else:
                return {"ok": False, "campo": None, "error": "Ya existe un usuario con esos datos."}

        except Exception:
            self.conexion.rollback()
            cursor.close()
            return {"ok": False, "campo": None, "error": "No fue posible completar el registro. Intenta de nuevo."}
    # Busca un usuario por su correo electrónico y devuelve un objeto Cliente si se encuentra, o None si no se encuentra
    def buscar_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("SELECT * FROM cliente WHERE correo = %s", (correo,))
            fila = cursor.fetchone()
            cursor.close()
        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None

        if fila is None:
            return None

        usuario = Cliente(
            fila[0], # id_cliente
            fila[1], # nombre
            fila[2], # apellido
            fila[3], # tipo_documento
            fila[4], # numero_documento
            fila[5], # telefono
            fila[6], # correo
            fila[7], # contrasena
            fila[8], # rol
            fila[9], # codigo_referido
            fila[10], # fecha_registro
            fila[11], # estado
            fila[12], # intentos_fallidos
            fila[13], # bloqueado_hasta
            fila[14], # acepta_politica_no_reembolso
            fila[15], # fecha_aceptacion_politica
            fila[16], # version_politica
            fila[17]  # id_nivel
        )

        return usuario
    
    # Obtiene la contraseña de un usuario por su correo electrónico
    def estado_acceso_cliente(self, correo):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_cliente, estado, intentos_fallidos, bloqueado_hasta FROM cliente WHERE correo=%s", (correo,))
        fila = cursor.fetchone()
        cursor.close()
        return fila

    def registrar_intento_fallido(self, correo, bloquear_hasta=None):
        cursor = self.conexion.cursor()
        if bloquear_hasta:
            cursor.execute("UPDATE cliente SET intentos_fallidos=5, bloqueado_hasta=%s WHERE correo=%s", (bloquear_hasta, correo))
        else:
            cursor.execute("UPDATE cliente SET intentos_fallidos=intentos_fallidos+1 WHERE correo=%s", (correo,))
        self.conexion.commit()
        cursor.close()

    def limpiar_intentos(self, correo):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE cliente SET intentos_fallidos=0, bloqueado_hasta=NULL WHERE correo=%s", (correo,))
        self.conexion.commit()
        cursor.close()

    def obtener_password_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("SELECT contrasena FROM cliente WHERE correo = %s", (correo,))
            fila = cursor.fetchone()
            cursor.close()
        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None

        if fila is None:
            return None

        return fila[0]
    
    # Obtiene todos los IDs y contraseñas de los usuarios en la base de datos
    def obtener_todos_id_password(self):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("SELECT id_cliente, contrasena FROM cliente")
            filas = cursor.fetchall()
            cursor.close()
            return filas
        
        except Exception:
            self.conexion.rollback()
            cursor.close()
            return []

    def buscar_guia_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT id_guia, nombre, apellido, correo, contrasena, estado
                FROM guia_turistico
                WHERE correo = %s
            """, (correo,))

            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            return {
                "id": fila[0],
                "nombre": fila[1],
                "apellido": fila[2],
                "correo": fila[3],
                "contrasena": fila[4],
                "estado": fila[5],
                "rol": "guia"
            }

        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None


    def obtener_guia_password_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT contrasena
                FROM guia_turistico
                WHERE correo = %s
            """, (correo,))

            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            return fila[0]

        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None

    def buscar_proveedor_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT id_proveedor, nombre, correo, contrasena, estado
                FROM proveedor
                WHERE correo = %s
            """, (correo,))

            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            return {
                "id": fila[0],
                "nombre": fila[1],
                "correo": fila[2],
                "contrasena": fila[3],
                "estado": fila[4],
                "rol": "proveedor"
            }

        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None


    def obtener_proveedor_password_por_correo(self, correo):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT contrasena
                FROM proveedor
                WHERE correo = %s
            """, (correo,))

            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            return fila[0]

        except Exception:
            self.conexion.rollback()
            cursor.close()
            return None
    def obtener_favoritos_cliente(self, id_cliente):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_paquete FROM favoritos WHERE id_cliente=%s ORDER BY fecha_agregado DESC", (id_cliente,))
        ids = [fila[0] for fila in cursor.fetchall()]
        cursor.close()
        return ids

    def actualizar_correo(self, id_cliente, correo):
        cursor = self.conexion.cursor()
        try:
            cursor.execute("UPDATE cliente SET correo=%s WHERE id_cliente=%s", (correo, id_cliente))
            self.conexion.commit()
            actualizado = cursor.rowcount > 0
            cursor.close()
            return {"ok": actualizado}
        except UniqueViolation:
            self.conexion.rollback()
            cursor.close()
            return {"ok": False, "error": "Ese correo ya está registrado."}
        except Exception:
            self.conexion.rollback()
            cursor.close()
            return {"ok": False, "error": "No fue posible actualizar el correo."}

    def actualizar_password(self, id_cliente, password_hash):
        cursor = self.conexion.cursor()
        try:
            cursor.execute("UPDATE cliente SET contrasena=%s WHERE id_cliente=%s", (password_hash, id_cliente))
            self.conexion.commit()
            actualizado = cursor.rowcount > 0
            cursor.close()
            return actualizado
        except Exception:
            self.conexion.rollback()
            cursor.close()
            return False

    def obtener_password_por_id(self, id_cliente):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT contrasena FROM cliente WHERE id_cliente=%s", (id_cliente,))
        fila = cursor.fetchone()
        cursor.close()
        return fila[0] if fila else None
