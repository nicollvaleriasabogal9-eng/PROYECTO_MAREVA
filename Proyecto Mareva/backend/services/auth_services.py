from repositories.auth_repository import AuthRepository
class AuthServices():

    def __init__(self):
        self.repository = AuthRepository()
    
    
    def iniciar_sesion(self, correo, password):
        usuario = self.repository.buscar_por_correo(correo)
        if usuario == None:
            return print("No se encontro un usuario con este correo")
        else:
            return print("el correo esta registrado")
        