from repositories.auth_repository import AuthRepository
from werkzeug.security import check_password_hash


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
        password
    ):
        resultado = self.repository.guardar_usuario(
            nombre,
            apellido,
            tipo_documento,
            numero_documento,
            telefono,
            codigo,
            correo,
            password
        )

        return resultado

    def iniciar_sesion(self, correo, password):
        # Obtiene el hash de la contraseña del usuario desde la base de datos
        password_hash = self.repository.obtener_password_por_correo(correo)

        if password_hash is None:
            return None
        # Verifica si la contraseña proporcionada coincide con el hash almacenado
        if not check_password_hash(password_hash, password):
            return None

        return self.repository.buscar_por_correo(correo)