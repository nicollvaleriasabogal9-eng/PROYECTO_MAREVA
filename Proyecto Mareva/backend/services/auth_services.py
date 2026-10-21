from repositories.auth_repository import AuthRepository
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

import os
import secrets
import urllib.parse
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class AuthServices():

    def __init__(self):
        self.repository = AuthRepository()

    def registrar_usuario(
        self,
        nombre,
        apellido,
        tipo_documento,
        numero_documento,
        telefono,
        codigo,
        correo,
        password,
        acepta_politica_no_reembolso=False
    ):
        resultado = self.repository.guardar_usuario(
            nombre,
            apellido,
            tipo_documento,
            numero_documento,
            telefono,
            codigo,
            correo,
            password,
            acepta_politica_no_reembolso
        )

        return resultado

    def actualizar_correo(self, id_cliente, correo):
        return self.repository.actualizar_correo(id_cliente, correo)

    def cambiar_password(self, id_cliente, password_actual, password_nueva):
        actual_hash = self.repository.obtener_password_por_id(id_cliente)
        if not actual_hash or not check_password_hash(actual_hash, password_actual):
            return {"ok": False, "error": "La contraseña actual no es correcta."}
        if password_actual == password_nueva:
            return {"ok": False, "error": "La nueva contraseña debe ser diferente."}
        import re
        if not (len(password_nueva) >= 8 and re.search(r"[A-ZÁÉÍÓÚÑ]", password_nueva) and re.search(r"\d", password_nueva) and re.search(r"[^A-Za-z0-9]", password_nueva)):
            return {"ok": False, "error": "La contraseña debe tener mínimo 8 caracteres, mayúscula, número y carácter especial."}
        ok = self.repository.actualizar_password(id_cliente, generate_password_hash(password_nueva))
        return {"ok": ok, "error": None if ok else "No fue posible actualizar la contraseña."}

    def favoritos(self, id_cliente):
        return self.repository.obtener_favoritos_cliente(id_cliente)

    def iniciar_sesion(self, correo, password):


        estado = self.repository.estado_acceso_cliente(correo)
        password_hash = self.repository.obtener_password_por_correo(correo)

        if password_hash is not None:
            if estado and not estado[1]:
                return None
            if estado and estado[3] and estado[3] > datetime.now():
                return None
            if check_password_hash(password_hash, password):
                self.repository.limpiar_intentos(correo)
                return self.repository.buscar_por_correo(correo)
            intentos = (estado[2] if estado else 0) + 1
            if intentos >= 5:
                self.repository.registrar_intento_fallido(correo, datetime.now() + timedelta(minutes=15))
            else:
                self.repository.registrar_intento_fallido(correo)
            return None

        proveedor_password = self.repository.obtener_proveedor_password_por_correo(correo) 
        
        if proveedor_password is not None: 
            if check_password_hash(proveedor_password, password): 
                proveedor = self.repository.buscar_proveedor_por_correo(correo) 
                if proveedor and proveedor["estado"]: 
                    return proveedor 
                return None


        guia_password = self.repository.obtener_guia_password_por_correo(correo)

        if guia_password is not None:

            if check_password_hash(guia_password, password):

                guia = self.repository.buscar_guia_por_correo(correo)

                if guia and guia["estado"]:
                    return guia

                return None

        return None

    def crear_url_google(self):

        client_id = os.getenv(
            "GOOGLE_CLIENT_ID",
            ""
        ).strip()

        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:5000/auth/google/callback"
        ).strip()

        if not client_id:

            return {
                "ok": False,
                "error": (
                    "Falta GOOGLE_CLIENT_ID en el archivo .env."
                )
            }

        state = secrets.token_urlsafe(32)

        parametros = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account"
        }

        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(parametros)
        )

        return {
            "ok": True,
            "url": url,
            "state": state
        }

    def procesar_codigo_google(self, code):

        client_id = os.getenv(
            "GOOGLE_CLIENT_ID",
            ""
        ).strip()

        client_secret = os.getenv(
            "GOOGLE_CLIENT_SECRET",
            ""
        ).strip()

        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:5000/auth/google/callback"
        ).strip()

        if not client_id:

            return {
                "ok": False,
                "error": (
                    "Falta GOOGLE_CLIENT_ID en el archivo .env."
                )
            }

        if not client_secret:

            return {
                "ok": False,
                "error": (
                    "Falta GOOGLE_CLIENT_SECRET en el archivo .env."
                )
            }

        try:

            respuesta = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                },
                timeout=20
            )

            try:
                datos = respuesta.json()
            except ValueError:
                datos = {}

            if respuesta.status_code != 200:

                print(
                    "GOOGLE TOKEN STATUS:",
                    respuesta.status_code
                )

                print(
                    "GOOGLE TOKEN RESPONSE:",
                    datos
                )

                return {
                    "ok": False,
                    "error": (
                        "Google no pudo completar la autorización."
                    )
                }

            token = datos.get("id_token")

            if not token:

                return {
                    "ok": False,
                    "error": (
                        "Google no devolvió el identificador "
                        "de la cuenta."
                    )
                }

            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
                clock_skew_in_seconds=30
            )

            if info.get("iss") not in {
                "accounts.google.com",
                "https://accounts.google.com"
            }:

                return {
                    "ok": False,
                    "error": (
                        "La identidad de Google no es válida."
                    )
                }

            correo = (
                info.get("email") or ""
            ).strip().lower()

            if not correo:

                return {
                    "ok": False,
                    "error": (
                        "Google no devolvió el correo."
                    )
                }

            if not info.get("email_verified"):

                return {
                    "ok": False,
                    "error": (
                        "Google no verificó el correo."
                    )
                }

            usuario = self.repository.buscar_por_correo(
                correo
            )

            if usuario is None:
                return {
                    "ok": True,
                    "nuevo": True,
                    "perfil_google": {
                        "correo": correo,
                        "nombre": info.get("given_name") or "",
                        "apellido": info.get("family_name") or ""
                    }
                }

            if usuario.rol != "cliente":

                return {
                    "ok": False,
                    "error": (
                        "Esta cuenta no corresponde a un cliente."
                    )
                }

            if not usuario.estado:

                return {
                    "ok": False,
                    "error": (
                        "La cuenta MAREVA está desactivada."
                    )
                }

            return {
                "ok": True,
                "usuario": usuario,
                "nuevo": False
            }

        except requests.RequestException as e:

            print(
                "GOOGLE REQUEST ERROR:",
                repr(e)
            )

            return {
                "ok": False,
                "error": (
                    "No fue posible conectar con Google."
                )
            }

        except ValueError as e:

            print(
                "GOOGLE VALUE ERROR:",
                repr(e)
            )

            return {
                "ok": False,
                "error": (
                    "La respuesta de Google no es válida."
                )
            }

        except Exception as e:

            print(
                "GOOGLE ERROR:",
                repr(e)
            )

            return {
                "ok": False,
                "error": (
                    "No fue posible iniciar sesión "
                    "con Google."
                )
            }