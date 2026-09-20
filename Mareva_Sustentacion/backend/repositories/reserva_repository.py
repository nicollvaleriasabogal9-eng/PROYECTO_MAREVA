from config.conexion import Conexion

import random
import string


class ReservaRepository:

    def __init__(self):

        self.conexion = Conexion().obtener_conexion()


    # =========================================================
    # CREAR RESERVA
    # =========================================================

    def crear_reserva(
        self,
        id_cliente,
        id_paquete,
        id_salida,
        fecha_viaje,
        cant_adultos,
        cant_menores,
        observaciones,
        acepta_no_reembolso,
        alergias,
        mascotas,
        plan,
        metodo_contacto,
        precio_total=None
    ):

        cursor = self.conexion.cursor()

        codigo_unico = self._generar_codigo()


        try:

            cursor.execute(
                """
                INSERT INTO reserva
                (
                    codigo_unico,
                    fecha_viaje,
                    cant_adultos,
                    cant_menores,
                    observaciones,
                    acepta_no_reembolso,
                    alergias,
                    mascotas,
                    plan,
                    metodo_contacto,
                    precio_total,
                    id_cliente,
                    id_paquete,
                    id_salida
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id_reserva
                """,
                (
                    codigo_unico,
                    fecha_viaje,
                    cant_adultos,
                    cant_menores,
                    observaciones,
                    acepta_no_reembolso,
                    alergias,
                    mascotas,
                    plan,
                    metodo_contacto,
                    precio_total,
                    id_cliente,
                    id_paquete,
                    id_salida
                )
            )


            id_reserva = cursor.fetchone()[0]


            self.conexion.commit()


            return {
                "ok": True,
                "id_reserva": id_reserva,
                "codigo_unico": codigo_unico
            }


        except Exception as e:

            self.conexion.rollback()


            print(
                "========== ERROR CREANDO RESERVA =========="
            )

            print(
                type(e).__name__
            )

            print(
                str(e)
            )

            print(
                "============================================"
            )


            return {
                "ok": False,
                "error": (
                    "No fue posible procesar la reserva. "
                    "Intenta de nuevo."
                )
            }


        finally:

            cursor.close()


    # =========================================================
    # SERVICIOS EXTRA
    # =========================================================

    def agregar_servicios_extra(
        self,
        id_reserva,
        ids_servicios_extra
    ):

        if not ids_servicios_extra:
            return


        cursor = self.conexion.cursor()


        try:

            for id_extra in ids_servicios_extra:

                cursor.execute(
                    """
                    INSERT INTO reserva_servicio_extra
                    (
                        id_reserva,
                        id_servicio_extra
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        id_reserva,
                        id_extra
                    )
                )


            self.conexion.commit()


        except Exception:

            self.conexion.rollback()

            raise


        finally:

            cursor.close()


    # =========================================================
    # VIAJEROS
    # =========================================================

    def agregar_viajeros(
        self,
        id_reserva,
        viajeros
    ):
        """
        viajeros:
        lista de diccionarios con:

        nombre
        apellido
        tipo_documento
        numero_documento
        idioma
        """

        if not viajeros:
            return


        cursor = self.conexion.cursor()


        try:

            for viajero in viajeros:

                cursor.execute(
                    """
                    INSERT INTO viajero_reserva
                    (
                        nombre,
                        apellido,
                        tipo_documento,
                        numero_documento,
                        idioma,
                        id_reserva
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        viajero["nombre"],
                        viajero["apellido"],
                        viajero["tipo_documento"],
                        viajero["numero_documento"],
                        viajero.get(
                            "idioma",
                            "Español"
                        ),
                        id_reserva
                    )
                )


            self.conexion.commit()


        except Exception:

            self.conexion.rollback()

            raise


        finally:

            cursor.close()


    # =========================================================
    # ÚLTIMA RESERVA DEL CLIENTE
    # =========================================================

    def obtener_ultima_reserva_cliente(
        self,
        id_cliente
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_reserva,
                    r.estado,
                    p.nombre,
                    r.fecha_viaje
                FROM reserva r
                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete
                WHERE r.id_cliente = %s
                ORDER BY r.id_reserva DESC
                LIMIT 1
                """,
                (id_cliente,)
            )


            fila = cursor.fetchone()


        finally:

            cursor.close()


        if not fila:
            return None


        return {
            "id_reserva": fila[0],
            "codigo_unico": fila[1],
            "fecha_reserva": fila[2],
            "estado": fila[3],
            "paquete_nombre": fila[4],
            "fecha_viaje": fila[5]
        }


    # =========================================================
    # LISTAR RESERVAS ADMIN
    # =========================================================

    def listar_reservas_admin(self):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_viaje,
                    r.estado,
                    c.nombre,
                    c.correo,
                    p.nombre,
                    r.reembolso_estado,
                    r.motivo_cancelacion,
                    COALESCE(r.precio_total, 0)
                FROM reserva r
                JOIN cliente c
                    ON c.id_cliente = r.id_cliente
                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete
                ORDER BY r.id_reserva DESC
                """
            )


            filas = cursor.fetchall()


            return [

                {
                    "id_reserva": fila[0],
                    "codigo_unico": fila[1],
                    "fecha_viaje": fila[2],
                    "estado": fila[3],
                    "cliente_nombre": fila[4],
                    "cliente_correo": fila[5],
                    "paquete_nombre": fila[6],
                    "reembolso_estado": fila[7],
                    "motivo_cancelacion": fila[8],
                    "precio_total": fila[9]
                }

                for fila in filas

            ]


        finally:

            cursor.close()


    # =========================================================
    # OBTENER VIAJEROS
    # =========================================================

    def obtener_viajeros_reserva(
        self,
        id_reserva
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    id_viajero,
                    nombre,
                    apellido,
                    tipo_documento,
                    numero_documento,
                    idioma
                FROM viajero_reserva
                WHERE id_reserva = %s
                ORDER BY id_viajero
                """,
                (id_reserva,)
            )


            filas = cursor.fetchall()


        finally:

            cursor.close()


        return [

            {
                "id_viajero": fila[0],
                "nombre": fila[1],
                "apellido": fila[2],
                "tipo_documento": fila[3],
                "numero_documento": fila[4],
                "idioma": fila[5]
            }

            for fila in filas

        ]


    # =========================================================
    # RESERVA DEL CLIENTE
    # =========================================================

    def obtener_reserva_cliente(
        self,
        id_reserva,
        id_cliente
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    id_reserva,
                    id_cliente,
                    estado
                FROM reserva
                WHERE id_reserva = %s
                  AND id_cliente = %s
                """,
                (
                    id_reserva,
                    id_cliente
                )
            )


            fila = cursor.fetchone()


        finally:

            cursor.close()


        if not fila:
            return None


        return {
            "id_reserva": fila[0],
            "id_cliente": fila[1],
            "estado": fila[2]
        }


    # =========================================================
    # RESERVA CON VIAJEROS
    # =========================================================

    def obtener_reserva_con_viajeros(
        self,
        id_reserva,
        id_cliente
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.estado,
                    p.nombre,
                    vr.id_viajero,
                    vr.nombre,
                    vr.apellido,
                    vr.tipo_documento,
                    vr.numero_documento,
                    vr.idioma
                FROM reserva r
                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete
                LEFT JOIN viajero_reserva vr
                    ON vr.id_reserva = r.id_reserva
                WHERE r.id_reserva = %s
                  AND r.id_cliente = %s
                ORDER BY vr.id_viajero
                """,
                (
                    id_reserva,
                    id_cliente
                )
            )


            filas = cursor.fetchall()


        finally:

            cursor.close()


        if not filas:
            return None


        reserva = {
            "id_reserva": filas[0][0],
            "codigo_unico": filas[0][1],
            "estado": filas[0][2],
            "paquete_nombre": filas[0][3],
            "viajeros": []
        }


        for fila in filas:

            if fila[4] is not None:

                reserva["viajeros"].append(
                    {
                        "id_viajero": fila[4],
                        "nombre": fila[5],
                        "apellido": fila[6],
                        "tipo_documento": fila[7],
                        "numero_documento": fila[8],
                        "idioma": fila[9]
                    }
                )


        return reserva


    # =========================================================
    # ACTUALIZAR VIAJERO
    # =========================================================

    def actualizar_viajero(
        self,
        id_viajero,
        id_cliente,
        nombre,
        apellido,
        tipo_documento,
        numero_documento
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                UPDATE viajero_reserva vr

                SET
                    nombre = %s,
                    apellido = %s,
                    tipo_documento = %s,
                    numero_documento = %s

                FROM reserva r

                WHERE vr.id_viajero = %s
                  AND vr.id_reserva = r.id_reserva
                  AND r.id_cliente = %s
                  AND r.estado IN (
                      'solicitada',
                      'pendiente a pago'
                  )
                """,
                (
                    nombre,
                    apellido,
                    tipo_documento,
                    numero_documento,
                    id_viajero,
                    id_cliente
                )
            )


            if cursor.rowcount == 0:

                self.conexion.rollback()

                return {
                    "ok": False,
                    "error": "No puedes modificar este viajero"
                }


            self.conexion.commit()


            return {
                "ok": True
            }


        except Exception as e:

            self.conexion.rollback()


            print(
                "ERROR ACTUALIZANDO VIAJERO:",
                e
            )


            return {
                "ok": False,
                "error": (
                    "No fue posible actualizar "
                    "la información del viajero."
                )
            }


        finally:

            cursor.close()


    # =========================================================
    # DATOS PARA ENCUESTA
    # =========================================================

    def obtener_datos_encuesta(
        self,
        id_reserva
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                SELECT
                    r.id_reserva,
                    r.estado,
                    c.id_cliente,
                    c.nombre,
                    c.correo
                FROM reserva r
                JOIN cliente c
                    ON c.id_cliente = r.id_cliente
                WHERE r.id_reserva = %s
                """,
                (id_reserva,)
            )


            fila = cursor.fetchone()


            if not fila:
                return None


            return {
                "id_reserva": fila[0],
                "estado": fila[1],
                "id_cliente": fila[2],
                "nombre": fila[3],
                "correo": fila[4]
            }


        finally:

            cursor.close()


    # =========================================================
    # MARCAR COMPLETADA
    # =========================================================

    def marcar_completada(
        self,
        id_reserva
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                UPDATE reserva

                SET estado = 'completada'

                WHERE id_reserva = %s
                  AND estado <> 'completada'

                RETURNING id_reserva
                """,
                (id_reserva,)
            )


            fila = cursor.fetchone()


            if not fila:

                self.conexion.rollback()

                return {
                    "ok": False,
                    "error": "No se pudo completar la reserva."
                }


            self.conexion.commit()


            return {
                "ok": True
            }


        except Exception as e:

            self.conexion.rollback()


            print(
                "ERROR COMPLETANDO RESERVA:",
                e
            )


            return {
                "ok": False,
                "error": (
                    "No fue posible completar la reserva."
                )
            }


        finally:

            cursor.close()


    # =========================================================
    # CÓDIGO DE RESERVA
    # =========================================================

    @staticmethod
    def _generar_codigo():

        return (
            "MRV-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=8
                )
            )
        )


    # =========================================================
    # REEMBOLSO
    # =========================================================

    def marcar_reembolso_realizado(
        self,
        id_reserva
    ):

        cursor = self.conexion.cursor()


        try:

            cursor.execute(
                """
                UPDATE reserva

                SET
                    reembolso_estado = 'realizado',
                    reembolso_fecha = CURRENT_TIMESTAMP

                WHERE id_reserva = %s
                  AND estado = 'cancelada'
                  AND reembolso_estado = 'pendiente'
                """,
                (id_reserva,)
            )


            ok = cursor.rowcount > 0


            self.conexion.commit()


            return ok


        except Exception:

            self.conexion.rollback()

            raise


        finally:

            cursor.close()


    def listar_reservas_cliente(self, id_cliente):

        cursor = self.conexion.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    r.id_reserva,
                    r.codigo_unico,
                    r.fecha_reserva,
                    r.fecha_viaje,
                    r.estado,
                    r.cant_adultos,
                    r.cant_menores,
                    COALESCE(r.precio_total, 0),
                    p.nombre,
                    d.nombre_destino,
                    s.fecha_salida,
                    s.fecha_regreso
                FROM reserva r

                JOIN paquete_turistico p
                    ON p.id_paquete = r.id_paquete

                LEFT JOIN destino d
                    ON d.id_destino = p.id_destino

                LEFT JOIN salida_paquete s
                    ON s.id_salida = r.id_salida

                WHERE r.id_cliente = %s

                ORDER BY
                    r.fecha_viaje DESC NULLS LAST,
                    r.id_reserva DESC
                """,
                (id_cliente,)
            )

            filas = cursor.fetchall()

        finally:
            cursor.close()

        return [
            {
                "id_reserva": fila[0],
                "codigo_unico": fila[1],
                "fecha_reserva": fila[2],
                "fecha_viaje": fila[3],
                "estado": fila[4],
                "cant_adultos": fila[5],
                "cant_menores": fila[6],
                "precio_total": fila[7],
                "paquete_nombre": fila[8],
                "destino": fila[9],
                "fecha_salida": fila[10],
                "fecha_regreso": fila[11],
            }
            for fila in filas
        ]