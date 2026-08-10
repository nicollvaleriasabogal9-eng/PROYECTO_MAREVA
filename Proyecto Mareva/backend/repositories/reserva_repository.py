from config.conexion import Conexion
import random
import string


class ReservaRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def crear_reserva(self, id_cliente, id_paquete, cant_adultos, cant_menores,
                       fecha_viaje, observaciones, alergias, mascotas, plan, metodo_contacto):
        cursor = self.conexion.cursor()
        codigo_unico = self._generar_codigo()

        try:
            cursor.execute("""
                INSERT INTO reserva
                    (codigo_unico, fecha_viaje, cant_adultos, cant_menores,
                     observaciones, alergias, mascotas, plan, metodo_contacto,
                     id_cliente, id_paquete)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_reserva
            """, (codigo_unico, fecha_viaje, cant_adultos, cant_menores,
                  observaciones, alergias, mascotas, plan, metodo_contacto,
                  id_cliente, id_paquete))

            id_reserva = cursor.fetchone()[0]
            self.conexion.commit()
            cursor.close()
            return {"ok": True, "id_reserva": id_reserva, "codigo_unico": codigo_unico}

        except Exception as e:
            self.conexion.rollback()
            cursor.close()
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
            SELECT r.codigo_unico, r.fecha_reserva, r.estado, p.nombre, p.emoji, r.fecha_viaje
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
            "codigo_unico": fila[0], "fecha_reserva": fila[1], "estado": fila[2],
            "paquete_nombre": fila[3], "paquete_emoji": fila[4], "fecha_viaje": fila[5],
        }

    @staticmethod
    def _generar_codigo():
        return "MRV-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))