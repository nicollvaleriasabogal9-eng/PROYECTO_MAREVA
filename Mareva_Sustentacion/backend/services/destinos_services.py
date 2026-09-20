from repositories.destino_repositories import DestinoRepository
from models.paquete import EMOJI_POR_CATEGORIA
from repositories.paquete_repository import PaqueteRepository


def _con_emoji(destino):
    if destino:
        destino["emoji"] = EMOJI_POR_CATEGORIA.get((destino.get("categoria") or "").lower(), "🗺️")
    return destino


class DestinoService:

    def __init__(self):
        self.repo = DestinoRepository()
        self.paquete_repo = PaqueteRepository()

    # Obtiene los destinos disponibles para mostrarlos al usuario.
    def listar_activos(self):
        return [_con_emoji(d) for d in self.repo.obtener_todos(solo_activos=True)]

    # Obtiene todos los destinos, incluyendo los inactivos.
    # Útil para la administración.
    def listar_todos(self):
        return [_con_emoji(d) for d in self.repo.obtener_todos(solo_activos=False)]

    # Obtiene la información de un destino específico.
    def obtener_detalle(self, id_destino):
        return _con_emoji(self.repo.obtener_por_id(id_destino))

    def paquetes_por_destino(self, id_destino):
        paquetes = self.paquete_repo.obtener_paquetes_destino(id_destino)
        for p in paquetes:
            p["emoji"] = EMOJI_POR_CATEGORIA.get((p.get("categoria") or "").lower(), "🧳")
        return paquetes

    # ---- Soporte para el panel de administración ----

    def crear_destino(self, datos):
        return self.repo.crear(datos)

    def actualizar_destino(self, id_destino, datos):
        return self.repo.actualizar(id_destino, datos)

    def cambiar_estado(self, id_destino, estado: bool):
        return self.repo.cambiar_estado(id_destino, estado)
