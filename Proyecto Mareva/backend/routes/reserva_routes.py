from flask import Blueprint, session, redirect, url_for
from controllers.reserva_controllers import ReservaController

reserva_bp = Blueprint("reserva", __name__)
controller = ReservaController()

#Funciones para mostrar el formulario de reserva
@reserva_bp.route("/reserva/<slug>", methods=["GET"])
def mostrar_formulario(slug):
    if "usuario" not in session:
        return redirect(url_for("auth.mostrar_login", next=f"/reserva/{slug}"))
    return controller.mostrar_formulario(slug)

@reserva_bp.route(
    "/reserva/viajero/<int:id_viajero>/editar",
    methods=["POST"]
)
def guardar_cambios_viajero(id_viajero):
    return controller.guardar_cambios_viajero(id_viajero)

@reserva_bp.route(
    "/reserva/<int:id_reserva>/viajeros",
    methods=["GET"]
)
def modificar_viajeros(id_reserva):
    return controller.modificar_viajeros(id_reserva)

@reserva_bp.route(
    "/reservas/<int:id_reserva>/completar",
    methods=["POST"]
)
def completar_reserva(id_reserva):

    return controller.completar_reserva(id_reserva)

@reserva_bp.route("/admin/reservas")
def listar_reservas_admin():
    return controller.listar_reservas_admin()

#Funciones para manejar la disponibilidad de un paquete y confirmar la reserva
@reserva_bp.route("/api/paquetes/<int:id_paquete>/disponibilidad", methods=["GET"])
def disponibilidad(id_paquete):
    return controller.disponibilidad_json(id_paquete)

#Funciones para confirmar la reserva
@reserva_bp.route("/confirmar-reserva", methods=["POST"])
def confirmar():
    return controller.confirmar()