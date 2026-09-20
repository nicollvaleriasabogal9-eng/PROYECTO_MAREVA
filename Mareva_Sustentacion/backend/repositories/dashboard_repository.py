from config.conexion import Conexion


class DashboardRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    # RF-123: Métricas principales del dashboard en tiempo real
    def obtener_metricas_generales(self):
        """
        Devuelve: reservas del día, reservas pendientes de confirmar,
        paquetes con salida próxima (7 días), cupos críticos por agotarse
        e ingresos esperados del mes actual.
        """
        cursor = self.conexion.cursor()

        try:
            # Reservas del día (reservadas hoy)
            cursor.execute("""
                SELECT COUNT(*)
                FROM reserva
                WHERE fecha_reserva::DATE = CURRENT_DATE
            """)
            reservas_del_dia = cursor.fetchone()[0]

            # Reservas pendientes de confirmar
            cursor.execute("""
                SELECT COUNT(*)
                FROM reserva
                WHERE estado = 'solicitada'
            """)
            reservas_pendientes = cursor.fetchone()[0]

            # Paquetes con salida próxima (dentro de los próximos 7 días)
            cursor.execute("""
                SELECT COUNT(*)
                FROM paquete_turistico
                WHERE fecha_inicio BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                    AND estado = 'activo'
            """)
            paquetes_salida_proxima = cursor.fetchone()[0]

            # Cupos críticos por agotarse (<= 3 cupos disponibles, aún activos)
            cursor.execute("""
                SELECT COUNT(*)
                FROM paquete_turistico
                WHERE cupos_disponibles <= 3
                    AND cupos_disponibles > 0
                    AND estado = 'activo'
            """)
            cupos_criticos = cursor.fetchone()[0]

            # Ingresos esperados del mes actual (reservas no canceladas)
            cursor.execute("""
                SELECT COALESCE(SUM(p.precio), 0)
                FROM reserva r
                JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                WHERE DATE_TRUNC('month', r.fecha_reserva::DATE) = DATE_TRUNC('month', CURRENT_DATE)
                    AND r.estado != 'cancelada'
            """)
            ingresos_mes = cursor.fetchone()[0]

            return {
                "reservas_del_dia": reservas_del_dia,
                "reservas_pendientes_confirmar": reservas_pendientes,
                "paquetes_salida_proxima": paquetes_salida_proxima,
                "cupos_criticos": cupos_criticos,
                "ingresos_esperados_mes": float(ingresos_mes) if ingresos_mes else 0
            }
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_metricas_generales: {e}")
            raise
        finally:
            cursor.close()

    # RF-124: Alerta de reservas sin confirmar por más de 3 días
    def obtener_alertas_reservas_sin_confirmar(self):
        """
        Reservas en estado 'pendiente a pago' con más de 3 días sin gestión
        (tomando fecha_reserva como referencia de última gestión).
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_reserva,
                    r.fecha_viaje,
                    c.nombre AS cliente_nombre,
                    c.correo AS cliente_correo,
                    c.telefono,
                    p.nombre AS paquete_nombre,
                    (CURRENT_DATE - r.fecha_reserva::DATE) AS dias_sin_gestion
                FROM reserva r
                JOIN cliente c ON c.id_cliente = r.id_cliente
                JOIN paquete_turistico p ON p.id_paquete = r.id_paquete
                WHERE r.estado = 'pendiente a pago'
                    AND r.fecha_reserva::DATE < CURRENT_DATE - INTERVAL '3 days'
                ORDER BY r.fecha_reserva ASC
            """)

            filas = cursor.fetchall()
            return [
                {
                    "id_reserva": fila[0],
                    "codigo_unico": fila[1],
                    "fecha_reserva": fila[2],
                    "fecha_viaje": fila[3],
                    "cliente_nombre": fila[4],
                    "cliente_correo": fila[5],
                    "cliente_telefono": fila[6],
                    "paquete_nombre": fila[7],
                    "dias_sin_gestion": fila[8]
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_alertas_reservas_sin_confirmar: {e}")
            raise
        finally:
            cursor.close()

    # RF-125: Alerta de paquetes próximos a salir con cupos sin llenar
    def obtener_alertas_paquetes_cupos_disponibles(self):
        """
        Paquetes con fecha de salida en menos de 7 días que aún tienen
        cupos disponibles.
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    p.id_paquete,
                    p.nombre,
                    p.fecha_inicio,
                    p.fecha_fin,
                    p.cupos_disponibles,
                    p.cupos_totales,
                    (p.fecha_inicio - CURRENT_DATE) AS dias_para_salida
                FROM paquete_turistico p
                WHERE p.fecha_inicio BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                    AND p.cupos_disponibles > 0
                    AND p.estado = 'activo'
                ORDER BY p.fecha_inicio ASC
            """)

            filas = cursor.fetchall()
            return [
                {
                    "id_paquete": fila[0],
                    "nombre": fila[1],
                    "fecha_inicio": fila[2],
                    "fecha_fin": fila[3],
                    "cupos_disponibles": fila[4],
                    "cupos_totales": fila[5],
                    "dias_para_salida": fila[6]
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_alertas_paquetes_cupos_disponibles: {e}")
            raise
        finally:
            cursor.close()

    # RF-126: Resumen de niveles de usuarios activos
    def obtener_resumen_niveles_usuarios(self):
        """
        Distribución de clientes activos por nivel.
        """
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    n.id_nivel,
                    n.nombre AS nivel_nombre,
                    n.porcentaje_descuento,
                    COUNT(c.id_cliente) AS cantidad_clientes
                FROM nivel n
                LEFT JOIN cliente c ON c.id_nivel = n.id_nivel
                    AND c.estado = true
                GROUP BY n.id_nivel, n.nombre, n.porcentaje_descuento
                ORDER BY n.id_nivel ASC
            """)

            filas = cursor.fetchall()
            return [
                {
                    "id_nivel": fila[0],
                    "nivel_nombre": fila[1],
                    "porcentaje_descuento": float(fila[2]) if fila[2] else 0,
                    "cantidad_clientes": fila[3]
                }
                for fila in filas
            ]
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en obtener_resumen_niveles_usuarios: {e}")
            raise
        finally:
            cursor.close()