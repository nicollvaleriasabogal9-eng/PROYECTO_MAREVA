from config.conexion import Conexion


class GamificacionRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    @staticmethod
    def _nivel_a_dict(fila):
        if not fila:
            return None
        return {
            "id_nivel": fila[0],
            "nombre": fila[1],
            "min_monto": fila[2],
            "min_reservas": fila[3],
            "descripcion": fila[4],
            "porcentaje_descuento": fila[5],
        }

    def obtener_niveles(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT id_nivel, nombre, min_monto, min_reservas,
                   descripcion, porcentaje_descuento
              FROM nivel
             ORDER BY min_monto, min_reservas, id_nivel
        """)
        niveles = [self._nivel_a_dict(fila) for fila in cursor.fetchall()]
        cursor.close()
        return niveles

    def obtener_nivel_cliente(self, id_cliente):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT n.id_nivel, n.nombre, n.min_monto, n.min_reservas,
                   n.descripcion, n.porcentaje_descuento
              FROM cliente c
              LEFT JOIN nivel n ON n.id_nivel = c.id_nivel
             WHERE c.id_cliente = %s
        """, (id_cliente,))
        nivel = self._nivel_a_dict(cursor.fetchone())
        cursor.close()
        return nivel

    def obtener_estadisticas_cliente(self, id_cliente):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FILTER (
                       WHERE r.estado IN ('confirmada', 'completada')
                   ) AS reservas_validas,
                   COALESCE(SUM(COALESCE(r.valor_referencial, p.precio)) FILTER (
                       WHERE r.estado IN ('confirmada', 'completada')
                   ), 0) AS monto_total,
                   COUNT(*) FILTER (
                       WHERE r.estado = 'completada'
                   ) AS viajes_completados
              FROM reserva r
              JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
             WHERE r.id_cliente = %s
        """, (id_cliente,))
        fila = cursor.fetchone()
        cursor.close()
        return {
            "reservas_validas": fila[0] or 0,
            "monto_total": fila[1] or 0,
            "viajes_completados": fila[2] or 0,
        }

    def actualizar_nivel_cliente(self, id_cliente, id_nivel):
        cursor = self.conexion.cursor()
        cursor.execute(
            "UPDATE cliente SET id_nivel = %s WHERE id_cliente = %s",
            (id_nivel, id_cliente),
        )
        actualizado = cursor.rowcount > 0
        self.conexion.commit()
        cursor.close()
        return actualizado

    def crear_notificacion(self, id_cliente, tipo, mensaje):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO notificacion (tipo, mensaje, id_cliente)
            VALUES (%s, %s, %s)
        """, (tipo, mensaje, id_cliente))
        self.conexion.commit()
        cursor.close()

    def obtener_notificaciones_recientes(self, id_cliente, limite=5):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT id_notificacion, tipo, mensaje, fecha, leida
              FROM notificacion
             WHERE id_cliente = %s
             ORDER BY fecha DESC
             LIMIT %s
        """, (id_cliente, limite))
        notificaciones = [
            {
                "id_notificacion": fila[0],
                "tipo": fila[1],
                "mensaje": fila[2],
                "fecha": fila[3],
                "leida": fila[4],
            }
            for fila in cursor.fetchall()
        ]
        cursor.close()
        return notificaciones

    def crear_nivel(self, datos):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO nivel
                (nombre, min_monto, min_reservas, descripcion, porcentaje_descuento)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_nivel
        """, (
            datos["nombre"], datos["min_monto"], datos["min_reservas"],
            datos["descripcion"], datos["porcentaje_descuento"],
        ))
        id_nivel = cursor.fetchone()[0]
        self.conexion.commit()
        cursor.close()
        return id_nivel

    def actualizar_nivel(self, id_nivel, datos):
        cursor = self.conexion.cursor()
        cursor.execute("""
            UPDATE nivel
               SET nombre = %s,
                   min_monto = %s,
                   min_reservas = %s,
                   descripcion = %s,
                   porcentaje_descuento = %s
             WHERE id_nivel = %s
        """, (
            datos["nombre"], datos["min_monto"], datos["min_reservas"],
            datos["descripcion"], datos["porcentaje_descuento"], id_nivel,
        ))
        actualizado = cursor.rowcount > 0
        self.conexion.commit()
        cursor.close()
        return actualizado
