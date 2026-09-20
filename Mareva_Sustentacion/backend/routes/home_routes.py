from flask import Blueprint, render_template, redirect, session, url_for
from controllers.home_controllers import  HomeController
from controllers.reserva_controllers import ReservaController

home_bp = Blueprint('home', __name__)

controller = HomeController()
reserva_controller = ReservaController()
#Muestra la página de inicio
@home_bp.route("/")
def home():
    return controller.inicio()

    
@home_bp.route("/perfil")
def perfil():

    if "usuario" not in session:
        return redirect(
            url_for("auth.mostrar_login")
        )

    usuario = session["usuario"]

    id_cliente = (
        usuario.get("id")
        or usuario.get("id_cliente")
    )

    reservas = []

    if id_cliente:
        reservas = reserva_controller.service.listar_reservas_cliente(
            id_cliente
        )

    return render_template(
        "cliente/perfil.html",
        usuario=usuario,
        reservas=reservas
    )

@home_bp.route("/perfil/correo", methods=["POST"])
def actualizar_correo():
    return controller.actualizar_correo()

@home_bp.route("/perfil/password", methods=["POST"])
def cambiar_password():
    return controller.cambiar_password()

@home_bp.route("/perfil/historial/eliminar", methods=["POST"])
def eliminar_historial():
    return controller.eliminar_historial()

@home_bp.route("/perfil/historial/aplicar/<int:id_busqueda>")
def aplicar_filtros(id_busqueda):
    return controller.aplicar_filtros(id_busqueda)

#Cierra la sesion del usuario y redirige a la página de inicio
@home_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("auth.mostrar_login"))
