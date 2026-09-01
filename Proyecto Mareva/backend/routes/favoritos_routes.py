from flask import Blueprint

from controllers.favoritos_controllers import FavoritosController


favoritos_bp = Blueprint("favoritos", __name__)
controller = FavoritosController()


@favoritos_bp.route("/favoritos", methods=["GET"])
def listar():
    return controller.listar()


@favoritos_bp.route("/favoritos/<int:id_paquete>/alternar", methods=["POST"])
def alternar(id_paquete):
    return controller.alternar(id_paquete)
