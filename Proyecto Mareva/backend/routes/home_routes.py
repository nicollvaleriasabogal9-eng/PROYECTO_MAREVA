from flask import Blueprint, render_template, redirect, session, url_for
from controllers.home_controllers import  HomeController

home_bp = Blueprint('home', __name__)

controller = HomeController()
#Muestra la página de inicio
@home_bp.route("/")
def home():
    print("Se accedio al inicio correcamente")
    return render_template("principal/index.html")

#Muestra la página de perfil para clientes
@home_bp.route("/perfil")
def perfil(): 
    if 'usuario' not in session:
        return redirect(url_for('home.home'))
    return controller.perfil()
    

@home_bp.route("/perfil/historial/eliminar", methods=["POST"])
def eliminar_historial():
    return controller.eliminar_historial()

@home_bp.route("/perfil/historial/aplicar/<int:id_busqueda>")
def aplicar_filtros(id_busqueda):
    return controller.aplicar_filtros(id_busqueda)

#Cierra la sesion del usuario y redirige a la página de inicio
@home_bp.route('/logout')
def logout():
    session.pop("usuario", None)
    return render_template("principal/login.html")
