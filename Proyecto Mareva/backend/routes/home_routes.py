from flask import Blueprint, render_template, redirect, session, url_for

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def home():
    print("Se accedio al inicio correcamente")
    return render_template("principal/index.html")

@home_bp.route("/perfil")
def perfil(): 
    if 'usuario' not in session:
        return redirect('home')
    return render_template("cliente/perfil.html")

@home_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))
