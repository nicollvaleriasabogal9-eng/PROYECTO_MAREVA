from config.conexion import Conexion


class SalidaRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()


    def obtener_por_paquete(
        self,
        id_paquete,
        solo_disponibles=False
    ):
        cursor = self.conexion.cursor()

        query = """
            SELECT
                sp.id_salida,
                sp.id_paquete,
                sp.fecha_salida,
                sp.fecha_regreso,
                sp.estado,
                sp.id_guia,
                sp.observaciones,
                g.nombre,
                g.apellido
            FROM salida_paquete sp
            LEFT JOIN guia_turistico g
                ON g.id_guia = sp.id_guia
            WHERE sp.id_paquete = %s
        """

        params = [id_paquete]


        if solo_disponibles:

            query += """
                AND sp.estado IN ('programada', 'disponible')
                AND sp.fecha_salida >= CURRENT_DATE
            """


        query += """
            ORDER BY sp.fecha_salida ASC
        """


        try:

            cursor.execute(
                query,
                params
            )

            filas = cursor.fetchall()

        finally:

            cursor.close()


        return [

            {
                "id_salida": fila[0],
                "id_paquete": fila[1],
                "fecha_salida": fila[2],
                "fecha_regreso": fila[3],
                "estado": fila[4],
                "id_guia": fila[5],
                "observaciones": fila[6],
                "guia_nombre": (
                    f"{fila[7]} {fila[8]}"
                    if fila[7] and fila[8]
                    else None
                ),
            }

            for fila in filas
        ]


    def obtener_por_id(self, id_salida):

        cursor = self.conexion.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    sp.id_salida,
                    sp.id_paquete,
                    sp.fecha_salida,
                    sp.fecha_regreso,
                    sp.estado,
                    sp.id_guia,
                    sp.observaciones,
                    g.nombre,
                    g.apellido
                FROM salida_paquete sp
                LEFT JOIN guia_turistico g
                    ON g.id_guia = sp.id_guia
                WHERE sp.id_salida = %s
                """,
                (id_salida,)
            )

            fila = cursor.fetchone()

        finally:

            cursor.close()


        if not fila:
            return None


        return {
            "id_salida": fila[0],
            "id_paquete": fila[1],
            "fecha_salida": fila[2],
            "fecha_regreso": fila[3],
            "estado": fila[4],
            "id_guia": fila[5],
            "observaciones": fila[6],
            "guia_nombre": (
                f"{fila[7]} {fila[8]}"
                if fila[7] and fila[8]
                else None
            ),
        }