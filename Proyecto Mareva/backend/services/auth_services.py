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


        password_hash = self.repository.obtener_password_por_correo(correo)

        if password_hash is not None:

            if check_password_hash(password_hash, password):
                return self.repository.buscar_por_correo(correo)

            return None


        guia_password = self.repository.obtener_guia_password_por_correo(correo)

        if guia_password is not None:

            if check_password_hash(guia_password, password):

                guia = self.repository.buscar_guia_por_correo(correo)

                if guia and guia["estado"]:
                    return guia

                return None

        return None