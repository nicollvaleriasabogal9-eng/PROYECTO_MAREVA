from flask import render_template, redirect, url_for, request, session
from services.paquete_services import PaqueteService


class PaqueteController:

    def __init__(self):
        self.service = PaqueteService()

    #Listado de paquetes para clientes
    def listar_catalogo(self):
        paquetes = self.service.listar_activos()
        return render_template("cliente/paquetes.html", paquetes=paquetes)
    #Listado de paquetes para clientes
    def ver_detalle(self, slug):
        paquete = self.service.obtener_detalle(slug)
        if not paquete:
            return redirect(url_for("paquetes.listar_catalogo"))
        return render_template("cliente/detalle_paquete.html", paquete=paquete)

    #Listado de paquetes para administradores
    def panel_admin(self):
        paquetes = self.service.listar_todos_admin()
        return render_template("cliente/paquetes.html", paquetes=paquetes)
    #Mostrar formulario para crear un paquete
    def mostrar_form_crear(self):
        datos = self.service.datos_formulario()
        return render_template("admin/form_paquete.html", **datos, paquete=None)
    # Crear un paquete
    def crear(self):
        datos = self._leer_form()
        error = self._validar(datos)
        if error:
            datos_form = self.service.datos_formulario()
            return render_template("admin/form_paquete.html", **datos_form, paquete=None, error=error)

        self.service.crear_paquete(datos)
        return redirect(url_for("paquetes.panel_admin"))
    # Mostrar formulario para editar un paquete
    def mostrar_form_editar(self, id_paquete):
        paquete = self.service.obtener_para_editar(id_paquete)
        if not paquete:
            return redirect(url_for("paquetes.panel_admin"))
        datos = self.service.datos_formulario()
        return render_template("admin/form_paquete.html", **datos, paquete=paquete)
    # Actualizar un paquete
    def actualizar(self, id_paquete):
        datos = self._leer_form()
        error = self._validar(datos)
        if error:
            datos_form = self.service.datos_formulario()
            return render_template("admin/form_paquete.html", **datos_form, paquete={"id_paquete": id_paquete, **datos}, error=error)

        self.service.actualizar_paquete(id_paquete, datos)
        return redirect(url_for("paquetes.panel_admin"))

    def suspender(self, id_paquete):
        self.service.suspender(id_paquete)
        return redirect(url_for("paquetes.panel_admin"))

    def activar(self, id_paquete):
        self.service.activar(id_paquete)
        return redirect(url_for("paquetes.panel_admin"))

    #Leer los datos del formulario
    def _leer_form(self):
        return {
            "nombre": request.form.get("nombre", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "precio": request.form.get("precio", "0"),
            "duracion_dias": request.form.get("duracion_dias", "0"),
            "duracion_noches": request.form.get("duracion_noches", "0"),
            "cupos_totales": request.form.get("cupos_totales", "0"),
            "fecha_inicio": request.form.get("fecha_inicio") or None,
            "fecha_fin": request.form.get("fecha_fin") or None,
            "id_destino": request.form.get("id_destino"),
            "id_guia": request.form.get("id_guia") or None,
            "emoji": request.form.get("emoji", "🧳").strip() or "🧳",
        }
    
    # Validación de los datos del formulario
    def _validar(self, datos):
        if not datos["nombre"]:
            return "El nombre es obligatorio."
        if not datos["id_destino"]:
            return "Debes seleccionar un destino."
        try:
            precio = float(datos["precio"])
            if precio <= 0:
                return "El precio debe ser mayor a 0."
            datos["precio"] = precio
            datos["duracion_dias"] = int(datos["duracion_dias"])
            datos["duracion_noches"] = int(datos["duracion_noches"])
            datos["cupos_totales"] = int(datos["cupos_totales"])
            datos["id_destino"] = int(datos["id_destino"])
            if datos["id_guia"]:
                datos["id_guia"] = int(datos["id_guia"])
        except (ValueError, TypeError):
            return "Precio, duración y cupos deben ser numéricos."
        return None