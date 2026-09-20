"""
Este script corrige las contraseñas de los usuarios que se cargaron
con el INSERT inicial (INSERT INTO usuario ... VALUES ('Admin_mareva01', ...)).
Esas contraseñas se guardaron en texto plano, pero el login del sistema
compara contra un hash (werkzeug), así que con ellas el login SIEMPRE
va a fallar con "contraseña incorrecta" hasta que se corran este script.

Es seguro ejecutarlo varias veces: si una contraseña ya está hasheada,
el script la deja tal cual.

Uso (desde la raíz del proyecto, con el entorno virtual activado):
    cd backend
    python ../database/hashear_passwords.py
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from werkzeug.security import generate_password_hash
from config.conexion import Conexion


def parece_hash(valor):
    return valor.startswith("pbkdf2:") or valor.startswith("scrypt:")


def main():
    conexion = Conexion.obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id_usuario, correo, contrasena FROM usuario")
    usuarios = cursor.fetchall()

    actualizados = 0

    for id_usuario, correo, contrasena in usuarios:
        if parece_hash(contrasena):
            continue

        nuevo_hash = generate_password_hash(contrasena)

        cursor.execute(
            "UPDATE usuario SET contrasena = %s WHERE id_usuario = %s",
            (nuevo_hash, id_usuario),
        )

        print(f"Hasheada la contraseña de: {correo}")
        actualizados += 1

    conexion.commit()
    cursor.close()
    conexion.close()

    print(f"\nListo. {actualizados} contraseña(s) actualizada(s).")
    print("Las contraseñas para iniciar sesión siguen siendo las mismas")
    print("del INSERT original (por ejemplo: Admin_mareva01, cliente_pass1, etc).")


if __name__ == "__main__":
    main()
