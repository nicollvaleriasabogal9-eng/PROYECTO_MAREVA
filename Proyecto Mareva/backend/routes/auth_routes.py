from flask import Blueprint
from controllers.auth_controllers import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    return AuthController.registrar_usuario()

@auth_bp.route("/login", methods=["POST"])
def registro():
    return AuthController.registrar_usuario()


