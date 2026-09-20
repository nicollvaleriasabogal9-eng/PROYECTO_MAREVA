from functools import wraps
from flask import Blueprint, session, redirect, url_for
from controllers.destinos_controllers import DestinoController

destinos_bp = Blueprint("destinos", __name__)
controller = DestinoController()


# Decorador para verificar si el usuario es admin
def requiere_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        return f(*args, **kwargs)

    return wrapper


@destinos_bp.route("/destinos")
def listar_catalogo():
    return controller.listar()


@destinos_bp.route("/destinos/<int:id_destino>")
def ver_detalle(id_destino):
    return controller.detalle(id_destino)


@destinos_bp.route("/admin/destinos")
@requiere_admin
def panel_admin():
    return controller.panel_admin()


@destinos_bp.route("/admin/destinos/nuevo", methods=["GET"])
@requiere_admin
def mostrar_form_crear():
    return controller.mostrar_form_crear()


@destinos_bp.route("/admin/destinos/<int:id_destino>/editar", methods=["GET"])
@requiere_admin
def mostrar_form_editar(id_destino):
    return controller.mostrar_form_editar(id_destino)


@destinos_bp.route("/admin/destinos/nuevo", methods=["POST"])
@requiere_admin
def crear():
    return controller.crear()


@destinos_bp.route("/admin/destinos/<int:id_destino>/editar", methods=["POST"])
@requiere_admin
def actualizar(id_destino):
    return controller.actualizar(id_destino)

@destinos_bp.route(
    "/admin/destinos/<int:id_destino>/suspender",
    methods=["POST"]
)
@requiere_admin
def suspender(id_destino):
    return controller.suspender(id_destino)


@destinos_bp.route("/admin/destinos/<int:id_destino>/activar", methods=["POST"])
@requiere_admin
def activar(id_destino):
    return controller.activar(id_destino)