from flask import flash, redirect, render_template, request, session, url_for

from services.guia_services import GuiaService


class GuiaController:

    def __init__(self):
        self.service = GuiaService()

    @staticmethod
    def _id_guia():
        return (session.get("usuario") or {}).get("id")

    def mostrar_panel(self):
        datos = self.service.obtener_panel(
            self._id_guia(), request.args.get("estado")
        )
        return render_template("guia/panel.html", **datos)

    def actualizar_estado(self, id_reserva):
        resultado = self.service.cambiar_estado_reserva(
            self._id_guia(),
            id_reserva,
            request.form.get("estado", ""),
        )
        flash(
            "Estado de la reserva actualizado."
            if resultado["ok"] else resultado["error"],
            "success" if resultado["ok"] else "error",
        )
        return redirect(url_for("guia.panel"))
