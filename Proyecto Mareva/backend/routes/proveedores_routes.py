
from flask import Blueprint

from controllers.proveedor_controllers import ProveedorController


proveedor_bp = Blueprint(
    "proveedor",
    __name__,
    url_prefix="/proveedores"
)

controller = ProveedorController()


@proveedor_bp.route("/registrar", methods=["GET"])
def mostrar_registro():
    return controller.mostrar_registro()


@proveedor_bp.route("/registrar", methods=["POST"])
def registrar_proveedor():
    return controller.registrar_proveedor()

