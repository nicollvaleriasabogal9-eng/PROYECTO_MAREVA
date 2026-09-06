from config.conexion import Conexion
from datetime import datetime


class ReporteRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    # RF-89: Reporte de reservas por período (rango de fechas)
    def obtener_reservas_por_periodo(self, fecha_inicio, fecha_fin, estado=None):
        """
        Obtiene todas las reservas en un rango de fechas

        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)
            estado: Filtro opcional por estado

        Returns:
            Lista de diccionarios con datos de reservas
        """
        cursor = self.conexion.cursor()

        try:
            if estado:
                cursor.execute("""
                    SELECT
                        r.id_reserva,
                        r.codigo_unico,
                        r.fecha_viaje,
                        r.fecha_reserva,
                        r.estado,
                        r.cant_adultos,
                        r.cant_menores,
                        r.plan,
                        c.nombre AS cliente_nombre,
                        c.correo AS cliente_correo,
                        p.nombre AS paquete_nombre,
                        p.precio
                    FROM reserva r
                    JOIN cliente c ON c.id_cliente = r.id_cliente
                    JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                    WHERE r.fecha_reserva::DATE BETWEEN %s AND %s
                        AND r.estado = %s
                    ORDER BY r.fecha_reserva DESC
                """, (fecha_inicio, fecha_fin, estado))
            else:
                cursor.execute("""
                    SELECT
                        r.id_reserva,
                        r.codigo_unico,
                        r.fecha_viaje,
                        r.fecha_reserva,
                        r.estado,
                        r.cant_adultos,
                        r.cant_menores,
                        r.plan,
                        c.nombre AS cliente_nombre,
                        c.correo AS cliente_correo,
                        p.nombre AS paquete_nombre,
                        p.precio
                    FROM reserva r
                    JOIN cliente c ON c.id_cliente = r.id_cliente
                    JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                    WHERE r.fecha_reserva::DATE BETWEEN %s AND %s
                    ORDER BY r.fecha_reserva DESC
                """, (fecha_inicio, fecha_fin))

            filas = cursor.fetchall()
            return [
                {
                    "id_reserva": fila[0],
                    "codigo_unico": fila[1],
                    "fecha_viaje": fila[2],
                    "fecha_reserva": fila[3],
                    "estado": fila[4],
                    "cant_adultos": fila[5],
                    "cant_menores": fila[6],
                    "plan": fila[7],
                    "cliente_nombre": fila[8],
                    "cliente_correo": fila[9],
                    "paquete_nombre": fila[10],
                    "precio": float(fila[11]) if fila[11] else 0
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_reservas_por_periodo: {e}")
            raise
        finally:
            cursor.close()

    # RF-90: Reporte de paquetes más reservados (ranking)
    def obtener_paquetes_mas_reservados(self, fecha_inicio, fecha_fin, limite=10):
        """
        Obtiene ranking de paquetes con más reservas en un período

        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)
            limite: Top N paquetes

        Returns:
            Lista de diccionarios con ranking
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    p.id_paquete,
                    p.nombre,
                    COUNT(r.id_reserva) AS total_reservas,
                    SUM(r.cant_adultos + r.cant_menores) AS total_personas,
                    ROUND(AVG(p.precio)::NUMERIC, 2) AS precio_promedio,
                    d.nombre_destino AS destino_nombre
                FROM paquete_turistico p
                LEFT JOIN reserva r ON r.id_paquete = p.id_paquete
                    AND r.fecha_reserva::DATE BETWEEN %s AND %s
                LEFT JOIN destino d ON d.id_destino = p.id_destino
                GROUP BY p.id_paquete, p.nombre, d.nombre_destino
                HAVING COUNT(r.id_reserva) > 0
                ORDER BY total_reservas DESC
                LIMIT %s
            """, (fecha_inicio, fecha_fin, limite))

            filas = cursor.fetchall()
            return [
                {
                    "id_paquete": fila[0],
                    "nombre": fila[1],
                    "total_reservas": fila[2],
                    "total_personas": fila[3] or 0,
                    "precio_promedio": float(fila[4]) if fila[4] else 0,
                    "destino_nombre": fila[5]
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_paquetes_mas_reservados: {e}")
            raise
        finally:
            cursor.close()

    # RF-91: Reporte de reservas canceladas
    def obtener_reservas_canceladas(self, fecha_inicio, fecha_fin):
        """
        Obtiene reservas canceladas con motivo y fecha

        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)

        Returns:
            Lista de diccionarios con datos de cancelaciones
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_viaje,
                    r.fecha_reserva,
                    r.observaciones,
                    c.nombre AS cliente_nombre,
                    c.correo AS cliente_correo,
                    c.telefono,
                    p.nombre AS paquete_nombre,
                    p.precio
                FROM reserva r
                JOIN cliente c ON c.id_cliente = r.id_cliente
                JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                WHERE r.estado = 'cancelada'
                    AND r.fecha_reserva::DATE BETWEEN %s AND %s
                ORDER BY r.fecha_reserva DESC
            """, (fecha_inicio, fecha_fin))

            filas = cursor.fetchall()
            return [
                {
                    "id_reserva": fila[0],
                    "codigo_unico": fila[1],
                    "fecha_viaje": fila[2],
                    "fecha_reserva": fila[3],
                    "motivo": fila[4] or "No especificado",
                    "cliente_nombre": fila[5],
                    "cliente_correo": fila[6],
                    "cliente_telefono": fila[7],
                    "paquete_nombre": fila[8],
                    "precio": float(fila[9]) if fila[9] else 0
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_reservas_canceladas: {e}")
            raise
        finally:
            cursor.close()

    # RF-92: Reporte de ingresos esperados
    def obtener_ingresos_esperados(self, fecha_inicio, fecha_fin):
        """
        Calcula ingresos esperados basado en reservas confirmadas

        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)

        Returns:
            Diccionario con estadísticas de ingresos
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    COUNT(r.id_reserva) AS total_reservas,
                    COALESCE(SUM(p.precio), 0) AS ingreso_total,
                    COALESCE(AVG(p.precio), 0) AS ingreso_promedio,
                    COUNT(DISTINCT r.id_cliente) AS clientes_unicos,
                    r.estado
                FROM reserva r
                JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                WHERE r.fecha_reserva::DATE BETWEEN %s AND %s
                    AND r.estado IN ('solicitada', 'pendiente a pago', 'confirmada', 'completada')
                GROUP BY r.estado
                ORDER BY COUNT(r.id_reserva) DESC
            """, (fecha_inicio, fecha_fin))

            filas = cursor.fetchall()

            total_general = 0
            desglose_por_estado = []

            for fila in filas:
                desglose_por_estado.append({
                    "estado": fila[4],
                    "reservas": fila[0],
                    "ingreso": float(fila[1]) if fila[1] else 0,
                    "promedio": float(fila[2]) if fila[2] else 0,
                    "clientes": fila[3]
                })
                total_general += float(fila[1]) if fila[1] else 0

            # Obtener también información total sin filtrar por estado
            cursor.execute("""
                SELECT
                    COUNT(r.id_reserva) AS total_reservas,
                    COALESCE(SUM(p.precio), 0) AS ingreso_total,
                    COALESCE(AVG(p.precio), 0) AS ingreso_promedio,
                    COUNT(DISTINCT r.id_cliente) AS clientes_unicos
                FROM reserva r
                JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                WHERE r.fecha_reserva::DATE BETWEEN %s AND %s
                    AND r.estado IN ('solicitada', 'pendiente a pago', 'confirmada', 'completada')
            """, (fecha_inicio, fecha_fin))

            fila_total = cursor.fetchone()

            return {
                "total_reservas": fila_total[0],
                "ingreso_total": float(fila_total[1]) if fila_total[1] else 0,
                "ingreso_promedio": float(fila_total[2]) if fila_total[2] else 0,
                "clientes_unicos": fila_total[3],
                "desglose_por_estado": desglose_por_estado
            }
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_ingresos_esperados: {e}")
            raise
        finally:
            cursor.close()

    # RF-93: Reporte de destinos por temporada
    def obtener_destinos_por_temporada(self, fecha_inicio, fecha_fin):
        """
        Obtiene destinos más demandados por mes, con disponibilidad y precio promedio

        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)

        Returns:
            Lista de diccionarios con datos de destinos por temporada
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    d.id_destino,
                    d.nombre_destino,
                    TO_CHAR(r.fecha_reserva, 'YYYY-MM') AS mes,
                    COUNT(r.id_reserva) AS cantidad_reservas,
                    SUM(r.cant_adultos + r.cant_menores) AS total_personas,
                    ROUND(AVG(p.precio)::NUMERIC, 2) AS precio_promedio,
                    MAX(p.precio) AS precio_maximo,
                    MIN(p.precio) AS precio_minimo,
                    COUNT(DISTINCT p.id_paquete) AS paquetes_diferentes,
                    SUM(CASE WHEN r.estado = 'completada' THEN 1 ELSE 0 END) AS reservas_completadas
                FROM destino d
                LEFT JOIN paquete_turistico p ON p.id_destino = d.id_destino
                LEFT JOIN reserva r ON r.id_paquete = p.id_paquete
                    AND r.fecha_reserva::DATE BETWEEN %s AND %s
                GROUP BY d.id_destino, d.nombre_destino, TO_CHAR(r.fecha_reserva, 'YYYY-MM')
                HAVING COUNT(r.id_reserva) > 0
                ORDER BY mes DESC, cantidad_reservas DESC
            """, (fecha_inicio, fecha_fin))

            filas = cursor.fetchall()
            return [
                {
                    "id_destino": fila[0],
                    "nombre": fila[1],
                    "mes": fila[2],
                    "cantidad_reservas": fila[3],
                    "total_personas": fila[4] or 0,
                    "precio_promedio": float(fila[5]) if fila[5] else 0,
                    "precio_maximo": float(fila[6]) if fila[6] else 0,
                    "precio_minimo": float(fila[7]) if fila[7] else 0,
                    "paquetes_diferentes": fila[8],
                    "reservas_completadas": fila[9]
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_destinos_por_temporada: {e}")
            raise
        finally:
            cursor.close()