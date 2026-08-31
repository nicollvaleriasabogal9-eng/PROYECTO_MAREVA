from flask import render_template, redirect, url_for, session, request

from services.historial_services import HistorialServices
from services.reserva_services import ReservaService

class HomeController:

    def __init__(self):
        self.historial_services = HistorialServices()
        self.reserva_service = ReservaService()

    def perfil(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("home.home"))

        id_cliente = usuario["id"]
        ultima_reserva = self.reserva_service.obtener_ultima_reserva(id_cliente)

        historial = self.historial_services.listar_historial(id_cliente)

        return render_template(
            "cliente/perfil.html",
            historial=historial,
            ultima_reserva=ultima_reserva
        )


    def eliminar_historial(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("home.home"))

        id_cliente = usuario["id"]

        self.historial_services.eliminar_historial(id_cliente)

        return redirect(url_for("home.perfil"))

    def aplicar_filtros(self, id_busqueda):

        usuario = session.get("usuario")

        if not usuario:
          return redirect(url_for("home.home"))

        id_cliente = usuario["id"]

        busqueda = self.historial_services.obtener_busqueda(
           id_busqueda,
           id_cliente
        )

        if not busqueda:
            return redirect(url_for("home.perfil"))

        filtros = busqueda["filtros"]

        return redirect(
             url_for(
                "paquetes.listar_catalogo",
                categoria=filtros.get("categoria", ""),
                duracion=filtros.get("duracion", []),
                precio_max=filtros.get("precio_max", ""),
                incluye=filtros.get("incluye", []),
                historial=1
            )
        )