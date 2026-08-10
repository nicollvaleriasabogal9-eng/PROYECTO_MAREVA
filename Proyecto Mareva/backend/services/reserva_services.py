from repositories.reserva_repository import ReservaRepository


class ReservaService:

    def __init__(self):
        self.repo = ReservaRepository()
    # Confirma una reserva y guarda los datos en la base de datos
    def confirmar_reserva(self, id_cliente, id_paquete, cant_adultos, cant_menores,
                           fecha_viaje, observaciones, alergias, mascotas, plan,
                           metodo_contacto, extras_ids, viajeros):
        resultado = self.repo.crear_reserva(
            id_cliente, id_paquete, cant_adultos, cant_menores,
            fecha_viaje, observaciones, alergias, mascotas, plan, metodo_contacto
        )

        if not resultado["ok"]:
            return resultado

        if extras_ids:
            self.repo.agregar_servicios_extra(resultado["id_reserva"], extras_ids)

        if viajeros:
            self.repo.agregar_viajeros(resultado["id_reserva"], viajeros)

        return resultado
    # Obtiene la última reserva de un cliente por su ID
    def obtener_ultima_reserva(self, id_cliente):
        return self.repo.obtener_ultima_reserva_cliente(id_cliente)