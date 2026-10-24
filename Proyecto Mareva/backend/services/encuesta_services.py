from repositories.encuesta_repository import EncuestaRepository
from repositories.reserva_repository import ReservaRepository

class EncuestaService:

    def __init__(self):
        self.encuesta_repo = EncuestaRepository()
        self.reserva_repo = ReservaRepository()

    def enviar_encuesta(self, correo_cliente, nombre_cliente, id_reserva):
        print(f"[SKIP EMAIL] Encuesta pendiente para {correo_cliente} (reserva {id_reserva})")
        return {"ok": True}

    def obtener_encuesta(self, id_reserva, id_cliente):

        reserva = self.encuesta_repo.verificar_reserva_cliente(
            id_reserva,
            id_cliente
        )

        if not reserva:
            return {
                "ok": False,
                "error": "La reserva no existe o no pertenece al usuario."
            }

        if reserva["estado"] != "completada":
            return {
                "ok": False,
                "error": "La encuesta estará disponible cuando el viaje haya sido completado."
            }

        preguntas = self.encuesta_repo.obtener_preguntas_activas()

        if not preguntas:
            return {
                "ok": False,
                "error": "Actualmente no hay preguntas disponibles para la encuesta."
            }

        return {
            "ok": True,
            "reserva": reserva,
            "preguntas": preguntas
        }

    def guardar_encuesta(
        self,
        id_cliente,
        id_reserva,
        respuestas
    ):

        if not id_cliente or not id_reserva:
            return {
                "ok": False,
                "error": "No se pudo identificar al cliente o la reserva."
            }

        if not respuestas:
            return {
                "ok": False,
                "error": "Debes responder todas las preguntas."
            }

        reserva = self.encuesta_repo.verificar_reserva_cliente(
            id_reserva=id_reserva,
            id_cliente=id_cliente
        )

        if not reserva:
            return {
                "ok": False,
                "error": "La reserva no existe o no te pertenece."
            }

        preguntas = self.encuesta_repo.obtener_todas_preguntas()

        if not preguntas:
            return {
                "ok": False,
                "error": "No hay preguntas disponibles."
            }

        preguntas_dict = {
            pregunta["id_pregunta"]: pregunta
            for pregunta in preguntas
        }

        respuestas_dict = {}

        for respuesta in respuestas:
            id_pregunta = respuesta["id_pregunta"]

            # No aceptar preguntas inexistentes ni duplicadas.
            if id_pregunta not in preguntas_dict:
                return {
                    "ok": False,
                    "error": "Se recibió una pregunta no válida."
                }

            if id_pregunta in respuestas_dict:
                return {
                    "ok": False,
                    "error": "Se recibió una respuesta duplicada."
                }

            respuestas_dict[id_pregunta] = respuesta["valor"]

        # Exigir una respuesta para cada pregunta mostrada.
        ids_preguntas = set(preguntas_dict.keys())

        if set(respuestas_dict.keys()) != ids_preguntas:
            return {
                "ok": False,
                "error": "Debes responder todas las preguntas."
            }

        respuestas_procesadas = []

        for id_pregunta, valor in respuestas_dict.items():

            pregunta = preguntas_dict[id_pregunta]

            tipo = (
                pregunta.get("tipo_respuesta") or ""
            ).strip().lower()

            valor = str(valor).strip()

            if not valor:
                return {
                    "ok": False,
                    "error": "Las respuestas no pueden estar vacías."
                }

            if tipo in (
                "numero",
                "rating",
                "calificacion"
            ):
                try:
                    numero = int(valor)

                except (ValueError, TypeError):
                    return {
                        "ok": False,
                        "error": (
                            f"La pregunta {id_pregunta} "
                            "requiere una calificación numérica."
                        )
                    }

                # El HTML presenta opciones del 1 al 5.
                if numero < 1 or numero > 5:
                    return {
                        "ok": False,
                        "error": "Las calificaciones deben estar entre 1 y 5."
                    }

                respuestas_procesadas.append({
                    "id_pregunta": id_pregunta,
                    "respuesta_texto": None,
                    "respuesta_numero": numero
                })

            else:
                respuestas_procesadas.append({
                    "id_pregunta": id_pregunta,
                    "respuesta_texto": valor,
                    "respuesta_numero": None
                })

        guardado = self.encuesta_repo.guardar_respuestas(
            id_cliente=id_cliente,
            id_reserva=id_reserva,
            respuestas=respuestas_procesadas
        )

        if not guardado:
            return {
                "ok": False,
                "error": (
                    "No fue posible guardar la encuesta. "
                    "Verifica si ya fue respondida e inténtalo nuevamente."
                )
            }

        return {
            "ok": True,
            "mensaje": "Encuesta guardada correctamente."
        }

    def obtener_preguntas_admin(self):
        return self.encuesta_repo.obtener_todas_preguntas()


    def obtener_pregunta(self, id_pregunta):
        return self.encuesta_repo.obtener_pregunta(id_pregunta)


    def crear_pregunta(self, texto, tipo_respuesta, orden):

        texto = texto.strip()

        if not texto:
            return {
                "ok": False,
                "error": "El texto de la pregunta es obligatorio."
            }

        if tipo_respuesta not in ("numero", "texto", "opcion"):
            return {
                "ok": False,
                "error": "El tipo de respuesta no es válido."
            }

        if orden < 1:
            return {
                "ok": False,
                "error": "El orden debe ser mayor a 0."
            }

        return self.encuesta_repo.crear_pregunta(
            texto,
            tipo_respuesta,
            orden
        )


    def actualizar_pregunta(
        self,
        id_pregunta,
        texto,
        tipo_respuesta,
        orden
    ):

        texto = texto.strip()

        if not texto:
            return {
                "ok": False,
                "error": "El texto de la pregunta es obligatorio."
            }

        if tipo_respuesta not in ("numero", "texto", "opcion"):
            return {
                "ok": False,
                "error": "El tipo de respuesta no es válido."
            }

        if orden < 1:
            return {
                "ok": False,
                "error": "El orden debe ser mayor a 0."
            }

        return self.encuesta_repo.actualizar_pregunta(
            id_pregunta,
            texto,
            tipo_respuesta,
            orden
        )


    def cambiar_estado_pregunta(self, id_pregunta):
        return self.encuesta_repo.cambiar_estado_pregunta(id_pregunta)

    def obtener_datos_reporte(self):
        return {
            "paquetes": self.encuesta_repo.obtener_paquetes_reporte(),
            "destinos": self.encuesta_repo.obtener_destinos_reporte()
        }

    def obtener_reporte(
        self,
        id_paquete=None,
        id_destino=None,
        fecha_inicio=None,
        fecha_fin=None
    ):
        return self.encuesta_repo.obtener_reporte_encuestas(
            id_paquete=id_paquete,
            id_destino=id_destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )