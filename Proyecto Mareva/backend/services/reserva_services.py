from repositories.reserva_repository import ReservaRepository
from services.encuesta_services import EncuestaService

class ReservaService:

    def __init__(self):
        self.repo = ReservaRepository()
        self.encuesta_service = EncuestaService()

    # Confirma una reserva y guarda los datos en la base de datos
    def confirmar_reserva(
            self, 
            id_cliente, 
            id_paquete, 
            cant_adultos, 
            cant_menores,
            fecha_viaje, 
            observaciones, 
            acepta_no_reembolso, 
            alergias, 
            mascotas, 
            plan,
            metodo_contacto, 
            extras_ids, 
            viajeros):
        
        resultado = self.repo.crear_reserva(
            id_cliente=id_cliente,
            id_paquete=id_paquete, 
            cant_adultos=cant_adultos, 
            cant_menores=cant_menores,
            fecha_viaje=fecha_viaje, 
            observaciones=observaciones, 
            acepta_no_reembolso=acepta_no_reembolso, 
            alergias=alergias, 
            mascotas=mascotas, 
            plan=plan, 
            metodo_contacto=metodo_contacto
        )

        if not resultado["ok"]:
            return resultado

        if extras_ids:
            self.repo.agregar_servicios_extra(
                resultado["id_reserva"], 
                extras_ids)

        if viajeros:
            self.repo.agregar_viajeros(
                resultado["id_reserva"], 
                viajeros)

        return resultado

    def actualizar_viajero(
        self,
        id_viajero,
        id_cliente,
        nombre,
        apellido,
        tipo_documento,
        numero_documento
    ):
        return self.repo.actualizar_viajero(
            id_viajero,
            id_cliente,
            nombre,
            apellido,
            tipo_documento,
            numero_documento
        )

    def obtener_viajeros_reserva(self, id_reserva):
        return self.repo.obtener_viajeros_reserva(id_reserva)

    def obtener_reserva_cliente(self, id_reserva, id_cliente):
        return self.repo.obtener_reserva_cliente(id_reserva, id_cliente)

    def obtener_reserva_con_viajeros(self, id_reserva, id_cliente):
        return self.repo.obtener_reserva_con_viajeros(
            id_reserva,
            id_cliente
        )

    def completar_reserva(self, id_reserva):

        reserva = self.repo.obtener_datos_encuesta(id_reserva)

        if not reserva:
            return {
                "ok": False,
                "error": "Reserva no encontrada."
            }

        if reserva["estado"] == "completada":
            return {
                "ok": False,
                "error": "La reserva ya está completada."
            }

        resultado = self.repo.marcar_completada(id_reserva)

        if not resultado["ok"]:
            return resultado

        envio = self.encuesta_service.enviar_encuesta(
            reserva["correo"],
            reserva["nombre"],
            id_reserva
        )

        if not envio["ok"]:
            print(
                "La reserva fue completada, "
                "pero no se pudo enviar la encuesta."
            )

        return {
            "ok": True,
            "encuesta_enviada": envio["ok"]
        }

    def listar_reservas_admin(self):
        return self.repo.listar_reservas_admin()

    # Obtiene la última reserva de un cliente por su ID
    def obtener_ultima_reserva(self, id_cliente):
        return self.repo.obtener_ultima_reserva_cliente(id_cliente)