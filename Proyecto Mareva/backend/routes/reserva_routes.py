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

#Funciones para manejar la disponibilidad de un paquete y confirmar la reserva
@reserva_bp.route("/api/paquetes/<int:id_paquete>/disponibilidad", methods=["GET"])
def disponibilidad(id_paquete):
    return controller.disponibilidad_json(id_paquete)

#Funciones para confirmar la reserva
@reserva_bp.route("/confirmar-reserva", methods=["POST"])
def confirmar():
    return controller.confirmar()