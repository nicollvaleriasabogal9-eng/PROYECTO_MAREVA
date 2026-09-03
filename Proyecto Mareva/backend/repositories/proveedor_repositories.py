from config.conexion import Conexion
from werkzeug.security import generate_password_hash
from psycopg.errors import UniqueViolation


class ProveedorRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def registrar_proveedor(
        self,
        nombre,
        nit,
        tipo_empresa,
        descripcion,
        direccion,
        ciudad,
        telefono,
        correo,
        contrasena,
        nombre_contacto,
        telefono_contacto,
        correo_contacto
    ):
        cursor = self.conexion.cursor()

        password_hash = generate_password_hash(contrasena)

        try:
            cursor.execute("""
                INSERT INTO proveedor (
                    nombre,
                    nit,
                    tipo_empresa,
                    descripcion,
                    direccion,
                    ciudad,
                    telefono,
                    correo,
                    contrasena,
                    nombre_contacto,
                    telefono_contacto,
                    correo_contacto
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """, (
                nombre,
                nit,
                tipo_empresa,
                descripcion,
                direccion,
                ciudad,
                telefono,
                correo,
                password_hash,
                nombre_contacto,
                telefono_contacto,
                correo_contacto
            ))

            self.conexion.commit()
            cursor.close()

            return {
                "ok": True
            }

        except UniqueViolation as e:
            self.conexion.rollback()
            cursor.close()

            mensaje = str(e)

            if "correo" in mensaje:
                return {
                    "ok": False,
                    "campo": "correo",
                    "error": "Ese correo ya está registrado."
                }

            if "nit" in mensaje:
                return {
                    "ok": False,
                    "campo": "nit",
                    "error": "Ese NIT ya está registrado."
                }

            return {
                "ok": False,
                "campo": None,
                "error": "Ya existe un proveedor con esos datos."
            }

        except Exception:
            self.conexion.rollback()
            cursor.close()

            return {
                "ok": False,
                "campo": None,
                "error": "No fue posible registrar el proveedor."
            }