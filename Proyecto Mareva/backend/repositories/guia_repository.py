from config.conexion import Conexion


class GuiaRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def obtener_perfil(self, id_guia):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT id_guia, nombre, apellido, idiomas, especialidad,
                   telefono, correo, estado
              FROM guia_turistico
             WHERE id_guia = %s
        """, (id_guia,))
        fila = cursor.fetchone()
        cursor.close()
        if not fila:
            return None
        return {
            "id_guia": fila[0],
            "nombre": fila[1],
            "apellido": fila[2],
            "idiomas": fila[3],
            "especialidad": fila[4],
            "telefono": fila[5],
            "correo": fila[6],
            "estado": fila[7],
        }

    def obtener_resumen(self, id_guia):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id_paquete) FILTER (
                       WHERE p.estado = 'activo'
                   ) AS paquetes_activos,
                   COUNT(r.id_reserva) FILTER (
                       WHERE r.estado NOT IN ('completada', 'cancelada')
                   ) AS reservas_pendientes,
                   COALESCE(SUM(r.cant_adultos + r.cant_menores) FILTER (
                       WHERE r.estado NOT IN ('completada', 'cancelada')
                   ), 0) AS viajeros_pendientes,
                   COUNT(r.id_reserva) FILTER (
                       WHERE r.estado = 'completada'
                   ) AS viajes_completados
              FROM paquete_turistico p
              LEFT JOIN reserva r ON r.id_paquete = p.id_paquete
             WHERE p.id_guia = %s
        """, (id_guia,))
        fila = cursor.fetchone()
        cursor.close()
        return {
            "paquetes_activos": fila[0] or 0,
            "reservas_pendientes": fila[1] or 0,
            "viajeros_pendientes": fila[2] or 0,
            "viajes_completados": fila[3] or 0,
        }

    def obtener_paquetes(self, id_guia):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT p.id_paquete, p.nombre, p.imagen_url, d.nombre_destino,
                   d.departamento, p.fecha_inicio, p.fecha_fin,
                   p.cupos_totales, p.cupos_disponibles, p.estado,
                   COUNT(r.id_reserva) FILTER (
                       WHERE r.estado <> 'cancelada'
                   ) AS total_reservas
              FROM paquete_turistico p
              JOIN destino d ON d.id_destino = p.id_destino
              LEFT JOIN reserva r ON r.id_paquete = p.id_paquete
             WHERE p.id_guia = %s
             GROUP BY p.id_paquete, p.nombre, p.imagen_url, d.nombre_destino,
                      d.departamento, p.fecha_inicio, p.fecha_fin,
                      p.cupos_totales, p.cupos_disponibles, p.estado
             ORDER BY p.fecha_inicio NULLS LAST, p.nombre
        """, (id_guia,))
        paquetes = [
            {
                "id_paquete": fila[0],
                "nombre": fila[1],
                "imagen_url": fila[2],
                "destino": fila[3],
                "departamento": fila[4],
                "fecha_inicio": fila[5],
                "fecha_fin": fila[6],
                "cupos_totales": fila[7],
                "cupos_disponibles": fila[8],
                "estado": fila[9],
                "total_reservas": fila[10],
            }
            for fila in cursor.fetchall()
        ]
        cursor.close()
        return paquetes

    def obtener_reservas(self, id_guia, estado=None):
        cursor = self.conexion.cursor()

        parametros = [id_guia]
        filtro = ""

        if estado:
            filtro = " AND r.estado = %s"
            parametros.append(estado)

        cursor.execute("""
           SELECT
                r.id_reserva,
                r.codigo_unico,
                r.fecha_reserva,
                r.fecha_viaje,
                r.estado,
                r.cant_adultos,
                r.cant_menores,
                r.observaciones,
                r.valor_referencial,

                c.nombre,
                c.apellido,
                c.telefono,
                c.correo,

                p.nombre,
                p.imagen_url,
                d.nombre_destino

            FROM reserva r

            JOIN paquete_turistico p
                ON p.id_paquete = r.id_paquete

            JOIN destino d
                ON d.id_destino = p.id_destino

            JOIN cliente c
                ON c.id_cliente = r.id_cliente

            WHERE p.id_guia = %s
        """ + filtro + """

            ORDER BY
                CASE r.estado
                    WHEN 'en_proceso' THEN 1
                    WHEN 'confirmada' THEN 2
                    WHEN 'solicitada' THEN 3
                    WHEN 'completada' THEN 4
                    ELSE 5
                END,
                r.fecha_viaje NULLS LAST,
                r.id_reserva DESC

        """, tuple(parametros))

        reservas = [
            {
                "id_reserva": fila[0],
                "codigo_unico": fila[1],
                "fecha_reserva": fila[2],
                "fecha_viaje": fila[3],
                "estado": fila[4],
                "cant_adultos": fila[5],
                "cant_menores": fila[6],
                "observaciones": fila[7],
                "valor_final": fila[8],

                "cliente_nombre": f"{fila[9]} {fila[10]}",
                "cliente_telefono": fila[11],
                "cliente_correo": fila[12],

                "paquete_nombre": fila[13],
                "imagen_url": fila[14],
                "destino": fila[15],

                "total_viajeros": (fila[5] or 0) + (fila[6] or 0),
            }
            for fila in cursor.fetchall()
        ]

        cursor.close()

        return reservas

    def actualizar_estado_reserva(self, id_guia, id_reserva, nuevo_estado):
        cursor = self.conexion.cursor()
        cursor.execute("""
            UPDATE reserva r
               SET estado = %s
              FROM paquete_turistico p
             WHERE r.id_reserva = %s
               AND p.id_paquete = r.id_paquete
               AND p.id_guia = %s
            RETURNING r.id_reserva
        """, (nuevo_estado, id_reserva, id_guia))
        actualizado = cursor.fetchone() is not None
        self.conexion.commit()
        cursor.close()
        return actualizado

    def obtener_estado_reserva(self, id_guia, id_reserva):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT r.estado
              FROM reserva r
              JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
             WHERE r.id_reserva = %s
               AND p.id_guia = %s
        """, (id_reserva, id_guia))
        fila = cursor.fetchone()
        cursor.close()
        return fila[0] if fila else None
