from flask import Blueprint

from controllers.encuesta_controller import EncuestaController


encuesta_bp = Blueprint(
    "encuesta",
    __name__,
    url_prefix="/encuesta"
)

controller = EncuestaController()


@encuesta_bp.route("/<int:id_reserva>", methods=["GET"])
def mostrar_encuesta(id_reserva):
    return controller.mostrar_encuesta(id_reserva)

@encuesta_bp.route("/admin/preguntas", methods=["GET"])
def panel_preguntas():

    return controller.panel_preguntas()


@encuesta_bp.route("/admin/preguntas/nueva", methods=["GET"])
def nueva_pregunta():

    return controller.mostrar_form_pregunta()


@encuesta_bp.route("/admin/preguntas/nueva", methods=["POST"])
def crear_pregunta():

    return controller.crear_pregunta()


@encuesta_bp.route(
    "/admin/preguntas/<int:id_pregunta>/editar",
    methods=["GET"]
)
def editar_pregunta(id_pregunta):

    return controller.mostrar_form_editar_pregunta(
        id_pregunta
    )

@encuesta_bp.route("/admin/encuestas/reporte", methods=["GET"])
def reporte():
    return controller.reporte()

@encuesta_bp.route(
    "/admin/preguntas/<int:id_pregunta>/editar",
    methods=["POST"]
)
def actualizar_pregunta(id_pregunta):

    return controller.actualizar_pregunta(
        id_pregunta
    )


@encuesta_bp.route(
    "/admin/preguntas/<int:id_pregunta>/estado",
    methods=["POST"]
)
def cambiar_estado_pregunta(id_pregunta):

    return controller.cambiar_estado_pregunta(
        id_pregunta
    )