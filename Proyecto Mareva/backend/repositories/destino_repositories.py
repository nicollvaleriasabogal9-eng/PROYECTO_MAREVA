from config.conexion import Conexion


COLUMNAS_DESTINO = [
    "id_destino", "nombre_destino", "departamento", "ciudad",
    "categoria", "descripcion", "atracciones", "docs_requeridos",
    "imagen_principal", "estado"
]


class DestinoRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    # Convierte la fila de la base de datos en un diccionario.
    def _fila_a_dict(self, fila):
        return dict(zip(COLUMNAS_DESTINO, fila))

    # Obtiene todos los destinos activos.
    def obtener_todos(self, solo_activos=True):
        cursor = self.conexion.cursor()

        query = """
            SELECT id_destino, nombre_destino, departamento, ciudad,
                   categoria, descripcion, atracciones, docs_requeridos,
                   imagen_principal, estado
            FROM destino
        """

        if solo_activos:
            query += " WHERE estado = TRUE"

        query += " ORDER BY nombre_destino"

        cursor.execute(query)
        filas = cursor.fetchall()
        cursor.close()

        return [self._fila_a_dict(fila) for fila in filas]

    # Obtiene un destino específico mediante su ID.
    def obtener_por_id(self, id_destino):
        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT id_destino, nombre_destino, departamento, ciudad,
                   categoria, descripcion, atracciones, docs_requeridos,
                   imagen_principal, estado
            FROM destino
            WHERE id_destino = %s
        """, (id_destino,))

        fila = cursor.fetchone()
        cursor.close()

        if fila is None:
            return None

        return self._fila_a_dict(fila)