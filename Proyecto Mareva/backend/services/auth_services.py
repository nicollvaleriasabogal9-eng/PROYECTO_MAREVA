from repositories.auth_repository import AuthRepository
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta


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