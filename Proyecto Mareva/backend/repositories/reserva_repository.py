from config.conexion import Conexion
import random
import string


class ReservaRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def crear_reserva(self, id_cliente, id_paquete, cant_adultos, cant_menores,
                       fecha_viaje, observaciones, acepta_no_reembolso, alergias, mascotas, plan, metodo_contacto):
        cursor = self.conexion.cursor()
        codigo_unico = self._generar_codigo()

        try:
            cursor.execute("""
                INSERT INTO reserva
                    (codigo_unico, fecha_viaje, cant_adultos, cant_menores,
                     observaciones, acepta_no_reembolso, alergias, mascotas, plan, metodo_contacto,
                     id_cliente, id_paquete)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_reserva
            """, (codigo_unico, fecha_viaje, cant_adultos, cant_menores,
                  observaciones, acepta_no_reembolso, alergias, mascotas, plan, metodo_contacto,
                  id_cliente, id_paquete))

            id_reserva = cursor.fetchone()[0]
            self.conexion.commit()
            cursor.close()
            return {"ok": True, "id_reserva": id_reserva, "codigo_unico": codigo_unico}

        except Exception as e:
            self.conexion.rollback()
            cursor.close()


            print("========== ERROR CREANDO RESERVA ==========")
            print(type(e).__name__)
            print(str(e))
            print("============================================")

            mensaje = str(e)



            if "CUPOS_INSUFICIENTES" in mensaje:
                return {"ok": False, "error": "No hay cupos suficientes disponibles para las fechas elegidas."}
            return {"ok": False, "error": "No fue posible procesar la reserva. Intenta de nuevo."}

    def agregar_servicios_extra(self, id_reserva, ids_servicios_extra):
        if not ids_servicios_extra:
            return
        cursor = self.conexion.cursor()
        for id_extra in ids_servicios_extra:
            cursor.execute(
                "INSERT INTO reserva_servicio_extra (id_reserva, id_servicio_extra) VALUES (%s, %s)",
                (id_reserva, id_extra)
            )
        self.conexion.commit()
        cursor.close()

    def agregar_viajeros(self, id_reserva, viajeros):
        """viajeros: lista de dicts {nombre, apellido, tipo_documento, numero_documento}"""
        if not viajeros:
            return
        cursor = self.conexion.cursor()
        for v in viajeros:
            cursor.execute("""
                INSERT INTO viajero_reserva (nombre, apellido, tipo_documento, numero_documento, id_reserva)
                VALUES (%s, %s, %s, %s, %s)
            """, (v["nombre"], v["apellido"], v["tipo_documento"], v["numero_documento"], id_reserva))
        self.conexion.commit()
        cursor.close()

    def obtener_ultima_reserva_cliente(self, id_cliente):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT r.id_reserva, r.codigo_unico, r.fecha_reserva, r.estado, p.nombre, r.fecha_viaje
              FROM reserva r
              JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
             WHERE r.id_cliente = %s
             ORDER BY r.id_reserva DESC
             LIMIT 1
        """, (id_cliente,))
        fila = cursor.fetchone()
        cursor.close()
        if not fila:
            return None
        return {
            "id_reserva": fila[0], "codigo_unico": fila[1], "fecha_reserva": fila[2], "estado": fila[3],
            "paquete_nombre": fila[4],  "fecha_viaje": fila[5],
        }

    def listar_reservas_admin(self):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_viaje,
                    r.estado,
                    c.nombre,
                    c.correo,
                    p.nombre
                FROM reserva r
                JOIN cliente c
                    ON c.id_cliente = r.id_cliente
                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete
                ORDER BY r.id_reserva DESC
            """)

            filas = cursor.fetchall()

            return [
                {
                    "id_reserva": fila[0],
                    "codigo_unico": fila[1],
                    "fecha_viaje": fila[2],
                    "estado": fila[3],
                    "cliente_nombre": fila[4],
                    "cliente_correo": fila[5],
                    "paquete_nombre": fila[6]
                }
                for fila in filas
            ]

        finally:
            cursor.close()

    def obtener_viajeros_reserva(self, id_reserva):

        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT id_viajero_reserva,
                   nombre,
                   apellido,
                   tipo_documento,
                   numero_documento
            FROM viajero_reserva
            WHERE id_reserva = %s
            ORDER BY id_viajero
        """, (id_reserva,))

        filas = cursor.fetchall()
        cursor.close()

        return [
            {
              "id_viajero": fila[0],
              "nombre": fila[1],
              "apellido": fila[2],
              "tipo_documento": fila[3],
              "numero_documento": fila[4]
            }
             for fila in filas
        ]

    def obtener_reserva_cliente(self, id_reserva, id_cliente):

        cursor = self.conexion.cursor()

        cursor.execute("""
           SELECT id_reserva,
                 id_cliente,
                 estado
          FROM reserva
            WHERE id_reserva = %s
              AND id_cliente = %s
        """, (id_reserva, id_cliente))

        fila = cursor.fetchone()
        cursor.close()

        if not fila:
            return None

        return {
            "id_reserva": fila[0],
            "id_cliente": fila[1],
            "estado": fila[2]
        }

    def actualizar_viajero(
        self,
        id_viajero,
        id_cliente,
        nombre,
        apellido,
        tipo_documento,
        numero_documento
    ):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                UPDATE viajero_reserva vr
                SET nombre = %s,
                    apellido = %s,
                    tipo_documento = %s,
                    numero_documento = %s
                FROM reserva r
                WHERE vr.id_viajero = %s
                    AND vr.id_reserva = r.id_reserva
                    AND r.id_cliente = %s
                    AND r.estado IN ('solicitada', 'pendiente a pago')
            """, (
                nombre,
                apellido,
                tipo_documento,
                numero_documento,
                id_viajero,
                id_cliente
            ))

            if cursor.rowcount == 0:
                self.conexion.rollback()
                cursor.close() 

                return {
                    "ok": False,
                    "error": "No puedes modificar este viajero"
                }
            
            self.conexion.commit()
            cursor.close()

            return {
                "ok": True
            }

        except Exception as e:
            self.conexion.rollback()
            cursor.close()

            print("ERROR ACTUALIZANDO VIAJERO:", e)

            return {
                "ok": False,
                "error": "No fue posible actualizar la información del viajero."
            }

    def obtener_reserva_con_viajeros(self, id_reserva, id_cliente):
        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.codigo_unico,
                r.estado,
                p.nombre,
                vr.id_viajero,
                vr.nombre,
                vr.apellido,
                vr.tipo_documento,
                vr.numero_documento
            FROM reserva r
            JOIN paquete_turistico p
                ON p.id_paquete = r.id_paquete
            LEFT JOIN viajero_reserva vr
                ON vr.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
              AND r.id_cliente = %s
            ORDER BY vr.id_viajero
        """, (id_reserva, id_cliente))

        filas = cursor.fetchall()
        cursor.close()

        if not filas:
            return None

        reserva = {
            "id_reserva": filas[0][0],
            "codigo_unico": filas[0][1],
            "estado": filas[0][2],
            "paquete_nombre": filas[0][3],
            "viajeros": []
        }

        for fila in filas:
            if fila[4] is not None:
                reserva["viajeros"].append({
                    "id_viajero": fila[4],
                    "nombre": fila[5],
                    "apellido": fila[6],
                    "tipo_documento": fila[7],
                    "numero_documento": fila[8]
                })

        return reserva

    def obtener_datos_encuesta(self, id_reserva):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.estado,
                    c.id_cliente,
                    c.nombre,
                    c.correo
                FROM reserva r
                JOIN cliente c
                    ON c.id_cliente = r.id_cliente
                WHERE r.id_reserva = %s
            """, (id_reserva,))

            fila = cursor.fetchone()

            if not fila:
                return None

            return {
                "id_reserva": fila[0],
                "estado": fila[1],
                "id_cliente": fila[2],
                "nombre": fila[3],
                "correo": fila[4]
            }

        finally:
            cursor.close()

    def marcar_completada(self, id_reserva):

        cursor = self.conexion.cursor()

        try:

            cursor.execute("""
                UPDATE reserva
                SET estado = 'completada'
                WHERE id_reserva = %s
                    AND estado <> 'completada'
                RETURNING id_reserva
            """, (id_reserva,))

            fila = cursor.fetchone()

            if not fila:
                self.conexion.rollback()

                return {
                    "ok": False,
                    "error": "No se pudo completar la reserva."
                }

            self.conexion.commit()

            return {
                "ok": True
            }

        except Exception as e:

            self.conexion.rollback()

            print("ERROR COMPLETANDO RESERVA:", e)

            return {
                "ok": False,
                "error": "No fue posible completar la reserva."
            }

        finally:
            cursor.close()

    @staticmethod
    def _generar_codigo():
        return "MRV-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))