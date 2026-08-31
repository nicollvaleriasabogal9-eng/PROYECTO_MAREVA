from config.conexion import Conexion
from psycopg.types.json import Json

class HistorialRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def guardar_filtros(self, destino_buscado, filtros, id_cliente):

        cursor = self.conexion.cursor()

        cursor.execute("""
            INSERT INTO historial_busqueda
            (
                destino_buscado,
                filtros,
                id_cliente
            )
            VALUES (%s, %s, %s)
            RETURNING id_busqueda
        """, (
            destino_buscado,
            Json(filtros),
            id_cliente
        ))

        id_busqueda = cursor.fetchone()[0]

        self.conexion.commit()
        cursor.close()

        return id_busqueda

    def listar_por_cliente(self, id_cliente):

        query = """
            SELECT
                id_busqueda,
                destino_buscado,
                filtros,
                fecha_busqueda
            FROM historial_busqueda
            WHERE id_cliente = %s
            ORDER BY fecha_busqueda DESC
        """

        cursor = self.conexion.cursor()
        cursor.execute(query, (id_cliente,))

        filas = cursor.fetchall()

        cursor.close()

        return filas

    def eliminar_por_cliente(self, id_cliente):

        query = """
            DELETE FROM historial_busqueda
            WHERE id_cliente = %s
        """

        cursor = self.conexion.cursor()

        cursor.execute(query, (id_cliente,))

        self.conexion.commit()

        cursor.close()

    def obtener_busqueda(self, id_busqueda, id_cliente):

        query = """
            SELECT
                id_busqueda,
                destino_buscado,
                filtros,
                fecha_busqueda
            FROM historial_busqueda
            WHERE id_busqueda = %s
            AND id_cliente = %s
        """

        cursor = self.conexion.cursor()

        cursor.execute(
            query,
            (id_busqueda, id_cliente)
        )

        fila = cursor.fetchone()

        cursor.close()

        if not fila:
            return None

        return {
            "id_busqueda": fila[0],
            "destino_buscado": fila[1],
            "filtros": fila[2],
            "fecha_busqueda": fila[3]
        }