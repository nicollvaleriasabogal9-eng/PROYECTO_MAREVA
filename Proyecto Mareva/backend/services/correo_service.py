import os
import smtplib

from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

class CorreoService:
    """Servicio centralizado para enviar correos de MAREVA mediante Gmail SMTP."""

    def _configuracion(self):
        correo_emisor = os.getenv("SMTP_USER")
        contrasena = os.getenv("SMTP_PASSWORD")
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not correo_emisor or not contrasena:
            return None

        return {
            "correo_emisor": correo_emisor,
            "contrasena": contrasena,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
        }

    def enviar_confirmacion_reserva(self, correo_cliente, nombre_cliente, reserva):
        """
        Envía al cliente la confirmación de una reserva recién creada.

        El envío es independiente de la creación de la reserva:
        si SMTP falla, la reserva no se deshace.
        """
        if not correo_cliente:
            return {
                "ok": False,
                "error": "El cliente no tiene un correo registrado."
            }

        config = self._configuracion()

        if not config:
            print(
                "ERROR: No están configuradas las credenciales del correo "
                "(revisa SMTP_USER / SMTP_PASSWORD en el .env)."
            )
            return {
                "ok": False,
                "error": "No está configurado el servicio de correo."
            }

        codigo = reserva.get("codigo_unico", "N/D")
        paquete = reserva.get("paquete", {})
        paquete_nombre = paquete.get("nombre", "N/D")
        fecha_viaje = reserva.get("fecha_viaje", "N/D")
        fecha_regreso = reserva.get("fecha_regreso", "N/D")
        adultos = reserva.get("cant_adultos", 0)
        menores = reserva.get("cant_menores", 0)
        total_personas = reserva.get("total_personas", adultos + menores)
        valor = reserva.get("valor_referencial", 0)
        plan = reserva.get("plan", "N/D")
        metodo_contacto = reserva.get("metodo_contacto", "N/D")

        viajeros_html = ""
        for viajero in reserva.get("viajeros", []):
            viajeros_html += f"""
                <li>
                    {viajero.get("nombre", "")} {viajero.get("apellido", "")}
                    — {viajero.get("tipo_documento", "")}:
                    {viajero.get("numero_documento", "")}
                </li>
            """

        if not viajeros_html:
            viajeros_html = "<li>Información de viajeros registrada en MAREVA.</li>"

        asunto = f"MAREVA - Confirmación de reserva {codigo}"

        contenido = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.5;">
                <div style="max-width: 680px; margin: auto;">
                    <h2 style="margin-bottom: 4px;">¡Hola, {nombre_cliente}!</h2>
                    <p>
                        Hemos recibido correctamente tu reserva en <strong>MAREVA</strong>.
                    </p>

                    <div style="padding: 18px; border: 1px solid #ddd; border-radius: 10px;">
                        <h3 style="margin-top: 0;">Resumen de tu reserva</h3>
                        <p><strong>Código:</strong> {codigo}</p>
                        <p><strong>Paquete:</strong> {paquete_nombre}</p>
                        <p><strong>Fecha de viaje:</strong> {fecha_viaje}</p>
                        <p><strong>Fecha de regreso:</strong> {fecha_regreso}</p>
                        <p><strong>Adultos:</strong> {adultos}</p>
                        <p><strong>Menores:</strong> {menores}</p>
                        <p><strong>Total de viajeros:</strong> {total_personas}</p>
                        <p><strong>Plan:</strong> {plan}</p>
                        <p><strong>Método de contacto:</strong> {metodo_contacto}</p>
                        <p><strong>Valor referencial:</strong> ${valor:,.0f}</p>

                        <h4>Viajeros</h4>
                        <ul>
                            {viajeros_html}
                        </ul>
                    </div>

                    <p>
                        Tu reserva ha quedado registrada. Conserva el código
                        <strong>{codigo}</strong> para futuras consultas.
                    </p>

                    <p>
                        Gracias por elegir MAREVA. 🌴
                    </p>
                </div>
            </body>
        </html>
        """

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = config["correo_emisor"]
        mensaje["To"] = correo_cliente
        mensaje.attach(MIMEText(contenido, "html", "utf-8"))

        try:
            with smtplib.SMTP(
                config["smtp_host"],
                config["smtp_port"],
                timeout=20
            ) as servidor:
                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()

                servidor.login(
                    config["correo_emisor"],
                    config["contrasena"]
                )
                
                servidor.sendmail(
                    config["correo_emisor"],
                    [correo_cliente],
                    mensaje.as_string()
                )

            print(f"Confirmación de reserva enviada a {correo_cliente}")

            return {"ok": True}

        except Exception as e:
            print("ERROR ENVIANDO CONFIRMACIÓN DE RESERVA:", e)
            return {
                "ok": False,
                "error": f"No fue posible enviar el correo ({e})."
            }