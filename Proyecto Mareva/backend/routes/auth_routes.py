from flask import Blueprint, render_template, request
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
    print("DATOS RECIBIDOS:", request.form)
    return controller.registrar_usuario()

#Muestra el formulario de login
@auth_bp.route("/login", methods=["GET"])
def mostrar_login():
    print("Se accedio al GET del login correctamente")
    return render_template(
        "principal/login.html",
        next=request.args.get("next", "")
    )

#Maneja el inicio de sesión de un usuario
@auth_bp.route("/login", methods=["POST"])
def funcion_login():
    print("Se accedio al POST del login correctamente")
    return controller.iniciar_sesion()

@auth_bp.route("/auth/google", methods=["GET"])
def google_login():
    return controller.iniciar_sesion_google()


@auth_bp.route("/auth/google/callback", methods=["GET"])
def google_callback():
    return controller.google_callback()

@auth_bp.route("/auth/google/registro", methods=["GET"])
def google_registro():
    return controller.iniciar_sesion_google(intencion="registro")

