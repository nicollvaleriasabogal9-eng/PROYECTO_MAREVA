from flask import redirect, url_for, render_template, request
from services.destinos_services import DestinoService

CATEGORIAS_VALIDAS = ["playa", "ciudad", "aventura", "montaña", "cultural"]


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
            return redirect(url_for("destinos.listar_catalogo"))

        paquetes = self.service.paquetes_por_destino(id_destino)
        return render_template("cliente/destino_detalle.html", destino=destino, paquetes=paquetes)

    # ---- Administración ----

    # Panel con todos los destinos (activos e inactivos).
    def panel_admin(self):
        destinos = self.service.listar_todos()
        return render_template("admin/destinos.html", destinos=destinos, categorias=CATEGORIAS_VALIDAS)

    # Formulario para crear un destino nuevo.
    def mostrar_form_crear(self):
        return render_template("admin/form_destino.html", destino=None, categorias=CATEGORIAS_VALIDAS)

    # Formulario para editar un destino existente.
    def mostrar_form_editar(self, id_destino):
        destino = self.service.obtener_detalle(id_destino)
        if not destino:
            return redirect(url_for("destinos.panel_admin"))
        return render_template("admin/form_destino.html", destino=destino, categorias=CATEGORIAS_VALIDAS)

    # Crea el destino con los datos del formulario.
    def crear(self):
        datos, error = self._leer_form()
        if error:
            return render_template("admin/form_destino.html", destino=datos, categorias=CATEGORIAS_VALIDAS, error=error)

        self.service.crear_destino(datos)
        return redirect(url_for("destinos.panel_admin"))

    # Actualiza el destino con los datos del formulario.
    def actualizar(self, id_destino):
        datos, error = self._leer_form()
        if error:
            datos["id_destino"] = id_destino
            return render_template("admin/form_destino.html", destino=datos, categorias=CATEGORIAS_VALIDAS, error=error)

        self.service.actualizar_destino(id_destino, datos)
        return redirect(url_for("destinos.panel_admin"))

    # Suspende (borrado lógico) un destino.
    def suspender(self, id_destino):
        self.service.cambiar_estado(id_destino, False)
        return redirect(url_for("destinos.panel_admin"))

    # Reactiva un destino previamente suspendido.
    def activar(self, id_destino):
        self.service.cambiar_estado(id_destino, True)
        return redirect(url_for("destinos.panel_admin"))

    # Lee y valida los campos del formulario de destino.
    def _leer_form(self):
        datos = {
            "nombre_destino": request.form.get("nombre_destino", "").strip(),
            "departamento": request.form.get("departamento", "").strip(),
            "ciudad": request.form.get("ciudad", "").strip(),
            "categoria": request.form.get("categoria", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "atracciones": request.form.get("atracciones", "").strip(),
            "docs_requeridos": request.form.get("docs_requeridos", "").strip(),
            "imagen_principal": request.form.get("imagen_principal", "").strip(),
        }

        if not datos["nombre_destino"]:
            return datos, "El nombre del destino es obligatorio."
        if datos["categoria"] and datos["categoria"] not in CATEGORIAS_VALIDAS:
            return datos, "Selecciona una categoría válida."

        return datos, None
