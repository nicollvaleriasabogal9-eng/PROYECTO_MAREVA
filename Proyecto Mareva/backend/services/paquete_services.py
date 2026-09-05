import re
import unicodedata
from repositories.paquete_repository import PaqueteRepository
from models.paquete import factory_paquete

class PaqueteService:

    def __init__(self):
        self.repo = PaqueteRepository()

    # Obtiene la disponibilidad de un paquete por su ID
    def obtener_disponibilidad(self, id_paquete):
        return self.repo.obtener_disponibilidad(id_paquete)
    
    # Listar paquetes activos para el catálogo
    def listar_activos(self):
        paquetes = [factory_paquete(p).to_dict() for p in self.repo.obtener_todos(solo_activos=True)]
        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(p["id_paquete"])
        return paquetes
    
    # Listar todos los paquetes, incluyendo los suspendidos, para administración
    def listar_todos_admin(self):
        return [factory_paquete(p).to_dict() for p in self.repo.obtener_todos(solo_activos=False)]
    
    # Obtener el detalle de un paquete por su slug
    def obtener_detalle(self, slug):
        data = self.repo.obtener_por_slug(slug)
        if not data:
            return None
        paquete = factory_paquete(data).to_dict()
        paquete["servicios_extra"] = self.repo.obtener_servicios_extra(data["id_paquete"])
        return paquete
    
    # Obtener los datos de un paquete para edición
    def obtener_para_editar(self, id_paquete):
        data = self.repo.obtener_por_id(id_paquete)
        return data
    
    # Obtener los datos necesarios para el formulario de creación/edición de paquetes
    def datos_formulario(self):
        return {
            "destinos": self.repo.obtener_destinos(),
            "guias": self.repo.obtener_guias(),
        }

    def filtrar(self, termino, categoria, duracion, precio_max, incluye):

        if precio_max:
            precio_max = int(precio_max)
            if precio_max >= 5000000:
                precio_max = None

        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.filtrar(
                termino,
                categoria,
                duracion,
                precio_max,
                incluye
            )
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(p["id_paquete"])

        return paquetes

    def listar_por_ids(self, ids_paquetes):
        return [
            factory_paquete(paquete).to_dict()
            for paquete in self.repo.obtener_por_ids(ids_paquetes)
        ]

    def buscar(self, termino):

        if not termino:
            return self.listar_activos()

        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.buscar(termino)
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(p["id_paquete"])
        print("RESULTADO BUSQUEDA 3:", termino)
        return paquetes
    
# <------- CRUD ADMINISTRADOR -------->
    def crear_paquete(self, datos):
        datos["slug"] = self._generar_slug(datos["nombre"])
        return self.repo.crear(datos)

    def actualizar_paquete(self, id_paquete, datos):
        return self.repo.actualizar(id_paquete, datos)

    def suspender(self, id_paquete):
        return self.repo.cambiar_estado(id_paquete, "suspendido")

    def activar(self, id_paquete):
        return self.repo.cambiar_estado(id_paquete, "activo")
    # genera un slug a partir del nombre del paquete, eliminando acentos y caracteres especiales
    @staticmethod
    def _generar_slug(nombre):
        texto = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
        texto = texto.lower().strip()
        return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    
