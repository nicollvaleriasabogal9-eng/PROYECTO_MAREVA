from flask import redirect, url_for, request, render_template, session
from services.auth_services import AuthServices

class AuthController():
    
    def __init__(self):
        self.service = AuthServices()

    def registrar_usuario(self):

        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        tipo_documento = request.form.get("tipo")
        numero_documento = request.form.get("numero")
        telefono = request.form.get("telefono")
        rol = request.form.get("rol")
        codigo = request.form.get("codigo")
        correo = request.form.get("correo")
        password = request.form.get("password")
        print("Se tomaron los datos correctamente")
        print(request.form)
        return self.service.enviar_usuario(
            nombre,
            apellido,
            tipo_documento,
            numero_documento,
            telefono,
            rol,
            codigo,
            correo,
            password
        )
    
    def iniciar_sesion(self):

        correo = request.form.get("correo")
        password = request.form.get("password")

        usuario = self.service.iniciar_sesion(correo, password)

        if usuario is None:
            print("Usuario no encontrado")
            return render_template("principal/login.html")
        else:
            session["usuario"] = {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "rol": usuario.rol
            }
            return redirect(url_for('home.home'))
