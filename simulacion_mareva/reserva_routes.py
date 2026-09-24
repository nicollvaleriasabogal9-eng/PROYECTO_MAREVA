from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    request,
    send_file,
    render_template
)

from controllers.reserva_controllers import ReservaController


reserva_bp = Blueprint("reserva", __name__)

controller = ReservaController()


@reserva_bp.route("/reserva/<slug>", methods=["GET"])
def mostrar_formulario(slug):

    if "usuario" not in session:
        return redirect(
            url_for(
                "auth.mostrar_login",
                next=f"/reserva/{slug}"
            )
        )

    return controller.mostrar_formulario(slug)


@reserva_bp.route(
    "/reserva/viajero/<int:id_viajero>/editar",
    methods=["POST"]
)
def guardar_cambios_viajero(id_viajero):

    return controller.guardar_cambios_viajero(
        id_viajero
    )


@reserva_bp.route(
    "/reserva/<int:id_reserva>/viajeros",
    methods=["GET"]
)
def modificar_viajeros(id_reserva):

    return controller.modificar_viajeros(
        id_reserva
    )


@reserva_bp.route(
    "/reservas/<int:id_reserva>/completar",
    methods=["POST"]
)
def completar_reserva(id_reserva):

    return controller.completar_reserva(
        id_reserva
    )


@reserva_bp.route(
    "/admin/reservas/<int:id_reserva>/reembolso",
    methods=["POST"]
)
def marcar_reembolso(id_reserva):

    return controller.marcar_reembolso(
        id_reserva
    )


@reserva_bp.route("/admin/reservas")
def listar_reservas_admin():

    return controller.listar_reservas_admin()


@reserva_bp.route(
    "/api/paquetes/<int:id_paquete>/disponibilidad",
    methods=["GET"]
)
def disponibilidad(id_paquete):

    return controller.disponibilidad_json(
        id_paquete
    )


@reserva_bp.route(
    "/reserva/preparar/<slug>",
    methods=["POST"]
)
def preparar(slug):

    return controller.preparar_reserva(
        slug
    )


@reserva_bp.route(
    "/reserva/confirmar/<slug>",
    methods=["GET"]
)
def confirmar_reserva(slug):

    return controller.mostrar_confirmacion_reserva(
        slug
    )


@reserva_bp.route(
    "/reserva/guardar/<slug>",
    methods=["POST"]
)
def guardar(slug):

    return controller.guardar_reserva(
        slug
    )


@reserva_bp.route(
    "/confirmar-reserva",
    methods=["POST"]
)
def confirmar():

    slug = (
        request.form.get("slug")
        or ""
    ).strip()

    if not slug:
        return redirect(
            url_for(
                "paquetes.listar_catalogo"
            )
        )

    return controller.confirmar(slug)


# =========================================================
# CONFIRMACIÓN DE RESERVA
# =========================================================

@reserva_bp.route(
    "/reserva/confirmacion",
    methods=["GET"]
)
def confirmacion():

    if "usuario" not in session:
        return redirect(
            url_for(
                "auth.mostrar_login"
            )
        )

    return controller.mostrar_confirmacion()


# =========================================================
# PAGO SIMULADO
# =========================================================

@reserva_bp.route(
    "/reserva/pago",
    methods=["GET"]
)
def pago():

    return controller.mostrar_pago()


@reserva_bp.route(
    "/reserva/pago/procesar",
    methods=["POST"]
)
def procesar_pago():

    return controller.procesar_pago()


@reserva_bp.route(
    "/reserva/pago/exitoso",
    methods=["GET"]
)
def pago_exitoso():

    if "usuario" not in session:
        return redirect(
            url_for(
                "auth.mostrar_login"
            )
        )

    detalle = session.get(
        "detalle_reserva"
    )

    pago = session.get(
        "pago_simulado"
    )

    if (
        not detalle
        or not pago
        or not pago.get("realizado")
    ):
        return redirect(
            url_for(
                "reserva.confirmacion"
            )
        )

    return render_template(
        "principal/pago_exitoso.html",
        reserva=detalle,
        pago=pago
    )


# =========================================================
# PDF
# =========================================================

@reserva_bp.route(
    "/reserva/confirmacion/pdf",
    methods=["GET"]
)
def descargar_pdf():

    if "usuario" not in session:
        return redirect(
            url_for(
                "auth.mostrar_login"
            )
        )

    resultado = controller.descargar_pdf()

    if not hasattr(
        resultado,
        "getvalue"
    ):
        return resultado

    return send_file(
        resultado,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="reserva_mareva.pdf"
    )