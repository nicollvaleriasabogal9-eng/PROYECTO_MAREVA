from flask import Blueprint
from controllers.dashboard_controllers import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)
controller = DashboardController()

# Panel principal del dashboard
@dashboard_bp.route("/admin/dashboard")
def mostrar_panel():
    return controller.mostrar_panel()

# RF-123: Métricas en tiempo real
@dashboard_bp.route("/api/dashboard/metricas", methods=["GET"])
def obtener_metricas():
    return controller.obtener_metricas()

# RF-124: Alerta de reservas sin confirmar
@dashboard_bp.route("/api/dashboard/alertas-reservas", methods=["GET"])
def obtener_alertas_reservas():
    return controller.obtener_alertas_reservas()

# RF-125: Alerta de paquetes próximos a salir con cupos sin llenar
@dashboard_bp.route("/api/dashboard/alertas-paquetes", methods=["GET"])
def obtener_alertas_paquetes():
    return controller.obtener_alertas_paquetes()

# RF-126: Resumen de niveles de usuarios activos
@dashboard_bp.route("/api/dashboard/niveles", methods=["GET"])
def obtener_niveles():
    return controller.obtener_niveles()

# Panel completo (una sola llamada para la carga inicial)
@dashboard_bp.route("/api/dashboard/panel-completo", methods=["GET"])
def obtener_panel_completo():
    return controller.obtener_panel_completo()