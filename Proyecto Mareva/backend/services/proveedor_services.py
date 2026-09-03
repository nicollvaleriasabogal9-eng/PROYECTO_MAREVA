
import re
import phonenumbers

from repositories.proveedor_repositories import ProveedorRepository


class ProveedorService:

    def __init__(self):
        self.repository = ProveedorRepository()

    def registrar_proveedor(
        self,
        nombre,
        nit,
        tipo_empresa,
        descripcion,
        direccion,
        ciudad,
        telefono,
        correo,
        contrasena,
        nombre_contacto,
        telefono_contacto,
        correo_contacto
    ):


        nombre = " ".join(nombre.split())

        if not nombre:
            return {
                "ok": False,
                "campo": "nombre",
                "error": "El nombre del proveedor es obligatorio."
            }

        if len(nombre) < 2 or len(nombre) > 100:
            return {
                "ok": False,
                "campo": "nombre",
                "error": "El nombre debe tener entre 2 y 100 caracteres."
            }


        nit = nit.strip()

        if not nit:
            return {
                "ok": False,
                "campo": "nit",
                "error": "El NIT es obligatorio."
            }

        if not re.fullmatch(r"[0-9-]{5,30}", nit):
            return {
                "ok": False,
                "campo": "nit",
                "error": "El NIT solo puede contener números y guiones."
            }


        tipo_empresa = " ".join(tipo_empresa.split())

        if not tipo_empresa:
            return {
                "ok": False,
                "campo": "tipo_empresa",
                "error": "El tipo de empresa es obligatorio."
            }

        if len(tipo_empresa) > 50:
            return {
                "ok": False,
                "campo": "tipo_empresa",
                "error": "El tipo de empresa no puede superar los 50 caracteres."
            }

        descripcion = descripcion.strip()

        if not descripcion:
            return {
                "ok": False,
                "campo": "descripcion",
                "error": "La descripción es obligatoria."
            }

        if len(descripcion) > 1000:
            return {
                "ok": False,
                "campo": "descripcion",
                "error": "La descripción no puede superar los 1000 caracteres."
            }


        direccion = direccion.strip()

        if direccion and len(direccion) > 200:
            return {
                "ok": False,
                "campo": "direccion",
                "error": "La dirección no puede superar los 200 caracteres."
            }


        ciudad = " ".join(ciudad.split())

        if ciudad and len(ciudad) > 100:
            return {
                "ok": False,
                "campo": "ciudad",
                "error": "La ciudad no puede superar los 100 caracteres."
            }


        if telefono:

            try:
                if not telefono.startswith("+"):
                    return {
                        "ok": False,
                        "campo": "telefono",
                        "error": "Ingrese el teléfono con código de país."
                    }

                numero_tel = phonenumbers.parse(telefono, None)

                if not phonenumbers.is_valid_number(numero_tel):
                    return {
                        "ok": False,
                        "campo": "telefono",
                        "error": "El teléfono no es válido."
                    }

            except phonenumbers.NumberParseException:
                return {
                    "ok": False,
                    "campo": "telefono",
                    "error": "Ingrese un teléfono válido."
                }


        correo = correo.strip().lower()

        if not correo:
            return {
                "ok": False,
                "campo": "correo",
                "error": "El correo electrónico es obligatorio."
            }

        correo_valido = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.fullmatch(correo_valido, correo):
            return {
                "ok": False,
                "campo": "correo",
                "error": "Ingrese un correo electrónico válido."
            }


        if not contrasena:
            return {
                "ok": False,
                "campo": "contrasena",
                "error": "La contraseña es obligatoria."
            }

        if len(contrasena) < 8:
            return {
                "ok": False,
                "campo": "contrasena",
                "error": "La contraseña debe tener mínimo 8 caracteres."
            }

        nombre_contacto = " ".join(nombre_contacto.split())

        if nombre_contacto and len(nombre_contacto) > 100:
            return {
                "ok": False,
                "campo": "nombre_contacto",
                "error": "El nombre del contacto no puede superar los 100 caracteres."
            }

        if telefono_contacto:

            try:
                if not telefono_contacto.startswith("+"):
                    return {
                        "ok": False,
                        "campo": "telefono_contacto",
                        "error": "Ingrese el teléfono del contacto con código de país."
                    }

                numero_contacto = phonenumbers.parse(
                    telefono_contacto,
                    None
                )

                if not phonenumbers.is_valid_number(numero_contacto):
                    return {
                        "ok": False,
                        "campo": "telefono_contacto",
                        "error": "El teléfono del contacto no es válido."
                    }

            except phonenumbers.NumberParseException:
                return {
                    "ok": False,
                    "campo": "telefono_contacto",
                    "error": "Ingrese un teléfono de contacto válido."
                }


        correo_contacto = correo_contacto.strip().lower()

        if correo_contacto:

            if not re.fullmatch(correo_valido, correo_contacto):
                return {
                    "ok": False,
                    "campo": "correo_contacto",
                    "error": "Ingrese un correo de contacto válido."
                }

    

        return self.repository.registrar_proveedor(
            nombre,
            nit,
            tipo_empresa,
            descripcion,
            direccion,
            ciudad,
            telefono,
            correo,
            contrasena,
            nombre_contacto,
            telefono_contacto,
            correo_contacto
        )

