from flask import redirect, url_for, request, render_template, session
from services.auth_services import AuthServices
import re
import phonenumbers
import secrets
import time


class AuthController:

    def __init__(self):
        self.service = AuthServices()


    def registrar_usuario(self):
        # Se obtenienen y limpian los datos del formulario
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

        #Validaciones de los datos del nombre del cliente
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", nombre):
            return render_template("principal/registro.html",
            error="El nombre solo puede contener letras.")

        #Validaciones de los datos del apellido del cliente
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", apellido):
            return render_template("principal/registro.html",
            error="El apellido solo puede contener letras.")

        #Validaciones de los datos del tipo de documento
        tipos = ["CC","TI","CE","PA","PEP","PPT","RC"]
        
        if tipo not in tipos:
            return render_template("principal/registro.html", error="Seleccione un documento válido.")

        #Validaciones de los datos del número de documento
        reglas_documento = {
            "CC": r"\d{6,10}", #Cantidad de dígitos para cédula de ciudadanía
            "TI": r"\d{10}", #Cantidad de dígitos para tarjeta de identidad
            "CE": r"\d{6,7}", #Cantidad de dígitos para cédula de extranjería
            "PA": r"[A-Za-z0-9]{6,12}" #Cantidad de caracteres para pasaporte
        }

        #Validación del número de documento según el tipo seleccionado
        if tipo in reglas_documento and not re.fullmatch(reglas_documento[tipo], numero):
            return render_template(
                "principal/registro.html",
                error="El número de documento no es válido."
            )

        #Validación del teléfono
        try:

            if not telefono.startswith("+"):
                return render_template("principal/registro.html", error="Ingrese un teléfono válido.")


            numero_tel = phonenumbers.parse(telefono, None)


            if not phonenumbers.is_valid_number(numero_tel):
                return render_template("principal/registro.html", error="El teléfono no es válido para el país seleccionado.")


        except phonenumbers.NumberParseException:

            return render_template("principal/registro.html", error="Ingrese un teléfono válido.")


        #Validación del código de referido
        if codigo and not re.fullmatch(r"[A-Za-z0-9]{1,20}", codigo):
            return render_template(
                "principal/registro.html",
                error="Código de referido inválido."
            )


        # Validación del correo electrónico

        correo_valido = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"

        if not re.fullmatch(correo_valido, correo):
            return render_template(
                "principal/registro.html",
                error="El correo electrónico no es válido."
            )


        # Validación de contraseña, confirmación y términos
        if not terminos:
            return render_template("principal/registro.html", error="Debes aceptar los términos y condiciones.")
        if not acepta_politica:
            return render_template("principal/registro.html", error="Debes leer y aceptar la Política de No Reembolso para crear tu cuenta.")
        if password != confirm_password:
            return render_template("principal/registro.html", error="Las contraseñas no coinciden.")
        if not (len(password) >= 8 and re.search(r"[A-ZÁÉÍÓÚÑ]", password) and re.search(r"\d", password) and re.search(r"[^A-Za-z0-9]", password)):
            return render_template("principal/registro.html", error="La contraseña debe tener mínimo 8 caracteres, mayúscula, número y carácter especial.")
        if len(password) < 8:
            return render_template(
                "principal/registro.html",
                error="La contraseña debe tener mínimo 8 caracteres."
            )

        # Envio de los datos al servicio para registrar el usuario
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
            return render_template(
                "principal/login.html",
                mensaje="Registro exitoso. Ahora inicia sesión."
            )

        return render_template(
            "principal/registro.html",
            error=resultado["error"]
        )



    def iniciar_sesion(self):

        correo = request.form.get("correo","").strip()
        password = request.form.get("password","")

        usuario = self.service.iniciar_sesion(correo, password)


        if usuario is None:
            return render_template("principal/login.html", error="Correo o contraseña incorrectos.", correo=correo)

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
            "acepta_politica_no_reembolso": getattr(usuario, "acepta_politica_no_reembolso", True)
        }

        if session["usuario"]["rol"] == "cliente":
            session["favoritos"] = self.service.favoritos(session["usuario"]["id"])
        print("Usuario autenticado:", session["usuario"]["correo"])
      
        next_url = request.args.get("next") or request.form.get("next")

        rol = session["usuario"]["rol"] # Redirecciones según el rol 
        if rol == "admin": 
            return redirect(url_for("dashboard.mostrar_panel")) 
        
        elif rol == "guia": 
            return redirect(url_for("guia.panel")) 
        
        elif rol == "proveedor": 
            return redirect(url_for("home.home")) 
        
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
            "acepta_politica_no_reembolso": getattr(
                usuario,
                "acepta_politica_no_reembolso",
                True
            )
        }

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
                    "home.home"
                )
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

    def mostrar_registro(self, error=None):
        perfil = self._registro_google_pendiente()
        datos = dict(perfil or {})
        if request.method == "POST":
            for campo in ("nombre", "apellido", "tipo", "numero", "telefono", "codigo"):
                datos[campo] = request.form.get(campo, "")
            if not perfil:
                datos["correo"] = request.form.get("correo", "")
        return render_template(
            "principal/registro.html", error=error,
            google_registro=perfil, datos=datos
        )

    def _registro_google_pendiente(self):
        perfil = session.get("registro_google")
        if perfil and time.time() - perfil.get("creado", 0) > 1800:
            session.pop("registro_google", None)
            return None
        return perfil