from flask import Blueprint, render_template
from controllers.auth_controllers import AuthController

auth_bp = Blueprint('auth', __name__)

controller = AuthController()

#Muestra el formulario de registro
@auth_bp.route("/registro", methods=["GET"])
def mostrar_registro():
    print("Se accedio al GET del registro correcamente")
    return render_template("principal/registro.html")

#Maneja el registro de un nuevo usuario
@auth_bp.route("/registro", methods=["POST"])
def funcion_registro():
    print("Se accedio al POST del registro correctamente")
    return controller.registrar_usuario()

#Muestra el formulario de login
@auth_bp.route("/login", methods=["GET"])
def mostrar_login():
    print("Se accedio al GET del login correctamente")
    return render_template("principal/login.html")

#Maneja el inicio de sesión de un usuario
@auth_bp.route("/login", methods=["POST"])
def funcion_login():
    print("Se accedio al POST del login correctamente")
    return controller.iniciar_sesion()


