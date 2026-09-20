import re
import unicodedata

from repositories.paquete_repository import PaqueteRepository
from models.paquete import factory_paquete
from repositories.salida_repository import SalidaRepository


class PaqueteService:

    def __init__(self):
        self.repo = PaqueteRepository()
        self.salida_repo = SalidaRepository()

    # ==========================================================
    # DISPONIBILIDAD
    # ==========================================================

    def obtener_disponibilidad(self, id_paquete):
        return self.repo.obtener_disponibilidad(id_paquete)

    # ==========================================================
    # CATÁLOGO
    # ==========================================================

    def listar_activos(self):
        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.obtener_todos(solo_activos=True)
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(
                p["id_paquete"]
            )

        return paquetes

    def listar_todos_admin(self):
        return [
            factory_paquete(p).to_dict()
            for p in self.repo.obtener_todos(solo_activos=False)
        ]

    # ==========================================================
    # DETALLE DEL PAQUETE
    # ==========================================================

    def obtener_detalle(self, slug):
        data = self.repo.obtener_por_slug(slug)

        if not data:
            return None

        paquete = factory_paquete(data).to_dict()

        paquete["servicios_extra"] = (
            self.repo.obtener_servicios_extra(
                data["id_paquete"]
            )
        )

        # Todas las salidas disponibles del paquete
        paquete["salidas"] = (
            self.salida_repo.obtener_por_paquete(
                data["id_paquete"],
                solo_disponibles=True
            )
        )

        # NUEVO: contenido tipo "incluye" para el detalle del paquete
        paquete["alojamientos"] = self.repo.obtener_alojamientos_paquete(
            data["id_paquete"]
        )
        paquete["alimentacion"] = self.repo.obtener_alimentacion_paquete(
            data["id_paquete"]
        )
        paquete["transportes"] = self.repo.obtener_transportes_paquete(
            data["id_paquete"]
        )
        paquete["actividades"] = self.repo.obtener_actividades_paquete(
            data["id_paquete"]
        )
        paquete["guia"] = self.repo.obtener_guia_paquete(
            data["id_paquete"]
        )
        paquete["seguros"] = self.repo.obtener_seguros_paquete(
            data["id_paquete"]
        )
        paquete["incluye"] = self.repo.obtener_incluye(
            data["id_paquete"]
        )

        return paquete

    # ==========================================================
    # ADMIN - FORMULARIOS
    # ==========================================================

    def obtener_para_editar(self, id_paquete):
        return self.repo.obtener_por_id(id_paquete)

    def datos_formulario(self):
        return {
            "destinos": self.repo.obtener_destinos(),
            "guias": self.repo.obtener_guias(),
        }

    # ==========================================================
    # FILTROS
    # ==========================================================

    def filtrar(
        self,
        termino,
        categoria,
        duracion,
        precio_max,
        incluye,
        destino=None,
        precio_min=None,
        fecha_desde=None,
        solo_disponibles=False,
        ordenar="recomendados"
    ):
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
                incluye,
                destino,
                precio_min,
                fecha_desde,
                solo_disponibles,
                ordenar
            )
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(
                p["id_paquete"]
            )

        return paquetes

    # ==========================================================
    # COMPARAR
    # ==========================================================

    def comparar(self, ids_paquetes):
        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.obtener_comparacion(ids_paquetes)
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(
                p["id_paquete"]
            )

            p["servicios_extra"] = (
                self.repo.obtener_servicios_extra(
                    p["id_paquete"]
                )
            )

        return paquetes

    # ==========================================================
    # PROMOCIONES
    # ==========================================================

    def promociones_activas(self, limite=8):
        return self.repo.obtener_promociones_activas(limite)

    # ==========================================================
    # PAQUETES POR DESTINO
    # ==========================================================

    def paquetes_por_destino(self, id_destino, limite=12):
        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.obtener_paquetes_destino(
                id_destino,
                limite
            )
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(
                p["id_paquete"]
            )

        return paquetes

    # ==========================================================
    # RESERVAS
    # ==========================================================

    def reservas_no_canceladas(self, id_paquete):
        return self.repo.contar_reservas_no_canceladas(
            id_paquete
        )

    # ==========================================================
    # SUSPENDER / ACTIVAR
    # ==========================================================

    def suspender_seguro(self, id_paquete):
        total = self.repo.contar_reservas_no_canceladas(
            id_paquete
        )

        if total:
            return {
                "ok": False,
                "reservas": total,
                "error": (
                    "No se puede suspender un paquete "
                    "con reservas activas."
                )
            }

        self.repo.cambiar_estado(
            id_paquete,
            "suspendido"
        )

        return {
            "ok": True,
            "reservas": 0
        }

    def cancelar_por_contingencia(self, id_paquete, motivo):
        motivo = (motivo or "").strip()

        if len(motivo) < 15:
            return {
                "ok": False,
                "error": (
                    "Debes indicar un motivo de contingencia "
                    "detallado (mínimo 15 caracteres)."
                )
            }

        afectadas = (
            self.repo.cancelar_reservas_por_contingencia(
                id_paquete,
                motivo
            )
        )

        return {
            "ok": True,
            "reservas_canceladas": afectadas
        }

    # ==========================================================
    # FAVORITOS
    # ==========================================================

    def obtener_favoritos_cliente(self, id_cliente):
        return self.repo.obtener_favoritos_cliente(
            id_cliente
        )

    def agregar_favorito(self, id_cliente, id_paquete):
        return self.repo.agregar_favorito(
            id_cliente,
            id_paquete
        )

    def quitar_favorito(self, id_cliente, id_paquete):
        return self.repo.quitar_favorito(
            id_cliente,
            id_paquete
        )

    # ==========================================================
    # PAQUETES POR IDS
    # ==========================================================

    def listar_por_ids(self, ids_paquetes):
        return [
            factory_paquete(paquete).to_dict()
            for paquete in self.repo.obtener_por_ids(
                ids_paquetes
            )
        ]

    # ==========================================================
    # BUSCAR
    # ==========================================================

    def buscar(self, termino):
        if not termino:
            return self.listar_activos()

        paquetes = [
            factory_paquete(p).to_dict()
            for p in self.repo.buscar(termino)
        ]

        for p in paquetes:
            p["incluye"] = self.repo.obtener_incluye(
                p["id_paquete"]
            )

        print("RESULTADO BUSQUEDA 3:", termino)

        return paquetes

    # ==========================================================
    # CRUD ADMINISTRADOR
    # ==========================================================

    def crear_paquete(self, datos):
        datos["slug"] = self._generar_slug(
            datos["nombre"]
        )

        return self.repo.crear(datos)

    def actualizar_paquete(self, id_paquete, datos):
        return self.repo.actualizar(
            id_paquete,
            datos
        )

    def suspender(self, id_paquete):
        return self.repo.cambiar_estado(
            id_paquete,
            "suspendido"
        )

    def activar(self, id_paquete):
        return self.repo.cambiar_estado(
            id_paquete,
            "activo"
        )

    # ==========================================================
    # SLUG
    # ==========================================================

    @staticmethod
    def _generar_slug(nombre):
        texto = unicodedata.normalize(
            "NFKD",
            nombre
        ).encode(
            "ascii",
            "ignore"
        ).decode()

        texto = texto.lower().strip()

        return re.sub(
            r"[^a-z0-9]+",
            "-",
            texto
        ).strip("-")

    def obtener_paquetes_para_comparar(self, ids):
        if not ids:
            return []
        return self.repo.obtener_paquetes_para_comparar(ids)