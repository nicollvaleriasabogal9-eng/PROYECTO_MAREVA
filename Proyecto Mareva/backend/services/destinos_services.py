from repositories.destino_repositories import DestinoRepository


class DestinoService:

    def __init__(self):
        self.repo = DestinoRepository()

    # Obtiene los destinos disponibles para mostrarlos al usuario.
    def listar_activos(self):
        return self.repo.obtener_todos(solo_activos=True)

    # Obtiene todos los destinos, incluyendo los inactivos.
    # Puede ser útil para la administración.
    def listar_todos(self):
        return self.repo.obtener_todos(solo_activos=False)

    # Obtiene la información de un destino específico.
    def obtener_detalle(self, id_destino):
        return self.repo.obtener_por_id(id_destino)