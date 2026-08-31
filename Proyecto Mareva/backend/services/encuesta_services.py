import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from repositories.encuesta_repository import EncuestaRepository


class EncuestaService:

    def __init__(self):
        self.encuesta_repo = EncuestaRepository()

    def enviar_encuesta(self, correo_cliente, nombre_cliente, id_reserva):

        if not correo_cliente:
            return {
                "ok": False,
                "error": "El cliente no tiene un correo registrado."
            }

        correo_emisor = os.getenv("MAIL_USERNAME")
        contrasena = os.getenv("MAIL_PASSWORD")

        if not correo_emisor or not contrasena:
            print("ERROR: No están configuradas las credenciales del correo.")
            return {
                "ok": False,
                "error": "No está configurado el servicio de correo."
            }

        url_encuesta = (
            f"http://127.0.0.1:5000/encuesta/{id_reserva}"
        )

        mensaje = MIMEMultipart("alternative")

        mensaje["Subject"] = "Mareva - Encuesta de satisfacción"
        mensaje["From"] = correo_emisor
        mensaje["To"] = correo_cliente

        contenido = f"""
        <html>
            <body>
                <h2>¡Hola, {nombre_cliente}!</h2>

                <p>
                    Esperamos que hayas disfrutado tu viaje con Mareva.
                </p>

                <p>
                    Tu reserva ya fue marcada como completada.
                    Nos gustaría conocer tu experiencia.
                </p>

                <p>
                    <a href="{url_encuesta}">
                        Responder encuesta de satisfacción
                    </a>
                </p>

                <p>
                    Tu opinión nos ayuda a mejorar nuestros servicios.
                </p>

                <p>
                    Gracias por viajar con Mareva.
                </p>
            </body>
        </html>
        """

        mensaje.attach(MIMEText(contenido, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as servidor:

                servidor.starttls()

                servidor.login(
                    correo_emisor,
                    contrasena
                )

                servidor.sendmail(
                    correo_emisor,
                    correo_cliente,
                    mensaje.as_string()
                )

            print(
                f"Encuesta enviada correctamente a {correo_cliente}"
            )

            return {
                "ok": True
            }

        except Exception as e:

            print("ERROR ENVIANDO ENCUESTA:", e)

            return {
                "ok": False,
                "error": "No fue posible enviar la encuesta."
            }

    def obtener_encuesta(self, id_reserva, id_cliente):

        reserva = self.encuesta_repo.verificar_reserva_cliente(
            id_reserva,
            id_cliente
        )

        if not reserva:
            return {
                "ok": False,
                "error": "La reserva no existe o no pertenece al usuario."
            }

        if reserva["estado"] != "completada":
            return {
                "ok": False,
                "error": "La encuesta estará disponible cuando el viaje haya sido completado."
            }

        preguntas = self.encuesta_repo.obtener_preguntas_activas()

        if not preguntas:
            return {
                "ok": False,
                "error": "Actualmente no hay preguntas disponibles para la encuesta."
            }

        return {
            "ok": True,
            "reserva": reserva,
            "preguntas": preguntas
        }

    def obtener_preguntas_admin(self):
        return self.encuesta_repo.obtener_todas_preguntas()


    def obtener_pregunta(self, id_pregunta):
        return self.encuesta_repo.obtener_pregunta(id_pregunta)


    def crear_pregunta(self, texto, tipo_respuesta, orden):

        texto = texto.strip()

        if not texto:
            return {
                "ok": False,
                "error": "El texto de la pregunta es obligatorio."
            }

        if tipo_respuesta not in ("numero", "texto", "opcion"):
            return {
                "ok": False,
                "error": "El tipo de respuesta no es válido."
            }

        if orden < 1:
            return {
                "ok": False,
                "error": "El orden debe ser mayor a 0."
            }

        return self.encuesta_repo.crear_pregunta(
            texto,
            tipo_respuesta,
            orden
        )


    def actualizar_pregunta(
        self,
        id_pregunta,
        texto,
        tipo_respuesta,
        orden
    ):

        texto = texto.strip()

        if not texto:
            return {
                "ok": False,
                "error": "El texto de la pregunta es obligatorio."
            }

        if tipo_respuesta not in ("numero", "texto", "opcion"):
            return {
                "ok": False,
                "error": "El tipo de respuesta no es válido."
            }

        if orden < 1:
            return {
                "ok": False,
                "error": "El orden debe ser mayor a 0."
            }

        return self.encuesta_repo.actualizar_pregunta(
            id_pregunta,
            texto,
            tipo_respuesta,
            orden
        )


    def cambiar_estado_pregunta(self, id_pregunta):
        return self.encuesta_repo.cambiar_estado_pregunta(id_pregunta)

    def obtener_datos_reporte(self):
        return {
            "paquetes": self.encuesta_repo.obtener_paquetes_reporte(),
            "destinos": self.encuesta_repo.obtener_destinos_reporte()
        }


    def obtener_reporte(
        self,
        id_paquete=None,
        id_destino=None,
        fecha_inicio=None,
        fecha_fin=None
    ):
        return self.encuesta_repo.obtener_reporte_encuestas(
            id_paquete=id_paquete,
            id_destino=id_destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )