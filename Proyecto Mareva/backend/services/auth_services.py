from repositories.auth_repository import AuthRepository
class AuthServices():

    def __init__(self):
        self.repository = AuthRepository()

    def registrar_usuario(self, nombre, apellido, tipo_documento, numero_documento, telefono, codigo, correo, password):

        usuario = self.repository.guardar_usuario(
            nombre,
            apellido,
            tipo_documento,
            numero_documento,
            telefono,
            codigo,
            correo,
            password
        )

        return True

    def iniciar_sesion(self, correo, password):

        usuario = self.repository.buscar_por_correo(correo)

        if usuario is None:
            return print("No se encontro un usuario con este correo")
        else:
            if password == usuario.password:
                print("Inicio Sesion correctamente")
                return usuario
            else:
                print("La contraseña ingresada es incorrecta")
            

        