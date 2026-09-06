from repositories.dashboard_repository import DashboardRepository


class DashboardServices:

    def __init__(self):
        self.repo = DashboardRepository()

    # RF-123: Dashboard con métricas en tiempo real
    def generar_metricas_generales(self):
        """Genera las métricas principales del panel de administrador"""
        metricas = self.repo.obtener_metricas_generales()
        return metricas

    # RF-124: Alerta de reservas sin confirmar por más de 3 días
    def generar_alertas_reservas_sin_confirmar(self):
        """Genera la alerta de reservas pendientes de pago sin gestión"""
        datos = self.repo.obtener_alertas_reservas_sin_confirmar()

        return {
            "datos": datos,
            "total_alertas": len(datos),
            "hay_alertas": len(datos) > 0
        }

    # RF-125: Alerta de paquetes próximos a salir con cupos sin llenar
    def generar_alertas_paquetes_cupos(self):
        """Genera la alerta de paquetes con salida próxima y cupos disponibles"""
        datos = self.repo.obtener_alertas_paquetes_cupos_disponibles()

        total_cupos_sin_llenar = sum(p["cupos_disponibles"] for p in datos)

        return {
            "datos": datos,
            "total_alertas": len(datos),
            "total_cupos_sin_llenar": total_cupos_sin_llenar,
            "hay_alertas": len(datos) > 0
        }

    # RF-126: Resumen de niveles de usuarios activos
    def generar_resumen_niveles(self):
        """Genera la distribución de clientes activos por nivel"""
        datos = self.repo.obtener_resumen_niveles_usuarios()

        total_clientes = sum(n["cantidad_clientes"] for n in datos)

        for nivel in datos:
            nivel["porcentaje_del_total"] = (
                round((nivel["cantidad_clientes"] / total_clientes) * 100, 1)
                if total_clientes > 0 else 0
            )

        return {
            "datos": datos,
            "total_clientes": total_clientes
        }

    # Panel completo: junta todo para la carga inicial del dashboard
    def generar_panel_completo(self):
        """Genera toda la información del panel en una sola llamada"""
        return {
            "metricas": self.generar_metricas_generales(),
            "alertas_reservas": self.generar_alertas_reservas_sin_confirmar(),
            "alertas_paquetes": self.generar_alertas_paquetes_cupos(),
            "niveles": self.generar_resumen_niveles()
        }