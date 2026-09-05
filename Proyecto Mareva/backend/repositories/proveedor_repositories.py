from config.conexion import Conexion
from werkzeug.security import generate_password_hash
from psycopg.errors import UniqueViolation

class ProveedorRepository:

    def __init__(self):
     self.conexion = Conexion().obtener_conexion()

# =========================================================
# REGISTRAR PROVEEDOR
# =========================================================

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

        password_hash = generate_password_hash(
            contrasena
        )

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

# =========================================================
# RF-127
# OBTENER CONTRATOS DEL PROVEEDOR
# =========================================================

    def obtener_contratos_por_proveedor(
        self,
        proveedor_id
    ):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                SELECT
                    c.id_contrato,
                    c.id_proveedor,
                    c.id_paquete,
                    c.descripcion_terminos,
                    c.fecha_inicio,
                    c.fecha_fin,
                    c.condiciones_comerciales,
                    c.estado_contrato,
                    c.fecha_creacion,
                    c.respuesta_proveedor,
                    c.fecha_respuesta,
                    c.firma_proveedor,
                    c.fecha_firma,
                    c.metodo_firma,

                    p.nombre AS nombre_paquete,
                    p.descripcion AS descripcion_paquete,
                    p.precio,
                    p.duracion_dias,
                    p.duracion_noches,

                    d.nombre_destino,
                    d.departamento,
                    d.ciudad

                FROM contrato c

                INNER JOIN paquete_turistico p
                    ON p.id_paquete = c.id_paquete

                LEFT JOIN destino d
                    ON d.id_destino = p.id_destino

                WHERE c.id_proveedor = %s

                ORDER BY
                    CASE
                        WHEN c.estado_contrato = 'pendiente'
                        THEN 1
                        WHEN c.estado_contrato = 'aceptado'
                        THEN 2
                        WHEN c.estado_contrato = 'vigente'
                        THEN 3
                        ELSE 4
                    END,
                    c.fecha_creacion DESC
            """, (
                proveedor_id,
            ))

            columnas = [
                descripcion[0]
                for descripcion in cursor.description
            ]

            contratos = [
                dict(zip(columnas, fila))
                for fila in cursor.fetchall()
            ]

            cursor.close()

            return contratos

        except Exception:

            cursor.close()
            return []

    # =========================================================
    # RF-128
    # OBTENER UN CONTRATO
    # =========================================================

    def obtener_contrato_por_id(
        self,
        id_contrato,
        proveedor_id
    ):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                SELECT
                    c.id_contrato,
                    c.id_proveedor,
                    c.id_paquete,
                    c.descripcion_terminos,
                    c.fecha_inicio,
                    c.fecha_fin,
                    c.condiciones_comerciales,
                    c.estado_contrato,
                    c.fecha_creacion,
                    c.respuesta_proveedor,
                    c.fecha_respuesta,
                    c.firma_proveedor,
                    c.fecha_firma,
                    c.metodo_firma,

                    p.nombre AS nombre_paquete,
                    p.descripcion AS descripcion_paquete,
                    p.precio,
                    p.duracion_dias,
                    p.duracion_noches,
                    p.cupos_totales,
    
                    d.nombre_destino,
                    d.departamento,
                    d.ciudad,
                    d.descripcion AS descripcion_destino

                FROM contrato c

                INNER JOIN paquete_turistico p
                    ON p.id_paquete = c.id_paquete

                LEFT JOIN destino d
                    ON d.id_destino = p.id_destino

                WHERE
                    c.id_contrato = %s
                    AND c.id_proveedor = %s

                LIMIT 1
            """, (
                id_contrato,
                proveedor_id
            ))

            fila = cursor.fetchone()

            if not fila:
                cursor.close()
                return None

            columnas = [
                descripcion[0]
                for descripcion in cursor.description
            ]

            contrato = dict(
                zip(columnas, fila)
            )

            cursor.close()

            return contrato

        except Exception:

            cursor.close()
            return None

# =========================================================
# RF-129
# ACEPTAR / RECHAZAR CONTRATO
# =========================================================

    def responder_contrato(
        self,
        id_contrato,
        proveedor_id,
        decision
    ):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
            UPDATE contrato

                SET
                    respuesta_proveedor = %s,
                    fecha_respuesta = CURRENT_TIMESTAMP,
                    estado_contrato = %s

                WHERE
                    id_contrato = %s
                    AND id_proveedor = %s
                    AND estado_contrato = 'pendiente'

                RETURNING id_contrato
            """, (
                decision,
                decision,
                id_contrato,
                proveedor_id
            ))

            resultado = cursor.fetchone()

            if not resultado:

                self.conexion.rollback()
                cursor.close()

                return {
                    "ok": False,
                    "error": (
                        "No fue posible actualizar el contrato. "
                        "Puede que ya haya sido respondido."
                    )
                }

            self.conexion.commit()
            cursor.close()

            return {
                "ok": True
            }

        except Exception:

            self.conexion.rollback()
            cursor.close()

            return {
                "ok": False,
                "error": "No fue posible responder el contrato."
            }

# =========================================================
# RF-136
# FIRMA ELECTRÓNICA
# =========================================================

    def firmar_contrato(
        self,
        id_contrato,
            proveedor_id
    ):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                UPDATE contrato

                SET
                    firma_proveedor = TRUE,
                    fecha_firma = CURRENT_TIMESTAMP,
                    metodo_firma = 'firma_electronica_mareva'

                WHERE
                    id_contrato = %s
                    AND id_proveedor = %s
                    AND estado_contrato = 'aceptado'
                    AND firma_proveedor = FALSE

                RETURNING id_contrato
            """, (
                id_contrato,
                proveedor_id
            ))

            resultado = cursor.fetchone()

            if not resultado:

                self.conexion.rollback()
                cursor.close()

                return {
                    "ok": False,
                    "error": (
                        "No fue posible realizar la firma. "
                        "Verifique que el contrato esté aceptado "
                        "y aún no haya sido firmado."
                    )
                }

            self.conexion.commit()
            cursor.close()

            return {
                "ok": True,
                "mensaje": "Contrato firmado electrónicamente correctamente."
            }

        except Exception:

            self.conexion.rollback()
            cursor.close()

            return {
                "ok": False,
                "error": "No fue posible realizar la firma electrónica."
            }

