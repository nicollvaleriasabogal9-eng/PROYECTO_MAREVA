from flask import redirect, url_for, render_template
from services.destinos_services import DestinoService


class DestinoController:

    def __init__(self):
        self.service = DestinoService()

    # Muestra todos los destinos disponibles.
    def listar(self):
        destinos = self.service.listar_activos()
        return render_template("cliente/destinos.html", destinos=destinos)

    # Muestra la información de un destino específico.
    def detalle(self, id_destino):
        destino = self.service.obtener_detalle(id_destino)

        if not destino:
            return redirect(url_for("destino.listar"))

        return render_template("cliente/destino_detalle.html", destino=destino)