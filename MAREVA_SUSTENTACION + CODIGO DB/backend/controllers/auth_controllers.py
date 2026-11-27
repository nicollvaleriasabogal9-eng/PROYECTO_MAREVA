from flask import redirect, url_for, request, render_template, session
from services.auth_services import AuthServices
from services.correo_service import CorreoService
import re
import phonenumbers
import secrets
import time


class AuthController:

    def __init__(self):
        self.service = AuthServices()
        self.correo_service = CorreoService()


    def registrar_usuario(self):
        perfil_google = self._registro_google_pendiente()
        if perfil_google:
            return self._registrar_usuario_google(perfil_google)

        nombre = " ".join(request.form.get("nombre", "").split())
        apellido = " ".join(request.form.get("apellido", "").split())
        tipo = request.form.get("tipo", "").strip()
        numero = request.form.get("numero", "").strip()
        telefono = request.form.get("telefono", "").strip()
        codigo = request.form.get("codigo", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        terminos = request.form.get("terminos")
        acepta_politica = request.form.get("politica_no_reembolso")

        def fallar(mensaje):
            return self._error_registro(mensaje)

        rol = request.form.get("rol", "cliente").strip().lower()
        if rol != "cliente":
            return fallar("El registro público solo permite cuentas de cliente.")

        if self.service.correo_en_uso(correo):
            return fallar("Ya existe una cuenta con ese correo.")

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", nombre):
            return fallar("El nombre solo puede contener letras.")

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", apellido):
            return fallar("El apellido solo puede contener letras.")

        tipos = ["CC", "TI", "CE", "PA", "PEP", "PPT", "RC"]
        if tipo not in tipos:
            return fallar("Seleccione un documento válido.")

        reglas_documento = {
            "CC": r"\d{6,10}",
            "TI": r"\d{10}",
            "CE": r"\d{6,7}",
            "PA": r"[A-Za-z0-9]{6,12}"
        }
        if tipo in reglas_documento and not re.fullmatch(reglas_documento[tipo], numero):
            return fallar("El número de documento no es válido.")

        try:
            if not telefono.startswith("+"):
                return fallar("Ingrese un teléfono válido.")

            numero_tel = phonenumbers.parse(telefono, None)
            if not phonenumbers.is_valid_number(numero_tel):
                return fallar("El teléfono no es válido para el país seleccionado.")
        except phonenumbers.NumberParseException:
            return fallar("Ingrese un teléfono válido.")

        if codigo and not re.fullmatch(r"[A-Za-z0-9]{1,20}", codigo):
            return fallar("Código de referido inválido.")

        correo_valido = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.fullmatch(correo_valido, correo):
            return fallar("El correo electrónico no es válido.")

        if not self._correo_verificado(correo, "registro"):
            return fallar("Debes verificar el correo electrónico antes de crear la cuenta.")

        if not terminos:
            return fallar("Debes aceptar los términos y condiciones.")
        if not acepta_politica:
            return fallar("Debes leer y aceptar la Política de No Reembolso para crear tu cuenta.")
        if password != confirm_password:
            return fallar("Las contraseñas no coinciden.")
        if not (len(password) >= 8 and re.search(r"[A-ZÁÉÍÓÚÑ]", password) and re.search(r"\d", password) and re.search(r"[^A-Za-z0-9]", password)):
            return fallar("La contraseña debe tener mínimo 8 caracteres, mayúscula, número y carácter especial.")

        resultado = self.service.registrar_usuario(
            nombre,
            apellido,
            tipo,
            numero,
            telefono,
            codigo,
            correo,
            password,
            True
        )

        if resultado["ok"]:
            session.pop("correo_verificado", None)
            try:
                self.correo_service.enviar_confirmacion_cuenta(
                    correo,
                    f"{nombre} {apellido}".strip()
                )
            except Exception:
                pass
            return render_template(
                "principal/login.html",
                mensaje="Registro exitoso. Ahora inicia sesión.",
                next=session.get("reserva_pendiente_url", "")
            )

        return fallar(resultado["error"])

    def _error_registro(self, error):
        datos = request.form.to_dict(flat=True)
        telefono_completo = datos.get("telefono", "")

        datos["codigoPais"] = "+57"
        datos["telefono"] = telefono_completo

        for prefijo in ("+593", "+57", "+52", "+34", "+54", "+56", "+51", "+58", "+1", "+55", "+44"):
            if telefono_completo.startswith(prefijo):
                datos["codigoPais"] = prefijo
                datos["telefono"] = telefono_completo[len(prefijo):]
                break

        return render_template(
            "principal/registro.html",
            error=error,
            datos=datos,
            correo_verificado=self._correo_verificado(
                datos.get("correo", ""),
                "registro"
            )
        )

    def _correo_verificado(self, correo, proposito="registro"):
        registro = session.get("correo_verificado")

        return bool(
            registro
            and registro.get("correo") == str(correo).strip().lower()
            and registro.get("proposito", "registro") == proposito
            and time.time() <= registro.get("expira", 0)
        )

    def enviar_codigo_correo(self):
        datos = request.get_json(silent=True) or {}
        correo = str(datos.get("correo", "")).strip().lower()
        proposito = (
            "perfil" if datos.get("proposito") == "perfil" else "registro"
        )
        correo_valido = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"

        if not re.fullmatch(correo_valido, correo):
            return {"ok": False, "error": "Ingresa un correo válido."}, 400

        if self._correo_verificado(correo, proposito):
            session.pop("verificacion_correo", None)
            return {
                "ok": True,
                "verificado": True,
                "mensaje": "Este correo ya está verificado."
            }, 200

        usuario_actual = session.get("usuario") or {}
        correo_actual = (
            str(usuario_actual.get("correo", "")).strip().lower()
            if proposito == "perfil" else None
        )

        if self.service.correo_en_uso(correo, correo_actual):
            return {
                "ok": False,
                "error": "Ya existe una cuenta con ese correo."
            }, 409

        previo = session.get("verificacion_correo") or {}
        if (
            previo.get("correo") == correo
            and previo.get("proposito") == proposito
            and time.time() - previo.get("enviado", 0) < 60
        ):
            return {
                "ok": True,
                "mensaje": "Ya enviamos un código. Revisa tu correo."
            }, 200

        codigo = f"{secrets.randbelow(900000) + 100000:06d}"

        session.pop("correo_verificado", None)
        session["verificacion_correo"] = {
            "correo": correo,
            "proposito": proposito,
            "codigo": codigo,
            "enviado": time.time(),
            "expira": time.time() + 600,
            "intentos": 0
        }

        envio = self.correo_service.enviar_codigo_verificacion(correo, codigo)

        if not envio.get("ok"):
            session.pop("verificacion_correo", None)
            return {
                "ok": False,
                "error": "No fue posible enviar el código. Intenta de nuevo."
            }, 500

        return {"ok": True, "mensaje": "Te enviamos un código de 6 dígitos."}, 200

    def verificar_codigo_correo(self):
        datos = request.get_json(silent=True) or {}
        codigo = str(datos.get("codigo", "")).strip()
        registro = session.get("verificacion_correo")

        if not registro:
            return {"ok": False, "error": "Primero solicita un código."}, 400

        if time.time() > registro.get("expira", 0):
            session.pop("verificacion_correo", None)
            return {"ok": False, "error": "El código venció. Solicita uno nuevo."}, 400

        if registro.get("intentos", 0) >= 5:
            return {"ok": False, "error": "Demasiados intentos. Solicita un código nuevo."}, 429

        if codigo != registro.get("codigo"):
            registro["intentos"] = registro.get("intentos", 0) + 1
            session["verificacion_correo"] = registro
            return {"ok": False, "error": "El código no es correcto."}, 400

        session["correo_verificado"] = {
            "correo": registro.get("correo"),
            "proposito": registro.get("proposito", "registro"),
            "expira": time.time() + 1800
        }
        session.pop("verificacion_correo", None)

        return {
            "ok": True,
            "verificado": True,
            "correo": registro.get("correo"),
            "mensaje": "Correo verificado correctamente."
        }, 200



    @staticmethod
    def _ids_favoritos_invitado():
        favoritos = []

        for valor in session.get("favoritos", []) or []:
            try:
                favoritos.append(int(valor))
            except (TypeError, ValueError):
                continue

        return favoritos

    @staticmethod
    def _url_reserva_pendiente_valida(url):
        return bool(url and url.startswith("/") and not url.startswith("//"))

    @staticmethod
    def _datos_reserva_pendiente():
        return {
            "url": session.get("reserva_pendiente_url"),
            "seleccion": session.get("seleccion_reserva"),
        }

    @staticmethod
    def _restaurar_datos_reserva_pendiente(datos):
        if AuthController._url_reserva_pendiente_valida(datos.get("url")):
            session["reserva_pendiente_url"] = datos["url"]
        if datos.get("seleccion"):
            session["seleccion_reserva"] = datos["seleccion"]

    def mostrar_recuperacion(self):
        return render_template(
            "principal/olvide_password.html",
            paso="correo"
        )

    def enviar_recuperacion(self):
        correo = request.form.get("correo", "").strip().lower()

        if not re.fullmatch(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", correo):
            return render_template(
                "principal/olvide_password.html",
                paso="correo",
                correo=correo,
                error="Escribe un correo electrónico válido."
            )

        if not self.service.correo_registrado(correo):
            return render_template(
                "principal/olvide_password.html",
                paso="correo",
                correo=correo,
                error="No encontramos una cuenta con ese correo."
            )

        codigo = secrets.randbelow(900000) + 100000
        session["recuperacion_password"] = {
            "correo": correo,
            "codigo": str(codigo),
            "expira": time.time() + 600,
            "intentos": 0,
            "verificado": False,
        }

        envio = self.correo_service.enviar_codigo_recuperacion(
            correo,
            codigo
        )

        if not envio.get("ok"):
            session.pop("recuperacion_password", None)
            return render_template(
                "principal/olvide_password.html",
                paso="correo",
                correo=correo,
                error="No fue posible enviar el código. Intenta de nuevo."
            )

        return render_template(
            "principal/olvide_password.html",
            paso="codigo",
            correo=correo,
            mensaje="Te enviamos un código de 6 dígitos a tu correo."
        )

    def verificar_recuperacion(self):
        datos = session.get("recuperacion_password")

        if not datos:
            return redirect(url_for("auth.mostrar_recuperacion"))

        if time.time() > datos["expira"]:
            session.pop("recuperacion_password", None)
            return render_template(
                "principal/olvide_password.html",
                paso="correo",
                error="El código venció. Solicita uno nuevo."
            )

        codigo = request.form.get("codigo", "").strip()

        if datos["intentos"] >= 5:
            session.pop("recuperacion_password", None)
            return render_template(
                "principal/olvide_password.html",
                paso="correo",
                error="Demasiados intentos. Solicita un código nuevo."
            )

        if codigo != datos["codigo"]:
            datos["intentos"] += 1
            session.modified = True
            return render_template(
                "principal/olvide_password.html",
                paso="codigo",
                correo=datos["correo"],
                error="El código no es correcto."
            )

        datos["verificado"] = True
        session.modified = True

        return render_template(
            "principal/olvide_password.html",
            paso="nueva",
            correo=datos["correo"]
        )

    def cambiar_password_recuperado(self):
        datos = session.get("recuperacion_password")

        if not datos or not datos.get("verificado"):
            return redirect(url_for("auth.mostrar_recuperacion"))

        password = request.form.get("password", "")
        confirmacion = request.form.get("confirmacion", "")

        if password != confirmacion:
            return render_template(
                "principal/olvide_password.html",
                paso="nueva",
                correo=datos["correo"],
                error="Las contraseñas no coinciden."
            )

        resultado = self.service.restablecer_password(
            datos["correo"],
            password
        )

        if not resultado.get("ok"):
            return render_template(
                "principal/olvide_password.html",
                paso="nueva",
                correo=datos["correo"],
                error=resultado.get("error", "No fue posible actualizar la contraseña.")
            )

        session.pop("recuperacion_password", None)

        return render_template(
            "principal/login.html",
            mensaje="Contraseña actualizada correctamente. Inicia sesión.",
            correo=datos["correo"]
        )

    def iniciar_sesion(self):

        correo = request.form.get("correo","").strip()
        password = request.form.get("password","")

        usuario = self.service.iniciar_sesion(correo, password)


        if usuario is None:
            return render_template(
                "principal/login.html",
                error="Correo o contraseña incorrectos.",
                correo=correo,
                next=request.args.get("next") or request.form.get("next")
            )

        #   Manejo de la sesión del usuario 
        recordar = request.form.get("recordar")
        session.permanent = bool(recordar)
        # Almacenar la información del usuario en la sesión
        session["usuario"] = {
            "id": usuario.id if hasattr(usuario, "id") else usuario["id"],
            "nombre": usuario.nombre if hasattr(usuario, "nombre") else usuario["nombre"],
            "apellido": usuario.apellido if hasattr(usuario, "apellido") else usuario.get("apellido"),
            "correo": usuario.correo if hasattr(usuario, "correo") else usuario["correo"],
            "rol": usuario.rol if hasattr(usuario, "rol") else usuario["rol"],
            "acepta_politica_no_reembolso": bool(getattr(usuario, "acepta_politica_no_reembolso", True))
        }

        session.pop("encuesta_descartada", None)

        if session["usuario"]["rol"] == "cliente":
            id_cliente = session["usuario"]["id"]
            favoritos_invitado = self._ids_favoritos_invitado()

            if favoritos_invitado:
                self.service.sincronizar_favoritos(
                    id_cliente,
                    favoritos_invitado
                )

            session["favoritos"] = self.service.favoritos(id_cliente)
        print("Usuario autenticado:", session["usuario"]["correo"])
      
        next_url = request.args.get("next") or request.form.get("next")
        reserva_pendiente = session.pop("reserva_pendiente_url", None)

        rol = session["usuario"]["rol"] # Redirecciones según el rol 
        if rol == "admin": 
            return redirect(url_for("dashboard.mostrar_panel")) 
        
        elif rol == "guia": 
            return redirect(url_for("guia.panel")) 
        
        elif rol == "proveedor": 
            return redirect(url_for("proveedor.contratos")) 
        
        elif self._url_reserva_pendiente_valida(reserva_pendiente):
            return redirect(reserva_pendiente)
        
        elif next_url and next_url.startswith("/") and not next_url.startswith("//"): 
            return redirect(next_url) 
        
        return redirect(url_for("home.home"))

    def _error_google(self, intencion, error):
        if intencion == "registro":
            return self.mostrar_registro(error=error)
        return render_template("principal/login.html", error=error)

    def iniciar_sesion_google(self, intencion="login"):

        session.pop("registro_google", None)

        resultado = self.service.crear_url_google()

        if not resultado.get("ok"):

            return self._error_google(intencion, error=resultado.get(
                    "error",
                    "No fue posible iniciar sesión con Google."
                )
            )

        session["google_state"] = resultado["state"]
        session["google_intencion"] = intencion

        return redirect(
            resultado["url"]
        )

    def google_callback(self):

        intencion = session.pop("google_intencion", "login")
        datos_pendientes = self._datos_reserva_pendiente()

        error = request.args.get(
            "error"
        )

        if error:

            session.pop("google_state", None)

            return self._error_google(intencion, error=(
                    "Google canceló o rechazó "
                    "el inicio de sesión."
                )
            )

        state = request.args.get(
            "state",
            ""
        )

        state_guardado = session.pop(
            "google_state",
            ""
        )

        if (
            not state
            or not state_guardado
            or state != state_guardado
        ):

            return self._error_google(intencion, error=(
                    "La solicitud de Google no es válida. "
                    "Vuelve a intentarlo."
                )
            )

        code = request.args.get(
            "code",
            ""
        )

        if not code:

            return self._error_google(intencion, error=(
                    "Google no devolvió el código "
                    "de autorización."
                )
            )

        resultado = self.service.procesar_codigo_google(
            code
        )

        if not resultado.get("ok"):

            return self._error_google(intencion, error=resultado.get(
                    "error",
                    "No fue posible iniciar sesión con Google."
                )
            )

        if resultado.get("nuevo"):
            if intencion != "registro":
                return self._error_google(
                    "login", "Esta cuenta aún no está registrada. Ve a Crear cuenta y elige Registrarse con Google."
                )
            session.clear()
            self._restaurar_datos_reserva_pendiente(datos_pendientes)
            session["registro_google"] = {
                **resultado["perfil_google"],
                "creado": time.time(),
                "token": secrets.token_urlsafe(32)
            }
            return redirect(url_for("auth.mostrar_registro"))

        if intencion == "registro":
            return self.mostrar_registro(
                error="Esta cuenta de Google ya está registrada. Usa Iniciar sesión para entrar."
            )

        session.clear()
        self._restaurar_datos_reserva_pendiente(datos_pendientes)
        usuario = resultado["usuario"]

        session.permanent = True

        self._guardar_sesion(
            usuario
        )

        session["auth_google"] = True

        return self._redirigir_por_rol()

    def _guardar_sesion(
        self,
        usuario
    ):

        session["usuario"] = {
            "id": (
                usuario.id
                if hasattr(usuario, "id")
                else usuario["id"]
            ),
            "nombre": (
                usuario.nombre
                if hasattr(usuario, "nombre")
                else usuario["nombre"]
            ),
            "apellido": (
                usuario.apellido
                if hasattr(usuario, "apellido")
                else usuario.get("apellido")
            ),
            "correo": (
                usuario.correo
                if hasattr(usuario, "correo")
                else usuario["correo"]
            ),
            "rol": (
                usuario.rol
                if hasattr(usuario, "rol")
                else usuario["rol"]
            ),
            "acepta_politica_no_reembolso": bool(getattr(
                usuario,
                "acepta_politica_no_reembolso",
                True
            ))
        }

        session.pop("encuesta_descartada", None)

        if session["usuario"]["rol"] == "cliente":

            session["favoritos"] = (
                self.service.favoritos(
                    session["usuario"]["id"]
                )
            )

        print(
            "Usuario autenticado:",
            session["usuario"]["correo"]
        )

    def _redirigir_por_rol(
        self,
        next_url=None
    ):

        rol = session["usuario"]["rol"]
        reserva_pendiente = session.pop("reserva_pendiente_url", None)

        if rol == "admin":

            return redirect(
                url_for(
                    "dashboard.mostrar_panel"
                )
            )

        if rol == "guia":

            return redirect(
                url_for(
                    "guia.panel"
                )
            )

        if rol == "proveedor":

            return redirect(
                url_for(
                    "proveedor.contratos"
                )
            )

        if self._url_reserva_pendiente_valida(reserva_pendiente):

            return redirect(
                reserva_pendiente
            )

        if (
            next_url
            and next_url.startswith("/")
            and not next_url.startswith("//")
        ):

            return redirect(
                next_url
            )

        return redirect(
            url_for(
                "home.home"
            )
        )

    def mostrar_registro(self, error=None, next_url=None):
        if self._url_reserva_pendiente_valida(next_url):
            session["reserva_pendiente_url"] = next_url
        perfil = self._registro_google_pendiente()
        datos = dict(perfil or {})
        verificado = session.get("correo_verificado") or {}
        if (
            not perfil
            and verificado.get("correo")
            and verificado.get("proposito", "registro") == "registro"
        ):
            datos["correo"] = verificado["correo"]
        if request.method == "POST":
            for campo in ("nombre", "apellido", "tipo", "numero", "telefono", "codigo"):
                datos[campo] = request.form.get(campo, "")
            if not perfil:
                datos["correo"] = request.form.get("correo", "")
        return render_template(
            "principal/registro.html", error=error,
            google_registro=perfil, datos=datos,
            correo_verificado=self._correo_verificado(
                datos.get("correo", ""),
                "registro"
            ),
            next=session.get("reserva_pendiente_url", "")
        )

    def _registro_google_pendiente(self):
        perfil = session.get("registro_google")
        if perfil and time.time() - perfil.get("creado", 0) > 1800:
            session.pop("registro_google", None)
            return None
        return perfil

    def _registrar_usuario_google(self, perfil):
        datos_pendientes = self._datos_reserva_pendiente()
        nombre = " ".join(
            request.form.get("nombre", perfil.get("nombre", "")).split()
        )
        apellido = " ".join(
            request.form.get("apellido", perfil.get("apellido", "")).split()
        )
        numero = request.form.get("numero", "").strip()
        telefono = request.form.get("telefono", "").strip()
        terminos = request.form.get("terminos")
        politica = request.form.get("politica_no_reembolso")

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", nombre):
            return self.mostrar_registro(
                error="El nombre solo puede contener letras."
            )

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", apellido):
            return self.mostrar_registro(
                error="El apellido solo puede contener letras."
            )

        if not re.fullmatch(r"[A-Za-z0-9]{6,20}", numero):
            return self.mostrar_registro(
                error="Ingresa un número de documento válido."
            )

        try:

            if not telefono.startswith("+"):
                return self.mostrar_registro(
                    error="Ingrese un teléfono válido."
                )

            numero_tel = phonenumbers.parse(telefono, None)

            if not phonenumbers.is_valid_number(numero_tel):
                return self.mostrar_registro(
                    error="El teléfono no es válido para el país seleccionado."
                )

        except phonenumbers.NumberParseException:

            return self.mostrar_registro(
                error="Ingrese un teléfono válido."
            )

        if not terminos:
            return self.mostrar_registro(
                error="Debes aceptar los términos y condiciones."
            )

        if not politica:
            return self.mostrar_registro(
                error="Debes aceptar la Política de No Reembolso."
            )

        resultado = self.service.registrar_cliente_google(
            nombre,
            apellido,
            perfil.get("correo", ""),
            numero,
            telefono
        )

        if not resultado.get("ok"):
            return self.mostrar_registro(
                error=resultado.get(
                    "error",
                    "No fue posible crear la cuenta de Google."
                )
            )

        session.pop("registro_google", None)
        session.clear()
        self._restaurar_datos_reserva_pendiente(datos_pendientes)
        self._guardar_sesion(resultado["usuario"])
        session["auth_google"] = True

        return self._redirigir_por_rol()
