from flask import flash, redirect, render_template, request, session, url_for

from services.gamificacion_services import GamificacionService


class GamificacionController:

    def __init__(self):
        self.service = GamificacionService()

    @staticmethod
    def _id_cliente_sesion():
        usuario = session.get("usuario") or {}
        return usuario.get("id")

    def mostrar_niveles(self):
        datos = self.service.obtener_panel_niveles(self._id_cliente_sesion())
        return render_template("cliente/niveles.html", **datos)

    def mostrar_perfil(self):
        datos = self.service.obtener_datos_perfil(self._id_cliente_sesion())
        return render_template("cliente/perfil.html", **datos)

    def panel_niveles(self):
        return render_template(
            "admin/niveles.html",
            niveles=self.service.obtener_admin_niveles(),
        )

    def crear_nivel(self):
        try:
            self.service.guardar_nivel(request.form)
            flash("Nivel creado correctamente.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("gamificacion.admin_niveles"))

    def actualizar_nivel(self, id_nivel):
        try:
            actualizado = self.service.guardar_nivel(request.form, id_nivel)
            flash(
                "Nivel actualizado correctamente."
                if actualizado else "No se encontró el nivel.",
                "success" if actualizado else "error",
            )
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("gamificacion.admin_niveles"))
