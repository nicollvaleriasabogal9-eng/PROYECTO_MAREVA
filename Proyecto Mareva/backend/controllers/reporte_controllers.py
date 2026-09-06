from flask import request, session, redirect, url_for, render_template, send_file, jsonify
from services.reporte_services import ReporteServices
from datetime import datetime, timedelta


class ReporteController:

    def __init__(self):
        self.service = ReporteServices()

    def mostrar_panel(self):
        """Muestra el panel principal de reportes"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        # Valores por defecto: últimos 30 días
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        return render_template(
            "admin/reportes.html",
            fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=fecha_fin.strftime("%Y-%m-%d")
        )

    # RF-89: Reporte de reservas por período
    def obtener_reservas_periodo(self):
        """Retorna datos de reservas en un período (JSON)"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        estado = request.args.get("estado")
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Fechas requeridas"}), 400
        
        try:
            reporte = self.service.generar_reporte_reservas_periodo(
                fecha_inicio, fecha_fin, estado
            )
            return jsonify(reporte), 200
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return jsonify({"error": "Error generando reporte"}), 500

    def descargar_reservas_periodo(self):
        """Descarga reporte de reservas a Excel"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        estado = request.args.get("estado")
        
        if not fecha_inicio or not fecha_fin:
            return redirect(url_for("reporte.mostrar_panel"))
        
        try:
            excel_file = self.service.exportar_excel_reservas_periodo(
                fecha_inicio, fecha_fin, estado
            )
            
            filename = f"reporte_reservas_{fecha_inicio}_{fecha_fin}.xlsx"
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            print(f"Error descargando reporte: {e}")
            return redirect(url_for("reporte.mostrar_panel"))

    # RF-90: Reporte de paquetes más reservados
    def obtener_paquetes_top(self):
        """Retorna ranking de paquetes más reservados (JSON)"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Fechas requeridas"}), 400
        
        try:
            reporte = self.service.generar_reporte_paquetes_top(fecha_inicio, fecha_fin)
            return jsonify(reporte), 200
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return jsonify({"error": "Error generando reporte"}), 500

    def descargar_paquetes_top(self):
        """Descarga ranking de paquetes a Excel"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return redirect(url_for("reporte.mostrar_panel"))
        
        try:
            excel_file = self.service.exportar_excel_paquetes_top(fecha_inicio, fecha_fin)
            
            filename = f"reporte_paquetes_top_{fecha_inicio}_{fecha_fin}.xlsx"
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            print(f"Error descargando reporte: {e}")
            return redirect(url_for("reporte.mostrar_panel"))

    # RF-91: Reporte de reservas canceladas
    def obtener_canceladas(self):
        """Retorna datos de reservas canceladas (JSON)"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Fechas requeridas"}), 400
        
        try:
            reporte = self.service.generar_reporte_canceladas(fecha_inicio, fecha_fin)
            return jsonify(reporte), 200
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return jsonify({"error": "Error generando reporte"}), 500

    def descargar_canceladas(self):
        """Descarga reporte de canceladas a Excel"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return redirect(url_for("reporte.mostrar_panel"))
        
        try:
            excel_file = self.service.exportar_excel_canceladas(fecha_inicio, fecha_fin)
            
            filename = f"reporte_canceladas_{fecha_inicio}_{fecha_fin}.xlsx"
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            print(f"Error descargando reporte: {e}")
            return redirect(url_for("reporte.mostrar_panel"))

    # RF-92: Reporte de ingresos esperados
    def obtener_ingresos(self):
        """Retorna datos de ingresos esperados (JSON)"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Fechas requeridas"}), 400
        
        try:
            reporte = self.service.generar_reporte_ingresos(fecha_inicio, fecha_fin)
            return jsonify(reporte), 200
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return jsonify({"error": "Error generando reporte"}), 500

    def descargar_ingresos(self):
        """Descarga reporte de ingresos a Excel"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return redirect(url_for("reporte.mostrar_panel"))
        
        try:
            excel_file = self.service.exportar_excel_ingresos(fecha_inicio, fecha_fin)
            
            filename = f"reporte_ingresos_{fecha_inicio}_{fecha_fin}.xlsx"
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            print(f"Error descargando reporte: {e}")
            return redirect(url_for("reporte.mostrar_panel"))

    # RF-93: Reporte de destinos por temporada
    def obtener_destinos_temporada(self):
        """Retorna datos de destinos por temporada (JSON)"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Fechas requeridas"}), 400
        
        try:
            reporte = self.service.generar_reporte_destinos_temporada(fecha_inicio, fecha_fin)
            return jsonify(reporte), 200
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return jsonify({"error": "Error generando reporte"}), 500

    def descargar_destinos_temporada(self):
        """Descarga reporte de destinos a Excel"""
        usuario = session.get("usuario")
        
        if not usuario or usuario.get("rol") != "admin":
            return redirect(url_for("auth.mostrar_login"))
        
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            return redirect(url_for("reporte.mostrar_panel"))
        
        try:
            excel_file = self.service.exportar_excel_destinos_temporada(fecha_inicio, fecha_fin)
            
            filename = f"reporte_destinos_{fecha_inicio}_{fecha_fin}.xlsx"
            return send_file(
                excel_file,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            print(f"Error descargando reporte: {e}")
            return redirect(url_for("reporte.mostrar_panel"))