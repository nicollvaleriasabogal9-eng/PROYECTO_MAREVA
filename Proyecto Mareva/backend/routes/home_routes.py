from flask import Blueprint, render_template, redirect, session, url_for

home_bp = Blueprint('home', __name__)

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
    return render_template("cliente/perfil.html")

#Cierra la sesion del usuario y redirige a la página de inicio
@home_bp.route('/logout')
def logout():
    session.pop("usuario", None)
    return render_template("principal/login.html")
