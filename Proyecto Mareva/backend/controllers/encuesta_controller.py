from flask import render_template, session, request, redirect, url_for

from services.encuesta_services import EncuestaService


class EncuestaController:

    def __init__(self):
        self.service = EncuestaService()

    def mostrar_encuesta(self, id_reserva):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        resultado = self.service.obtener_encuesta(
            id_reserva,
            usuario["id"]
        )

        if not resultado["ok"]:
            return render_template(
                "cliente/encuesta.html",
                error=resultado["error"],
                reserva=None,
                preguntas=[]
            )

        return render_template(
            "cliente/encuesta.html",
            reserva=resultado["reserva"],
            preguntas=resultado["preguntas"],
            error=None
        )

    def panel_preguntas(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        preguntas = self.service.obtener_preguntas_admin()

        return render_template(
            "admin/encuesta_preguntas.html",
            preguntas=preguntas
        )


    def mostrar_form_pregunta(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        return render_template(
            "admin/encuesta_pregunta_form.html",
            pregunta=None,
            error=None
        )


    def crear_pregunta(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        texto = request.form.get("texto", "").strip()
        tipo_respuesta = request.form.get("tipo_respuesta", "").strip()

        try:
            orden = int(request.form.get("orden", 0))
        except (ValueError, TypeError):
            orden = 0

        resultado = self.service.crear_pregunta(
            texto,
            tipo_respuesta,
            orden
        )

        if not resultado["ok"]:
            return render_template(
                "admin/encuesta_pregunta_form.html",
                    pregunta={
                "texto": texto,
                "tipo_respuesta": tipo_respuesta,
                "orden": orden
            },
            error=resultado["error"]
        )

        return redirect(url_for("encuesta.panel_preguntas"))


    def mostrar_form_editar_pregunta(self, id_pregunta):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        pregunta = self.service.obtener_pregunta(id_pregunta)

        if not pregunta:
            return redirect(url_for("encuesta.panel_preguntas"))

        return render_template(
            "admin/encuesta_pregunta_form.html",
            pregunta=pregunta,
            error=None
        )


    def actualizar_pregunta(self, id_pregunta):

        print("========== ACTUALIZAR PREGUNTA ==========")
        print("ID recibido:", id_pregunta)


        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        texto = request.form.get("texto", "").strip()
        tipo_respuesta = request.form.get("tipo_respuesta", "").strip()

        try:
            orden = int(request.form.get("orden", 0))
        except (ValueError, TypeError):
           orden = 0

        resultado = self.service.actualizar_pregunta(
            id_pregunta,
            texto,
            tipo_respuesta,
            orden
        )

        if not resultado["ok"]:

            pregunta = self.service.obtener_pregunta(id_pregunta)

            if pregunta:
                pregunta["texto"] = texto
                pregunta["tipo_respuesta"] = tipo_respuesta
                pregunta["orden"] = orden

            return render_template(
                "admin/encuesta_pregunta_form.html",
                pregunta=pregunta,
                error=resultado["error"]
            )

        return redirect(url_for("encuesta.panel_preguntas"))


    def cambiar_estado_pregunta(self, id_pregunta):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        self.service.cambiar_estado_pregunta(id_pregunta)

        return redirect(url_for("encuesta.panel_preguntas"))

    def reporte(self):
        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        datos = self.service.obtener_datos_reporte()

        id_paquete = request.args.get("id_paquete") or None
        id_destino = request.args.get("id_destino") or None
        fecha_inicio = request.args.get("fecha_inicio") or None
        fecha_fin = request.args.get("fecha_fin") or None

        resultados = self.service.obtener_reporte(
            id_paquete=id_paquete,
            id_destino=id_destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        return render_template(
            "admin/reporte_encuestas.html",
            paquetes=datos["paquetes"],
            destinos=datos["destinos"],
            resultados=resultados,
            filtros={
                "id_paquete": id_paquete,
                "id_destino": id_destino,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }
    )