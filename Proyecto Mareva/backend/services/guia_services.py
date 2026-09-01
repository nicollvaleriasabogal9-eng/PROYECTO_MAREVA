from repositories.guia_repository import GuiaRepository

TRANSICIONES_RESERVA = {
        "solicitada": {"confirmada", "cancelada"},
        "confirmada": {"en_proceso", "cancelada"},
        "en_proceso": {"completada"},
        "completada": set(),
        "cancelada": set(),
    }

def transicion_valida(estado_actual, nuevo_estado):
        return nuevo_estado in TRANSICIONES_RESERVA.get(estado_actual, set())

class GuiaService:

    TRANSICIONES_RESERVA = TRANSICIONES_RESERVA

    def __init__(self):
        self.repository = GuiaRepository()

    def obtener_panel(self, id_guia, estado=None):
        estados_validos = set(self.TRANSICIONES_RESERVA)
        estado = estado if estado in estados_validos else None
        return {
            "perfil": self.repository.obtener_perfil(id_guia),
            "resumen": self.repository.obtener_resumen(id_guia),
            "paquetes": self.repository.obtener_paquetes(id_guia),
            "reservas": self.repository.obtener_reservas(id_guia, estado),
            "filtro_estado": estado or "todos",
            "transiciones": self.TRANSICIONES_RESERVA,
        }

    @classmethod
    def validar_transicion(cls, estado_actual, nuevo_estado):
        return transicion_valida(estado_actual, nuevo_estado)

    def cambiar_estado_reserva(self, id_guia, id_reserva, nuevo_estado):
        estado_actual = self.repository.obtener_estado_reserva(
            id_guia, id_reserva
        )
        if not estado_actual:
            return {"ok": False, "error": "La reserva no está asignada a este guía."}
        if not self.validar_transicion(estado_actual, nuevo_estado):
            return {
                "ok": False,
                "error": (
                    f"No se puede cambiar una reserva de {estado_actual} "
                    f"a {nuevo_estado}."
                ),
            }
        actualizado = self.repository.actualizar_estado_reserva(
            id_guia, id_reserva, nuevo_estado
        )
        return {"ok": actualizado, "error": None if actualizado else "No se actualizó la reserva."}
