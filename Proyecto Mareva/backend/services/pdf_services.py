import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Paleta MAREVA Caribe
MOR_ADO = colors.HexColor("#2b0870")
TURQUESA = colors.HexColor("#0f8fa4")
CORAL = colors.HexColor("#ff6f61")
ARENA = colors.HexColor("#fdf5e4")
GRIS_TEXTO = colors.HexColor("#4a5568")
GRIS_CLARO = colors.HexColor("#f4f7f6")


class PDFService:
    """Genera un PDF simple y elegante con el resumen de una reserva."""

    def generar_resumen_reserva(self, detalle):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            title=f"Reserva {detalle.get('codigo_unico', '')} · MAREVA",
        )

        estilos = getSampleStyleSheet()
        estilo_marca = ParagraphStyle(
            "Marca", parent=estilos["Normal"], fontSize=20, textColor=MOR_ADO,
            fontName="Helvetica-Bold", spaceAfter=2,
        )
        estilo_subtitulo = ParagraphStyle(
            "Subtitulo", parent=estilos["Normal"], fontSize=9.5,
            textColor=GRIS_TEXTO, spaceAfter=10,
        )
        estilo_h2 = ParagraphStyle(
            "H2", parent=estilos["Normal"], fontSize=12.5, textColor=MOR_ADO,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
        )
        estilo_texto = ParagraphStyle(
            "Texto", parent=estilos["Normal"], fontSize=9.5,
            textColor=GRIS_TEXTO, leading=14,
        )
        estilo_codigo = ParagraphStyle(
            "Codigo", parent=estilos["Normal"], fontSize=13, textColor=CORAL,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        )
        estilo_pie = ParagraphStyle(
            "Pie", parent=estilos["Normal"], fontSize=7.6, textColor=colors.HexColor("#8a97a6"),
            leading=11,
        )

        elementos = []

        elementos.append(Paragraph("MAREVA", estilo_marca))
        elementos.append(Paragraph("Resumen de solicitud de reserva · Caribe colombiano", estilo_subtitulo))
        elementos.append(HRFlowable(width="100%", thickness=1.4, color=TURQUESA, spaceAfter=10))

        elementos.append(Paragraph("CÓDIGO DE RESERVA", ParagraphStyle(
            "Label", parent=estilo_texto, alignment=TA_CENTER, fontSize=8, textColor=GRIS_TEXTO
        )))
        elementos.append(Paragraph(detalle.get("codigo_unico", "-"), estilo_codigo))
        elementos.append(Spacer(1, 10))

        # --- Datos del paquete ---
        elementos.append(Paragraph("Tu experiencia", estilo_h2))
        datos_paquete = [
            ["Paquete", detalle.get("paquete_nombre", "-")],
            ["Destino", detalle.get("destino", "-")],
            ["Duración", detalle.get("duracion", "-")],
            ["Fecha del viaje", detalle.get("fecha_viaje") or "Por confirmar"],
            ["Viajeros", f"{detalle.get('adultos', 0)} adulto(s) · {detalle.get('menores', 0)} menor(es)"],
            ["Estado", detalle.get("estado", "Solicitada").capitalize()],
        ]
        tabla_paquete = Table(datos_paquete, colWidths=[45 * mm, 115 * mm])
        tabla_paquete.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.3),
            ("TEXTCOLOR", (0, 0), (0, -1), MOR_ADO),
            ("TEXTCOLOR", (1, 0), (1, -1), GRIS_TEXTO),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e5ecea")),
            ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
        ]))
        elementos.append(tabla_paquete)

        # --- Servicios seleccionados ---
        items_servicios = []

        if detalle.get("alojamientos"):
            for a in detalle["alojamientos"]:
                items_servicios.append(
                    ["🏨 Alojamiento", a.get("nombre", ""), f"$ {0:,.0f}"]
                )

        if detalle.get("alimentacion"):
            for a in detalle["alimentacion"]:
                items_servicios.append(
                    ["🍽️ Alimentación", a.get("restaurante", ""), f"$ {a.get('precio', 0) or 0:,.0f}"]
                )

        if detalle.get("transportes"):
            for t in detalle["transportes"]:
                items_servicios.append(
                    ["🚌 Transporte", f"{t.get('empresa', '')} ({t.get('tipo', '')})", f"$ {0:,.0f}"]
                )

        if detalle.get("actividades"):
            for a in detalle["actividades"]:
                items_servicios.append(
                    ["🎟️ Actividad", a.get("nombre", ""), f"$ {a.get('costo', 0) or 0:,.0f}"]
                )

        if detalle.get("seguros"):
            for s in detalle["seguros"]:
                items_servicios.append(
                    ["🛡️ Seguro", s.get("nombre", ""), f"$ {s.get('precio', 0) or 0:,.0f}"]
                )

        for e in (detalle.get("extras") or []):
            items_servicios.append(
                ["✨ Extra", e.get("nombre", ""), f"$ {e.get('precio', 0) or 0:,.0f}"]
            )

        if items_servicios:
            elementos.append(Paragraph("Servicios seleccionados", estilo_h2))
            filas_s = [["Tipo", "Servicio", "Precio"]] + items_servicios
            tabla_s = Table(filas_s, colWidths=[42 * mm, 92 * mm, 26 * mm])
            tabla_s.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), MOR_ADO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabla_s)

        # --- Personalización ---
        if detalle.get("personalizacion"):
            elementos.append(Paragraph("Personalización solicitada", estilo_h2))
            texto_per = str(detalle["personalizacion"]).replace("\n", "<br/>")
            elementos.append(Paragraph(texto_per, estilo_texto))

        # --- Extras ---
        if detalle.get("extras"):
            elementos.append(Paragraph("Experiencias opcionales agregadas", estilo_h2))
            filas = [["Servicio", "Precio"]] + [
                [e["nombre"], f"$ {e['precio']:,.0f}"] for e in detalle["extras"]
            ]
            tabla_extras = Table(filas, colWidths=[120 * mm, 40 * mm])
            tabla_extras.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), MOR_ADO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabla_extras)

        # --- Precio ---
        elementos.append(Spacer(1, 12))
        precio_total = detalle.get("precio_total", 0)
        tabla_precio = Table(
            [["Valor referencial de tu solicitud", f"$ {precio_total:,.0f} COP"]],
            colWidths=[110 * mm, 50 * mm],
        )
        tabla_precio.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), MOR_ADO),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ]))
        elementos.append(tabla_precio)

        # --- Notas ---
        if detalle.get("notas") or detalle.get("alergias"):
            elementos.append(Paragraph("Notas del viajero", estilo_h2))
            if detalle.get("alergias"):
                elementos.append(Paragraph(f"<b>Alergias / necesidades:</b> {detalle['alergias']}", estilo_texto))
            if detalle.get("notas"):
                elementos.append(Paragraph(f"<b>Solicitudes especiales:</b> {detalle['notas']}", estilo_texto))

        elementos.append(Spacer(1, 18))
        elementos.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#dfe6e4"), spaceAfter=8))

        elementos.append(Paragraph(
            "El pago de este viaje se realiza directamente al proveedor del servicio, "
            "siguiendo las instrucciones que MAREVA te compartirá por correo. MAREVA no procesa pagos "
            "ni cobra comisiones dentro de esta plataforma.",
            estilo_pie,
        ))
        elementos.append(Spacer(1, 4))
        elementos.append(Paragraph(
            "Esta solicitud queda sujeta a la Política de No Reembolso de MAREVA aceptada por el cliente "
            "durante su registro. Documento generado automáticamente, no requiere firma.",
            estilo_pie,
        ))

        doc.build(elementos)
        buffer.seek(0)
        return buffer