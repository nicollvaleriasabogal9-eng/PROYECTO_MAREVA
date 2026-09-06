from flask import session, redirect, url_for, render_template, jsonify
from services.dashboard_services import DashboardServices


class DashboardController:

    def __init__(self):
        self.service = DashboardServices()

    def mostrar_panel(self):
        """Muestra el panel principal del dashboard de administrador"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))

        return render_template("admin/dashboard.html")

    # RF-123: Métricas en tiempo real
    def obtener_metricas(self):
        """Retorna las métricas generales del dashboard (JSON)"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        try:
            metricas = self.service.generar_metricas_generales()
            return jsonify(metricas), 200
        except Exception as e:
            print(f"Error generando métricas: {e}")
            return jsonify({"error": "Error generando métricas"}), 500

    # RF-124: Alerta de reservas sin confirmar
    def obtener_alertas_reservas(self):
        """Retorna la alerta de reservas pendientes de pago sin gestión (JSON)"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        try:
            alertas = self.service.generar_alertas_reservas_sin_confirmar()
            return jsonify(alertas), 200
        except Exception as e:
            print(f"Error generando alertas de reservas: {e}")
            return jsonify({"error": "Error generando alertas"}), 500

    # RF-125: Alerta de paquetes próximos a salir con cupos sin llenar
    def obtener_alertas_paquetes(self):
        """Retorna la alerta de paquetes con salida próxima y cupos disponibles (JSON)"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        try:
            alertas = self.service.generar_alertas_paquetes_cupos()
            return jsonify(alertas), 200
        except Exception as e:
            print(f"Error generando alertas de paquetes: {e}")
            return jsonify({"error": "Error generando alertas"}), 500

    # RF-126: Resumen de niveles de usuarios activos
    def obtener_niveles(self):
        """Retorna la distribución de clientes activos por nivel (JSON)"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        try:
            resumen = self.service.generar_resumen_niveles()
            return jsonify(resumen), 200
        except Exception as e:
            print(f"Error generando resumen de niveles: {e}")
            return jsonify({"error": "Error generando resumen"}), 500

    # Panel completo (una sola llamada para la carga inicial)
    def obtener_panel_completo(self):
        """Retorna toda la información del panel en una sola respuesta (JSON)"""
        usuario = session.get("usuario")

        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        try:
            panel = self.service.generar_panel_completo()
            return jsonify(panel), 200
        except Exception as e:
            print(f"Error generando panel completo: {e}")
            return jsonify({"error": "Error generando panel"}), 500