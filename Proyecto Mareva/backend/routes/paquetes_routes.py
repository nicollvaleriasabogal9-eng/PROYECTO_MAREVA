from flask import Blueprint, render_template

paquetes_bp = Blueprint('paquetes', __name__)

@paquetes_bp.route("/paquetes")
def paquetes():
    print("Se accedio al inicio correcamente")
    return render_template("cliente/paquetes.html")