
from flask import request, render_template, redirect, url_for, session

from services.proveedor_services import ProveedorService


class ProveedorController:

    def __init__(self):
        self.service = ProveedorService()

    def mostrar_registro(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        return render_template("proveedor/registrar.html")

    def registrar_proveedor(self):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("auth.login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("home.home"))

        # =========================
        # OBTENER DATOS DEL FORMULARIO
        # =========================

        nombre = request.form.get("nombre", "").strip()
        nit = request.form.get("nit", "").strip()
        tipo_empresa = request.form.get("tipo_empresa", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        direccion = request.form.get("direccion", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip().lower()

        contrasena = request.form.get("contrasena", "")

        nombre_contacto = request.form.get(
            "nombre_contacto",
            ""
        ).strip()

        telefono_contacto = request.form.get(
            "telefono_contacto",
            ""
        ).strip()

        correo_contacto = request.form.get(
            "correo_contacto",
            ""
        ).strip().lower()

        # =========================
        # ENVIAR AL SERVICE
        # =========================

        resultado = self.service.registrar_proveedor(
            nombre,
            nit,
            tipo_empresa,
            descripcion,
            direccion,
            ciudad,
            telefono,
            correo,
            contrasena,
            nombre_contacto,
            telefono_contacto,
            correo_contacto
        )

        # =========================
        # RESULTADO
        # =========================

        if resultado["ok"]:
            return render_template(
                "proveedor/registrar.html",
                mensaje="Proveedor registrado correctamente."
            )

        return render_template(
            "proveedor/registrar.html",
            error=resultado["error"]
        )

