from flask import Blueprint, render_template
from controllers.auth_controllers import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/registro", methods=["POST"])
def funcion_registro():
    print("Se accedio al registro correcamente")
    return AuthController.registrar_usuario()

@auth_bp.route("/registro", methods=["GET"])
def mostrar_registro():
    print("Se accedio al registro correcamente")
    return render_template("principal/registro.html")

@auth_bp.route("/login", methods=["GET"])
def mostrar_login():
    print("Se accedio al login correcamente")
    return render_template("principal/login.html")

@auth_bp.route("/login", methods=["POST"])
def funcion_login():
    print("Se accedio al login correcamente")
    return AuthController.iniciar_sesion()


