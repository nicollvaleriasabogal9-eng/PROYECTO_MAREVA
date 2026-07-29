from flask import redirect, url_for, request
from backend.services.auth_services import AuthServices


class AuthController():
    
    def registrar_usuario():
        nombre = request.form.get["nombre"]
        apellido = request.form.get["apellido"]
        tipo_documento = request.form.get["tipo"]
        numero_documento = request.form.get["numero"]
        telefono = request.form.get["telefono"]
        rol = request.form.get["rol"]
        codigo = request.form.get["codigo"]
        correo = request.form.get["correo"]
        password = request.form.get["password"]

        return AuthServices.enviar_usuario(
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
    
    def iniciar_sesion():
        correo = request.form.get["correo"]
        password = request.form.get["password"]
        
        return AuthServices.iniciar_sesion(
            correo,
            password
        )