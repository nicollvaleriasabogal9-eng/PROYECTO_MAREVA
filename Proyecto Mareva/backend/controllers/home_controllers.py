from flask import render_template, redirect, url_for, session, request

from services.historial_services import HistorialServices
from services.reserva_services import ReservaService
from services.destinos_services import DestinoService
from services.paquete_services import PaqueteService
from services.auth_services import AuthServices
from services.gamificacion_services import GamificacionService
import re

class HomeController:

    def __init__(self):
        self.historial_services = HistorialServices()
        self.reserva_service = ReservaService()
        self.destino_service = DestinoService()
        self.paquete_service = PaqueteService()
        self.auth_service = AuthServices()
        self.gamificacion_service = GamificacionService()

    def inicio(self):
        destacados = self.paquete_service.listar_activos()
        destinos = self.destino_service.listar_activos()
        promociones = self.paquete_service.promociones_activas()

        return render_template(
            "principal/index.html",
            destacados=destacados,
            destinos=destinos,
            promociones=promociones,
            categorias=[
                "playa",
                "montaña",
                "aventura",
                "ecoturismo",
                "cultural",
                "ciudad"
            ]
        )

    def perfil(self):
        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("home.home"))

        id_cliente = usuario["id"]

        ultima_reserva = self.reserva_service.obtener_ultima_reserva(id_cliente)
        historial = self.historial_services.listar_historial(id_cliente)
        datos_nivel = self.gamificacion_service.obtener_datos_perfil(id_cliente)

        return render_template(
            "cliente/perfil.html",
            usuario=usuario,
            historial=historial,
            ultima_reserva=ultima_reserva,
            nivel_actual=datos_nivel.get("nivel_actual"),
            notificaciones=datos_nivel.get("notificaciones", [])
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
def actualizar_correo(self):
        usuario = session.get("usuario")
        if not usuario or usuario.get("rol") != "cliente":
            return redirect(url_for("auth.mostrar_login"))
        correo = request.form.get("correo", "").strip().lower()
        patron = r"^[a-zA-Z0-9._%+-]+@(gmail|outlook|hotmail|live|yahoo)\.(com|es|co)$"
        if not re.fullmatch(patron, correo):
            from flask import flash
            flash("El correo debe ser Gmail, Outlook, Hotmail/Live o Yahoo y usar una extensión .com, .es o .co.", "error")
            return redirect(url_for("home.perfil"))
        resultado = self.auth_service.actualizar_correo(usuario["id"], correo)
        from flask import flash
        if resultado["ok"]:
            session["usuario"]["correo"] = correo
            session.modified = True
            flash("Correo actualizado correctamente.", "success")
        else:
            flash(resultado.get("error", "No fue posible actualizar el correo."), "error")
        return redirect(url_for("home.perfil"))

def cambiar_password(self):
        usuario = session.get("usuario")
        if not usuario or usuario.get("rol") != "cliente":
            return redirect(url_for("auth.mostrar_login"))
        actual = request.form.get("password_actual", "")
        nueva = request.form.get("password_nueva", "")
        confirmar = request.form.get("password_confirmacion", "")
        from flask import flash
        if nueva != confirmar:
            flash("Las nuevas contraseñas no coinciden.", "error")
            return redirect(url_for("home.perfil"))
        resultado = self.auth_service.cambiar_password(usuario["id"], actual, nueva)
        flash("Contraseña actualizada correctamente." if resultado["ok"] else resultado["error"], "success" if resultado["ok"] else "error")
        return redirect(url_for("home.perfil"))

