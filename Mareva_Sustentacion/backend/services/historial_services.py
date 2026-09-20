from repositories.historial_repositories import HistorialRepository

class HistorialServices:

    def __init__(self):
        self.repo = HistorialRepository()

    def guardar_filtros(self, destino_buscado, categoria, duracion, precio_max, incluye, id_cliente):

        filtros = {
            "categoria": categoria,
            "duracion": duracion,
            "precio_max": precio_max,
            "incluye": incluye,
            "id_cliente": id_cliente
        }

        return self.repo.guardar_filtros(
            destino_buscado,
            filtros,
            id_cliente
        )

    def listar_historial(self, id_cliente):

        filas = self.repo.listar_por_cliente(id_cliente)

        return [
            {
                "id_busqueda": fila[0],
                "destino_buscado": fila[1],
                "filtros": fila[2],
                "fecha_busqueda": fila[3]
            }
            for fila in filas
        ]

    def eliminar_historial(self, id_cliente):
        return self.repo.eliminar_por_cliente(id_cliente)

    def obtener_busqueda(self, id_busqueda, id_cliente):

        return self.repo.obtener_busqueda(
            id_busqueda,
            id_cliente
        )