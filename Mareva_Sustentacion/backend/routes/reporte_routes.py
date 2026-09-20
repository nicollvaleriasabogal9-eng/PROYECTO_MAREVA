from flask import Blueprint
from controllers.reporte_controllers import ReporteController

reporte_bp = Blueprint("reporte", __name__)
controller = ReporteController()

# Panel principal de reportes
@reporte_bp.route("/admin/reportes")
def mostrar_panel():
    return controller.mostrar_panel()

# RF-89: Reporte de reservas por período
@reporte_bp.route("/api/reportes/reservas", methods=["GET"])
def obtener_reservas_periodo():
    return controller.obtener_reservas_periodo()

@reporte_bp.route("/descargar/reportes/reservas", methods=["GET"])
def descargar_reservas_periodo():
    return controller.descargar_reservas_periodo()

# RF-90: Reporte de paquetes más reservados
@reporte_bp.route("/api/reportes/paquetes-top", methods=["GET"])
def obtener_paquetes_top():
    return controller.obtener_paquetes_top()

@reporte_bp.route("/descargar/reportes/paquetes-top", methods=["GET"])
def descargar_paquetes_top():
    return controller.descargar_paquetes_top()

# RF-91: Reporte de canceladas
@reporte_bp.route("/api/reportes/canceladas", methods=["GET"])
def obtener_canceladas():
    return controller.obtener_canceladas()

@reporte_bp.route("/descargar/reportes/canceladas", methods=["GET"])
def descargar_canceladas():
    return controller.descargar_canceladas()

# RF-92: Reporte de ingresos
@reporte_bp.route("/api/reportes/ingresos", methods=["GET"])
def obtener_ingresos():
    return controller.obtener_ingresos()

@reporte_bp.route("/descargar/reportes/ingresos", methods=["GET"])
def descargar_ingresos():
    return controller.descargar_ingresos()

# RF-93: Reporte de destinos por temporada
@reporte_bp.route("/api/reportes/destinos-temporada", methods=["GET"])
def obtener_destinos_temporada():
    return controller.obtener_destinos_temporada()

@reporte_bp.route("/descargar/reportes/destinos-temporada", methods=["GET"])
def descargar_destinos_temporada():
    return controller.descargar_destinos_temporada()