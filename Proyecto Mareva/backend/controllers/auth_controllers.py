from flask import redirect, url_for, request, render_template, session
from services.auth_services import AuthServices
import re
import phonenumbers


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

        correo_valido = r"^[a-zA-Z0-9._%+-]+@(gmail|outlook|hotmail|live|yahoo)\.(com|es|co)$"

        if not re.fullmatch(correo_valido, correo):
            return render_template(
                "principal/registro.html",
                error="Solo se permiten correos Gmail, Outlook, Hotmail/Live o Yahoo."
            )


        # Validación de la contraseña

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
            password
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
            "rol": usuario.rol if hasattr(usuario, "rol") else usuario["rol"]
        }

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

