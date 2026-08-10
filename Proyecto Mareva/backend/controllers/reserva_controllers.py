from flask import request, session, redirect, url_for, render_template, jsonify
from services.reserva_services import ReservaService
from services.paquete_services import PaqueteService


class ReservaController:

    def __init__(self):
        self.service = ReservaService()
        self.paquete_service = PaqueteService()

    def mostrar_formulario(self, slug):
        paquete = self.paquete_service.obtener_detalle(slug)
        if not paquete:
            return redirect(url_for("paquetes.listar_catalogo"))
        return render_template("cliente/reserva.html", paquete=paquete)
    #Disponibilidad de un paquete en formato JSON
    def disponibilidad_json(self, id_paquete):
        data = self.paquete_service.obtener_disponibilidad(id_paquete)
        if not data:
            return jsonify({"error": "Paquete no encontrado"}), 404
        return jsonify(data), 200
    #Confirmación de la reserva
    def confirmar(self):
        usuario = session.get("usuario")
        if not usuario:
            return redirect(url_for("auth.mostrar_login"))

        slug = request.form.get("paquete")
        paquete = self.paquete_service.obtener_detalle(slug)
        if not paquete:
            return redirect(url_for("paquetes.listar_catalogo"))

        try:
            adultos = int(request.form.get("adultos", 1)) # Obtiene el número de adultos, por defecto 1
            menores = int(request.form.get("menores", 0)) # Obtiene el número de menores, por defecto 0
        except ValueError:
            adultos, menores = 1, 0

        fecha_viaje = request.form.get("fecha_inicio") or None
        notas = request.form.get("notas", "").strip()
        alergias = request.form.get("alergias", "").strip() or None
        mascotas = request.form.get("mascotas") == "si"
        plan = request.form.get("plan", "completo")
        extras_raw = request.form.getlist("extras")
        extras_ids = [int(e) for e in extras_raw if e.isdigit()]

        # Validación mínima de fechas contra el rango del paquete
        if fecha_viaje and paquete.get("fecha_inicio") and paquete.get("fecha_fin"):
            if not (str(paquete["fecha_inicio"]) <= fecha_viaje <= str(paquete["fecha_fin"])):
                return render_template("cliente/reserva.html", paquete=paquete,
                                        error="La fecha elegida está fuera del rango disponible para este paquete.")

        viajeros = self._leer_viajeros(adultos + menores)
        
        resultado = self.service.confirmar_reserva(
            id_cliente=usuario["id"],
            id_paquete=paquete["id_paquete"],
            cant_adultos=adultos,
            cant_menores=menores,
            fecha_viaje=fecha_viaje,
            observaciones=notas,
            alergias=alergias,
            mascotas=mascotas,
            plan=plan,
            metodo_contacto="correo",
            extras_ids=extras_ids,
            viajeros=viajeros,
        )

        if not resultado["ok"]:
            paquete_actual = self.paquete_service.obtener_detalle(slug)
            return render_template("cliente/reserva.html", paquete=paquete_actual, error=resultado["error"])

        session["ultima_reserva_codigo"] = resultado["codigo_unico"]
        return redirect(url_for("home.home"))
    #Lee los datos de los viajeros desde el formulario
    def _leer_viajeros(self, total_personas):
        viajeros = []
        for i in range(total_personas):
            nombre = request.form.get(f"viajero_nombre_{i}", "").strip()
            if not nombre:
                continue
            viajeros.append({
                "nombre": nombre,
                "apellido": request.form.get(f"viajero_apellido_{i}", "").strip(),
                "tipo_documento": request.form.get(f"viajero_tipo_doc_{i}", "CC").strip(),
                "numero_documento": request.form.get(f"viajero_num_doc_{i}", "").strip(),
            })
        return viajeros