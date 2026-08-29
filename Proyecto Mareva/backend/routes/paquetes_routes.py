from functools import wraps
from flask import Blueprint, session, redirect, url_for
from controllers.paquete_controllers import PaqueteController

paquetes_bp = Blueprint("paquetes", __name__)
controller = PaqueteController()

#Decorador para verificar si el usuario es admin
def requiere_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        usuario = session.get("usuario")
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))
        return f(*args, **kwargs)
    return wrapper

#Funciones para el catálogo de paquetes 
@paquetes_bp.route("/paquetes")
def listar_catalogo():
    return controller.listar_catalogo()

#Funciones para ver el detalle de un paquete
@paquetes_bp.route("/paquetes/<slug>")
def ver_detalle(slug):
    return controller.ver_detalle(slug)



#Funciones para el panel de administración de paquetes
@paquetes_bp.route("/admin/paquetes")
@requiere_admin
def panel_admin():
    return controller.panel_admin()

#Funciones para mostrar el formulario de creación de un nuevo paquete
@paquetes_bp.route("/admin/paquetes/nuevo", methods=["GET"])
@requiere_admin
def mostrar_form_crear():
    return controller.mostrar_form_crear()

#Funciones para mostrar el formulario de edición de un paquete existente
@paquetes_bp.route("/admin/paquetes/<int:id_paquete>/editar", methods=["GET"])
@requiere_admin
def mostrar_form_editar(id_paquete):
    return controller.mostrar_form_editar(id_paquete)

#Funciones para crear, editar, suspender y activar paquetes
@paquetes_bp.route("/admin/paquetes/nuevo", methods=["POST"])
@requiere_admin
def crear():
    return controller.crear()

@paquetes_bp.route("/admin/paquetes/<int:id_paquete>/editar", methods=["POST"])
@requiere_admin
def actualizar(id_paquete):
    return controller.actualizar(id_paquete)

@paquetes_bp.route("/admin/paquetes/<int:id_paquete>/suspender", methods=["POST"])
@requiere_admin
def suspender(id_paquete):
    return controller.suspender(id_paquete)

@paquetes_bp.route("/admin/paquetes/<int:id_paquete>/activar", methods=["POST"])
@requiere_admin
def activar(id_paquete):
    return controller.activar(id_paquete)