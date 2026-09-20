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


@proveedor_bp.route("/contratos", methods=["GET"])
def contratos():
    return controller.listar_contratos()

@proveedor_bp.route("/contratos/<int:id_contrato>", methods=["GET"])
def detalle_contrato(id_contrato):
    return controller.detalle_contrato(id_contrato)

@proveedor_bp.route(
"/contratos/<int:id_contrato>/responder",
methods=["POST"]
)
def responder_contrato(id_contrato):
    return controller.responder_contrato(id_contrato)


@proveedor_bp.route(
"/contratos/<int:id_contrato>/firmar",
methods=["POST"]
)
def firmar_contrato(id_contrato):
    return controller.firmar_contrato(id_contrato)
