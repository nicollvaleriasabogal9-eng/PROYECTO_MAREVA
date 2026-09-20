from functools import wraps

from flask import Blueprint, redirect, session, url_for

from controllers.guia_controllers import GuiaController


guia_bp = Blueprint("guia", __name__, url_prefix="/guia")
controller = GuiaController()


def requiere_guia(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        usuario = session.get("usuario") or {}
        if usuario.get("rol") != "guia":
            return redirect(url_for("auth.mostrar_login"))
        return funcion(*args, **kwargs)
    return wrapper


@guia_bp.route("/panel", methods=["GET"])
@requiere_guia
def panel():
    return controller.mostrar_panel()


@guia_bp.route("/reservas/<int:id_reserva>/estado", methods=["POST"])
@requiere_guia
def actualizar_estado(id_reserva):
    return controller.actualizar_estado(id_reserva)
