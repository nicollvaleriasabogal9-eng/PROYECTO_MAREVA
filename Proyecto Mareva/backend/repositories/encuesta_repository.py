from config.conexion import Conexion


class EncuestaRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def obtener_preguntas_activas(self):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    id_pregunta,
                    texto,
                    tipo_respuesta,
                    orden
                FROM encuesta_pregunta
                WHERE estado = TRUE
                ORDER BY orden ASC, id_pregunta ASC
            """)

            filas = cursor.fetchall()

            return [
                {
                    "id_pregunta": fila[0],
                    "texto": fila[1],
                    "tipo_respuesta": fila[2],
                    "orden": fila[3]
                }
                for fila in filas
            ]

        finally:
            cursor.close()

    def verificar_reserva_cliente(self, id_reserva, id_cliente):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    r.id_reserva,
                    r.id_cliente,
                    r.estado,
                    p.nombre
                FROM reserva r
                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete
                WHERE r.id_reserva = %s
                  AND r.id_cliente = %s
            """, (id_reserva, id_cliente))

            fila = cursor.fetchone()

            if not fila:
                return None

            return {
                "id_reserva": fila[0],
                "id_cliente": fila[1],
                "estado": fila[2],
                "paquete_nombre": fila[3]
            }

        finally:
            cursor.close()

    def obtener_todas_preguntas(self):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                SELECT
                    id_pregunta,
                    texto,
                    tipo_respuesta,
                    orden,
                    estado
                FROM encuesta_pregunta
                ORDER BY orden ASC, id_pregunta ASC
            """)

            filas = cursor.fetchall()

            return [
                {
                    "id_pregunta": fila[0],
                    "texto": fila[1],
                    "tipo_respuesta": fila[2],
                    "orden": fila[3],
                    "estado": fila[4]
                }
                for fila in filas
            ]

        finally:
            cursor.close()

    def obtener_pregunta(self, id_pregunta):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                    SELECT
                        id_pregunta,
                        texto,
                        tipo_respuesta,
                        orden,
                        estado
                FROM encuesta_pregunta
                WHERE id_pregunta = %s
            """, (id_pregunta,))

            fila = cursor.fetchone()

            if not fila:
                return None

            return {
                "id_pregunta": fila[0],
                "texto": fila[1],
                "tipo_respuesta": fila[2],
                "orden": fila[3],
                "estado": fila[4]
            }

        finally:
            cursor.close()

    def crear_pregunta(self, texto, tipo_respuesta, orden):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                INSERT INTO encuesta_pregunta
                    (texto, tipo_respuesta, orden, estado)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id_pregunta
            """, (
                texto,
                tipo_respuesta,
                orden
            ))

            id_pregunta = cursor.fetchone()[0]

            self.conexion.commit()

            return {
                "ok": True,
                "id_pregunta": id_pregunta
            }

        except Exception as e:
            self.conexion.rollback()

            print("ERROR CREANDO PREGUNTA:", e)

            return {
                "ok": False,
                "error": "No fue posible crear la pregunta."
            }

        finally:
            cursor.close()


    def actualizar_pregunta(
        self,
        id_pregunta,
        texto,
        tipo_respuesta,
        orden
    ):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                UPDATE encuesta_pregunta
                SET
                    texto = %s,
                    tipo_respuesta = %s,
                    orden = %s
                WHERE id_pregunta = %s
            """, (
                texto,
                tipo_respuesta,
                orden,
                id_pregunta
            ))

            if cursor.rowcount == 0:
                self.conexion.rollback()

                return {
                    "ok": False,
                    "error": "La pregunta no existe."
                }

            self.conexion.commit()

            return {
                "ok": True
            }

        except Exception as e:
            self.conexion.rollback()

            print("ERROR ACTUALIZANDO PREGUNTA:", e)

            return {
                "ok": False,
                "error": "No fue posible actualizar la pregunta."
            }

        finally:
            cursor.close()


    def cambiar_estado_pregunta(self, id_pregunta):
        cursor = self.conexion.cursor()

        try:
            cursor.execute("""
                UPDATE encuesta_pregunta
                SET estado = NOT estado
                WHERE id_pregunta = %s
                RETURNING estado
            """, (id_pregunta,))

            fila = cursor.fetchone()

            if not fila:
                self.conexion.rollback()

                return {
                    "ok": False,
                    "error": "La pregunta no existe."
                }

            nuevo_estado = fila[0]

            self.conexion.commit()

            return {
                "ok": True,
                "estado": nuevo_estado
            }

        except Exception as e:
            self.conexion.rollback()

            print("ERROR CAMBIANDO ESTADO:", e)

            return {
                "ok": False,
                "error": "No fue posible cambiar el estado de la pregunta."
            }

        finally:
            cursor.close()

    def obtener_paquetes_reporte(self):
        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT DISTINCT
                p.id_paquete,
                p.nombre
            FROM paquete_turistico p
            INNER JOIN reserva r
                ON r.id_paquete = p.id_paquete
            INNER JOIN encuesta_respuesta er
                ON er.id_reserva = r.id_reserva
            ORDER BY p.nombre
        """)

        filas = cursor.fetchall()
        cursor.close()

        return [
            {
                "id_paquete": fila[0],
                "nombre": fila[1]
            }
            for fila in filas
        ]


    def obtener_destinos_reporte(self):
        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT DISTINCT
                d.id_destino,
                d.nombre_destino
            FROM destino d
            INNER JOIN paquete_turistico p
                ON p.id_destino = d.id_destino
            INNER JOIN reserva r
                ON r.id_paquete = p.id_paquete
            INNER JOIN encuesta_respuesta er
                ON er.id_reserva = r.id_reserva
            ORDER BY d.nombre_destino
        """)

        filas = cursor.fetchall()
        cursor.close()

        return [
            {
                "id_destino": fila[0],
                "nombre": fila[1]
            }
            for fila in filas
        ]


    def obtener_reporte_encuestas(
        self,
        id_paquete=None,
        id_destino=None,
        fecha_inicio=None,
        fecha_fin=None
    ):
        cursor = self.conexion.cursor()

        query = """
            SELECT
                p.nombre AS paquete,
                d.nombre_destino AS destino,
                ep.id_pregunta,
                ep.texto,
                ep.tipo_respuesta,

                COUNT(er.id_respuesta) AS total_respuestas,

                ROUND(
                    AVG(er.respuesta_numero)::numeric,
                    2
                ) AS promedio,

                er.respuesta_texto,
                MAX(er.fecha) AS fecha

            FROM encuesta_respuesta er

            INNER JOIN encuesta_pregunta ep
                ON ep.id_pregunta = er.id_pregunta

            INNER JOIN reserva r
                ON r.id_reserva = er.id_reserva

            INNER JOIN paquete_turistico p
                ON p.id_paquete = r.id_paquete

            INNER JOIN destino d
                ON d.id_destino = p.id_destino

            WHERE 1 = 1
        """

        parametros = []

        if id_paquete:
            query += """
                AND p.id_paquete = %s
            """
            parametros.append(id_paquete)

        if id_destino:
            query += """
                AND d.id_destino = %s
            """
            parametros.append(id_destino)

        if fecha_inicio:
            query += """
                AND er.fecha::date >= %s
            """
            parametros.append(fecha_inicio)

        if fecha_fin:
            query += """
                AND er.fecha::date <= %s
            """
            parametros.append(fecha_fin)

        query += """
            GROUP BY
                p.nombre,
                d.nombre_destino,
                ep.id_pregunta,
                ep.texto,
                ep.tipo_respuesta,
                er.respuesta_texto

            ORDER BY
                p.nombre,
                d.nombre_destino,
                ep.id_pregunta
        """

        try:
            cursor.execute(query, parametros)

            filas = cursor.fetchall()
            cursor.close()

            return [
                {
                    "paquete": fila[0],
                    "destino": fila[1],
                    "id_pregunta": fila[2],
                    "pregunta": fila[3],
                    "tipo_respuesta": fila[4],
                    "total_respuestas": fila[5],
                    "promedio": float(fila[6])
                    if fila[6] is not None else None,
                    "respuesta_texto": fila[7],
                    "fecha": fila[8]
                }
                for fila in filas
            ]

        except Exception as e:
            cursor.close()
            print("ERROR EN REPORTE DE ENCUESTAS:", e)
            return []
    
