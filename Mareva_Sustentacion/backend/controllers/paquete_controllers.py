from flask import render_template,redirect,url_for,request,session
from services.paquete_services import PaqueteService
from services.historial_services import HistorialServices
from repositories.salida_repository import SalidaRepository

class PaqueteController:
    def __init__(self):
        self.service=PaqueteService()
        self.historial_services=HistorialServices()
        self.salida_repository=SalidaRepository()

    def listar_catalogo(self):
        termino=request.args.get("q","").strip()
        categoria=request.args.get("categoria","").strip()
        destino=request.args.get("destino","").strip()
        duracion=request.args.getlist("duracion")
        precio_min=request.args.get("precio_min","").strip()
        precio_max=request.args.get("precio_max","").strip()
        fecha_desde=request.args.get("fecha_desde","").strip()
        incluye=request.args.getlist("incluye")
        solo_disponibles=request.args.get("solo_disponibles")=="1"
        ordenar=request.args.get("ordenar","recomendados").strip()
        paquetes=self.service.filtrar(
            termino,categoria,duracion,precio_max,incluye,
            destino=destino,precio_min=precio_min,fecha_desde=fecha_desde,
            solo_disponibles=solo_disponibles,ordenar=ordenar
        )
        usuario=session.get("usuario")
        desde_historial=request.args.get("historial")=="1"
        if usuario and not desde_historial:
            id_cliente=usuario["id"]
            hay_filtros=bool(
                termino or categoria not in ("","todos") or duracion or precio_max or
                incluye or destino or precio_min or fecha_desde or solo_disponibles
            )
            if hay_filtros:
                self.historial_services.guardar_filtros(
                    termino,categoria,duracion,precio_max,incluye,id_cliente
                )
        destinos=self.service.repo.obtener_destinos()
        favoritos_ids=[]
        if session.get("usuario") and session["usuario"].get("rol")=="cliente":
            favoritos_ids=self.service.obtener_favoritos_cliente(session["usuario"]["id"])
            session["favoritos"]=favoritos_ids
        else:
            favoritos_ids=[int(i) for i in session.get("favoritos",[]) if str(i).isdigit()]
        return render_template(
            "cliente/paquetes.html",
            paquetes=paquetes,
            termino=termino,
            favoritos_ids=favoritos_ids,
            filtros={
                "categoria":categoria,
                "destino":destino,
                "duracion":duracion,
                "precio_min":precio_min,
                "precio_max":precio_max,
                "fecha_desde":fecha_desde,
                "incluye":incluye,
                "solo_disponibles":solo_disponibles,
                "ordenar":ordenar
            },
            destinos=destinos
        )

    def comparar(self):
        raw = request.args.getlist("ids")
        if not raw and request.args.get("ids"):
            raw = request.args.get("ids").split(",")
        raw = raw + request.args.getlist("id")
        ids = []
        for value in raw:
            try:
                value=int(value)
                if value>0 and value not in ids:
                    ids.append(value)
            except (TypeError,ValueError):
                continue
        ids=ids[:3]
        paquetes=self.service.comparar(ids)
        return render_template("cliente/comparar.html",paquetes=paquetes,ids=ids)

    def ver_detalle(self, slug):
        paquete = self.service.obtener_detalle(slug)

        if not paquete:
            return redirect(url_for("paquetes.listar_catalogo"))

        salidas = self.salida_repository.obtener_por_paquete(
            paquete["id_paquete"],
            solo_disponibles=True
        )

        # Agrupar salidas por mes para mostrarlas como calendario
        meses = {}
        for salida in salidas:
            clave = salida["fecha_salida"].strftime("%Y-%m")
            meses.setdefault(clave, []).append(salida)

        return render_template(
            "cliente/detalle_paquete.html",
            paquete=paquete,
            salidas=salidas,
            salidas_por_mes=meses
        )
    
    def panel_admin(self):
        paquetes=self.service.listar_todos_admin()
        for p in paquetes:
            p["reservas_activas"]=self.service.reservas_no_canceladas(p["id_paquete"])
        return render_template("admin/paquetes.html",paquetes=paquetes)

    def mostrar_form_crear(self):
        datos=self.service.datos_formulario()
        return render_template("admin/form_paquete.html",**datos,paquete=None)

    def crear(self):
        datos=self._leer_form()
        error=self._validar(datos)
        if error:
            datos_form=self.service.datos_formulario()
            return render_template("admin/form_paquete.html",**datos_form,paquete=None,error=error)
        self.service.crear_paquete(datos)
        return redirect(url_for("paquetes.panel_admin"))

    def mostrar_form_editar(self,id_paquete):
        paquete=self.service.obtener_para_editar(id_paquete)
        if not paquete:
            return redirect(url_for("paquetes.panel_admin"))
        datos=self.service.datos_formulario()
        return render_template("admin/form_paquete.html",**datos,paquete=paquete)

    def actualizar(self,id_paquete):
        datos=self._leer_form()
        error=self._validar(datos)
        if error:
            datos_form=self.service.datos_formulario()
            return render_template(
                "admin/form_paquete.html",**datos_form,
                paquete={"id_paquete":id_paquete,**datos},error=error
            )
        try:
            self.service.actualizar_paquete(id_paquete,datos)
        except ValueError as exc:
            datos_form=self.service.datos_formulario()
            return render_template(
                "admin/form_paquete.html",**datos_form,
                paquete={"id_paquete":id_paquete,**datos},error=str(exc)
            )
        return redirect(url_for("paquetes.panel_admin"))

    def suspender(self,id_paquete):
        from flask import flash
        resultado=self.service.suspender_seguro(id_paquete)
        if not resultado["ok"]:
            flash(
                resultado["error"]+
                f" Hay {resultado['reservas']} reserva(s) asociada(s). Usa la cancelación por contingencia solo si realmente corresponde.",
                "error"
            )
        else:
            flash("Paquete suspendido correctamente.","success")
        return redirect(url_for("paquetes.panel_admin"))

    def cancelar_por_contingencia(self,id_paquete):
        from flask import flash
        motivo=request.form.get("motivo","").strip()
        resultado=self.service.cancelar_por_contingencia(id_paquete,motivo)
        flash(
            f"Contingencia registrada. Se cancelaron {resultado.get('reservas_canceladas',0)} reserva(s) y quedaron marcadas para reembolso."
            if resultado["ok"] else resultado["error"],
            "success" if resultado["ok"] else "error"
        )
        return redirect(url_for("paquetes.panel_admin"))

    def activar(self,id_paquete):
        self.service.activar(id_paquete)
        return redirect(url_for("paquetes.panel_admin"))

    def _leer_form(self):
        return {
            "nombre":request.form.get("nombre","").strip(),
            "descripcion":request.form.get("descripcion","").strip(),
            "precio":request.form.get("precio","0"),
            "duracion_dias":request.form.get("duracion_dias","0"),
            "duracion_noches":request.form.get("duracion_noches","0"),
            "cupos_totales":request.form.get("cupos_totales","0"),
            "fecha_inicio":request.form.get("fecha_inicio") or None,
            "fecha_fin":request.form.get("fecha_fin") or None,
            "id_destino":request.form.get("id_destino"),
            "id_guia":request.form.get("id_guia") or None,
            "emoji":request.form.get("emoji","🧳").strip() or "🧳",
            "imagen_url":request.form.get("imagen_url","").strip() or None,
            "personalizable":request.form.get("personalizable")=="1"
        }

    def _validar(self,datos):
        if not datos["nombre"]:
            return "El nombre es obligatorio."
        if not datos["id_destino"]:
            return "Debes seleccionar un destino."
        try:
            precio=float(datos["precio"])
            if precio<=0:
                return "El precio debe ser mayor a 0."
            datos["precio"]=precio
            datos["duracion_dias"]=int(datos["duracion_dias"])
            datos["duracion_noches"]=int(datos["duracion_noches"])
            datos["cupos_totales"]=int(datos["cupos_totales"])
            datos["id_destino"]=int(datos["id_destino"])
            if datos["id_guia"]:
                datos["id_guia"]=int(datos["id_guia"])
            if datos["duracion_dias"]<=0:
                return "La duración debe ser mayor a 0."
            if datos["cupos_totales"]<=0:
                return "Los cupos deben ser mayores a 0."
            if datos["fecha_inicio"] and datos["fecha_fin"] and datos["fecha_fin"]<datos["fecha_inicio"]:
                return "La fecha final no puede ser anterior a la fecha inicial."
        except (ValueError,TypeError):
            return "Precio, duración y cupos deben ser numéricos."
        return None

    def comparar_paquetes(self):
        ids_param = request.args.getlist("ids")

        try:
            ids = [int(id_paquete) for id_paquete in ids_param]
        except ValueError:
            ids = []

        ids = list(dict.fromkeys(ids))[:3]

        if len(ids) < 2:
            return render_template(
                "cliente/comparar.html",
                paquetes=[]
            )

        paquetes = self.service.obtener_paquetes_para_comparar(ids)

        precio_minimo = None
        precio_maximo = None
        diferencia = 0

        if paquetes:
            precios = [
                float(p["precio"])
                for p in paquetes
                if p["precio"] is not None
            ]

            if precios:
                precio_minimo = min(precios)
                precio_maximo = max(precios)
                diferencia = precio_maximo - precio_minimo

                for paquete in paquetes:
                    if paquete["precio"] is not None:
                        precio = float(paquete["precio"])

                        paquete["es_mas_economico"] = (
                            precio == precio_minimo
                        )

                        paquete["es_mas_costoso"] = (
                            precio == precio_maximo
                        )

                        paquete["diferencia_maxima"] = (
                            precio_maximo - precio
                        )

        return render_template(
            "cliente/comparar.html",
            paquetes=paquetes,
            precio_minimo=precio_minimo,
            precio_maximo=precio_maximo,
            diferencia=diferencia
        )