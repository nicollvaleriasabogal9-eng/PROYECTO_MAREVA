from decimal import Decimal

from repositories.gamificacion_repository import GamificacionRepository


class GamificacionService:

    def __init__(self):
        self.repository = GamificacionRepository()

    def sincronizar_cliente(self, id_cliente):
        estadisticas = self.repository.obtener_estadisticas_cliente(id_cliente)
        niveles = self.repository.obtener_niveles()
        nivel_anterior = self.repository.obtener_nivel_cliente(id_cliente)

        niveles_cumplidos = [
            nivel for nivel in niveles
            if estadisticas["monto_total"] >= nivel["min_monto"]
            and estadisticas["reservas_validas"] >= nivel["min_reservas"]
        ]
        nivel_calculado = niveles_cumplidos[-1] if niveles_cumplidos else None

        if nivel_calculado and (
            not nivel_anterior
            or nivel_anterior["id_nivel"] != nivel_calculado["id_nivel"]
        ):
            self.repository.actualizar_nivel_cliente(
                id_cliente, nivel_calculado["id_nivel"]
            )
            if nivel_anterior and self._es_nivel_superior(
                nivel_calculado, nivel_anterior, niveles
            ):
                self.repository.crear_notificacion(
                    id_cliente,
                    "subida_nivel",
                    (
                        f"¡Subiste al nivel {nivel_calculado['nombre']}! "
                        f"Tus próximas reservas tendrán "
                        f"{nivel_calculado['porcentaje_descuento']}% de descuento."
                    ),
                )

        return estadisticas

    @staticmethod
    def _es_nivel_superior(nuevo, anterior, niveles):
        posiciones = {nivel["id_nivel"]: i for i, nivel in enumerate(niveles)}
        return posiciones.get(nuevo["id_nivel"], -1) > posiciones.get(
            anterior["id_nivel"], -1
        )

    def obtener_beneficio_reserva(self, id_cliente):
        """Devuelve el nivel vigente antes de crear una nueva reserva."""
        self.sincronizar_cliente(id_cliente)
        nivel = self.repository.obtener_nivel_cliente(id_cliente)
        return {
            "nivel": nivel["nombre"] if nivel else "Explorador",
            "porcentaje_descuento": (
                Decimal(str(nivel["porcentaje_descuento"]))
                if nivel else Decimal("0")
            ),
        }

    def obtener_panel_niveles(self, id_cliente):
        estadisticas = self.sincronizar_cliente(id_cliente)
        niveles = self.repository.obtener_niveles()
        nivel_actual = self.repository.obtener_nivel_cliente(id_cliente)
        indice_actual = next(
            (
                indice for indice, nivel in enumerate(niveles)
                if nivel_actual and nivel["id_nivel"] == nivel_actual["id_nivel"]
            ),
            -1,
        )
        siguiente_nivel = (
            niveles[indice_actual + 1]
            if indice_actual + 1 < len(niveles)
            else None
        )

        for indice, nivel in enumerate(niveles):
            nivel["actual"] = indice == indice_actual
            nivel["alcanzado"] = indice <= indice_actual

        return {
            "nivel_actual": nivel_actual,
            "siguiente_nivel": siguiente_nivel,
            "niveles": niveles,
            "estadisticas": estadisticas,
            "progreso": self._calcular_progreso_nivel(
                estadisticas, siguiente_nivel
            ),
            "notificaciones": self.repository.obtener_notificaciones_recientes(
                id_cliente
            ),
        }

    @staticmethod
    def _calcular_progreso_nivel(estadisticas, siguiente_nivel):
        if not siguiente_nivel:
            return {
                "general": 100,
                "monto": 100,
                "reservas": 100,
                "faltan_monto": Decimal("0"),
                "faltan_reservas": 0,
            }

        meta_monto = siguiente_nivel["min_monto"] or 0
        meta_reservas = siguiente_nivel["min_reservas"] or 0
        porcentaje_monto = 100 if meta_monto == 0 else min(
            100, float(estadisticas["monto_total"] / meta_monto * 100)
        )
        porcentaje_reservas = 100 if meta_reservas == 0 else min(
            100, estadisticas["reservas_validas"] / meta_reservas * 100
        )
        return {
            "general": round(min(porcentaje_monto, porcentaje_reservas), 1),
            "monto": round(porcentaje_monto, 1),
            "reservas": round(porcentaje_reservas, 1),
            "faltan_monto": max(
                Decimal("0"), meta_monto - estadisticas["monto_total"]
            ),
            "faltan_reservas": max(
                0, meta_reservas - estadisticas["reservas_validas"]
            ),
        }

    def obtener_datos_perfil(self, id_cliente):
        self.sincronizar_cliente(id_cliente)
        return {
            "nivel_actual": self.repository.obtener_nivel_cliente(id_cliente),
            "notificaciones": self.repository.obtener_notificaciones_recientes(
                id_cliente
            ),
        }

    def obtener_admin_niveles(self):
        return self.repository.obtener_niveles()

    def guardar_nivel(self, datos, id_nivel=None):
        datos = self._validar_nivel(datos)
        if id_nivel:
            return self.repository.actualizar_nivel(id_nivel, datos)
        return self.repository.crear_nivel(datos)

    @staticmethod
    def _validar_nivel(datos):
        nombre = (datos.get("nombre") or "").strip()
        if not nombre:
            raise ValueError("El nombre del nivel es obligatorio.")

        try:
            min_monto = Decimal(str(datos.get("min_monto", "0")))
            min_reservas = int(datos.get("min_reservas", 0))
            descuento = Decimal(str(datos.get("porcentaje_descuento", "0")))
        except (ValueError, TypeError):
            raise ValueError("Los umbrales y el descuento deben ser numéricos.")

        if min_monto < 0 or min_reservas < 0:
            raise ValueError("Los umbrales no pueden ser negativos.")
        if descuento < 0 or descuento > 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")

        return {
            "nombre": nombre,
            "min_monto": min_monto,
            "min_reservas": min_reservas,
            "descripcion": (datos.get("descripcion") or "").strip(),
            "porcentaje_descuento": descuento,
        }
