from functools import wraps

from flask import Blueprint, redirect, request, session, url_for

from controllers.gamificacion_controllers import GamificacionController


gamificacion_bp = Blueprint("gamificacion", __name__)
controller = GamificacionController()


def requiere_cliente(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        usuario = session.get("usuario") or {}
        if usuario.get("rol") != "cliente":
            return redirect(url_for("auth.mostrar_login", next=request.path))
        return funcion(*args, **kwargs)
    return wrapper


def requiere_admin(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        usuario = session.get("usuario") or {}
        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))
        return funcion(*args, **kwargs)
    return wrapper


@gamificacion_bp.route("/niveles", methods=["GET"])
@requiere_cliente
def niveles():
    return controller.mostrar_niveles()


@gamificacion_bp.route("/admin/niveles", methods=["GET"])
@requiere_admin
def admin_niveles():
    return controller.panel_niveles()


@gamificacion_bp.route("/admin/niveles/nuevo", methods=["POST"])
@requiere_admin
def crear_nivel():
    return controller.crear_nivel()


@gamificacion_bp.route("/admin/niveles/<int:id_nivel>/editar", methods=["POST"])
@requiere_admin
def actualizar_nivel(id_nivel):
    return controller.actualizar_nivel(id_nivel)
