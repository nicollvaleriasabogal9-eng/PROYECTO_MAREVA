from flask import (request, render_template, redirect, url_for, session, flash)

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

        if resultado["ok"]:
            return render_template(
                "proveedor/registrar.html",
                mensaje="Proveedor registrado correctamente."
            )

        return render_template(
            "proveedor/registrar.html",
            error=resultado["error"]
        )


    def _obtener_proveedor_actual(self):

        usuario = session.get("usuario")

        if not usuario:
            return None

        if usuario.get("rol") != "proveedor":
            return None

        return usuario.get("id")


    def listar_contratos(self):

        proveedor_id = self._obtener_proveedor_actual()

        if not proveedor_id:
            return redirect(url_for("auth.mostrar_login"))

        contratos = self.service.obtener_contratos(
            proveedor_id
        )

        return render_template(
            "proveedor/contratos.html",
            contratos=contratos
        )


    def detalle_contrato(self, id_contrato):

        proveedor_id = self._obtener_proveedor_actual()

        if not proveedor_id:
            return redirect(url_for("auth.mostrar_login"))

        contrato = self.service.obtener_contrato(
            id_contrato,
            proveedor_id
        )

        if not contrato:
            flash(
                "El contrato no existe o no está disponible para este proveedor.",
                "error"
            )

            return redirect(
                url_for("proveedor.contratos")
            )

        return render_template(
            "proveedor/detalle_contrato.html",
            contrato=contrato
        )


    def responder_contrato(self, id_contrato):

        proveedor_id = self._obtener_proveedor_actual()

        if not proveedor_id:
            return redirect(url_for("auth.mostrar_login"))

        decision = request.form.get("decision")

        if decision not in ("aceptado", "rechazado"):
            flash(
                "La decisión enviada no es válida.",
                "error"
            )

            return redirect(
                url_for(
                    "proveedor.detalle_contrato",
                    id_contrato=id_contrato
                )
            )

        resultado = self.service.responder_contrato(
            id_contrato,
            proveedor_id,
            decision
        )

        if resultado["ok"]:
            flash(
                resultado["mensaje"],
                "success"
            )
        else:
            flash(
                resultado["error"],
                "error"
            )

        return redirect(
        url_for(
                "proveedor.detalle_contrato",
                id_contrato=id_contrato
            )
        )

# =========================================================
# RF-136
# FIRMA ELECTRÓNICA
# =========================================================

    def firmar_contrato(self, id_contrato):

        proveedor_id = self._obtener_proveedor_actual()

        if not proveedor_id:
            return redirect(url_for("auth.mostrar_login"))

        confirmacion = request.form.get(
            "confirmacion_firma"
        )

        if confirmacion != "acepto":
            flash(
                "Debe confirmar la firma electrónica del contrato.",
                "error"
            )

            return redirect(
                url_for(
                    "proveedor.detalle_contrato",
                    id_contrato=id_contrato
                )
            )

        resultado = self.service.firmar_contrato(
            id_contrato,
            proveedor_id
        )

        if resultado["ok"]:
            flash(
                resultado["mensaje"],
                "success"
            )
        else:
                flash(
                resultado["error"],
                "error"
            )

        return redirect(
            url_for(
                "proveedor.detalle_contrato",
                id_contrato=id_contrato
            )
        )

