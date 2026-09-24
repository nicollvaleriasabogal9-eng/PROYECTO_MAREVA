from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from datetime import datetime
import re

from services.reserva_services import ReservaService
from services.paquete_services import PaqueteService
from services.pdf_services import PDFService
from repositories.salida_repository import SalidaRepository


class ReservaController:

    def __init__(self):

        self.service = ReservaService()

        self.paquete_service = PaqueteService()

        self.pdf_service = PDFService()

        self.salida_repository = SalidaRepository()

    # =========================================================
    # LISTAR RESERVAS ADMIN
    # =========================================================

    def listar_reservas_admin(self):

        try:

            reservas = self.service.listar_reservas_admin()

            return render_template(
                "admin/reservas.html",
                reservas=reservas,
                error=None
            )

        except Exception as e:

            print(
                "ERROR LISTAR RESERVAS ADMIN:",
                e
            )

            return render_template(
                "admin/reservas.html",
                reservas=[],
                error="No fue posible cargar las reservas."
            )

    # =========================================================
    # PREPARAR RESERVA
    # =========================================================

    def preparar_reserva(self, slug):

        paquete = self.paquete_service.obtener_detalle(
            slug
        )

        if not paquete:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        id_salida = request.form.get(
            "id_salida",
            ""
        ).strip()

        if not id_salida:

            return redirect(
                url_for(
                    "paquetes.ver_detalle",
                    slug=slug,
                    error="Debes seleccionar una fecha de salida."
                )
            )

        try:

            id_salida = int(id_salida)

        except (ValueError, TypeError):

            return redirect(
                url_for(
                    "paquetes.ver_detalle",
                    slug=slug,
                    error="La fecha seleccionada no es válida."
                )
            )

        salida = self.salida_repository.obtener_por_id(
            id_salida
        )

        if (
            not salida
            or salida["id_paquete"] != paquete["id_paquete"]
            or salida["estado"] not in (
                "programada",
                "disponible"
            )
        ):

            return redirect(
                url_for(
                    "paquetes.ver_detalle",
                    slug=slug,
                    error="La fecha seleccionada ya no está disponible."
                )
            )

        def _ids(campo):

            resultado = []

            for valor in request.form.getlist(campo):

                try:

                    resultado.append(
                        int(valor)
                    )

                except (ValueError, TypeError):

                    continue

            return resultado

        ids_seguros = set(
            _ids("seguros")
        )

        for seguro in paquete.get(
            "seguros",
            []
        ):

            if seguro.get(
                "es_obligatorio"
            ):

                ids_seguros.add(
                    seguro.get(
                        "id_seguro"
                    )
                )

        seleccion = {

            "slug": slug,

            "id_salida": id_salida,

            "fecha_viaje": salida["fecha_salida"],

            "fecha_regreso": salida["fecha_regreso"],

            "alojamiento": _ids(
                "alojamiento"
            ),

            "alimentacion": _ids(
                "alimentacion"
            ),

            "transporte": _ids(
                "transporte"
            ),

            "actividades": _ids(
                "actividades"
            ),

            "seguros": sorted(
                ids_seguros
            ),

            "extras": _ids(
                "extras"
            ),
        }

        session["seleccion_reserva"] = seleccion

        if not session.get("usuario"):

            return redirect(
                url_for(
                    "auth.mostrar_login",
                    next=f"/reserva/confirmar/{slug}"
                )
            )

        return redirect(
            url_for(
                "reserva.confirmar_reserva",
                slug=slug
            )
        )

    # =========================================================
    # MOSTRAR FORMULARIO
    # =========================================================

    def mostrar_formulario(self, slug):

        paquete = (
            self.paquete_service.obtener_detalle(
                slug
            )
        )

        if not paquete:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        salidas = (
            self.salida_repository.obtener_por_paquete(
                paquete["id_paquete"],
                solo_disponibles=True
            )
        )

        return render_template(
            "cliente/reserva.html",
            paquete=paquete,
            salidas=salidas
        )

    # =========================================================
    # CONFIRMAR RESERVA
    # =========================================================

    def confirmar(self, slug):

        usuario = session.get("usuario")

        if not usuario:

            return redirect(
                url_for(
                    "auth.mostrar_login",
                    next=f"/reserva/{slug}"
                )
            )

        paquete = (
            self.paquete_service.obtener_detalle(
                slug
            )
        )

        if not paquete:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        id_salida = (
            request.form
            .get(
                "id_salida",
                ""
            )
            .strip()
        )

        if not id_salida:

            salidas = (
                self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                )
            )

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=salidas,
                error=(
                    "Debes seleccionar una fecha "
                    "de salida."
                )
            )

        try:

            id_salida = int(id_salida)

        except (ValueError, TypeError):

            salidas = (
                self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                )
            )

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=salidas,
                error=(
                    "La fecha seleccionada "
                    "no es válida."
                )
            )

        salida = (
            self.salida_repository.obtener_por_id(
                id_salida
            )
        )

        if not salida:

            salidas = (
                self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                )
            )

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=salidas,
                error=(
                    "La salida seleccionada "
                    "no existe."
                )
            )

        if salida["id_paquete"] != paquete["id_paquete"]:

            salidas = (
                self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                )
            )

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=salidas,
                error=(
                    "La fecha seleccionada "
                    "no pertenece a este paquete."
                )
            )

        if salida["estado"] not in (
            "programada",
            "disponible"
        ):

            salidas = (
                self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                )
            )

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=salidas,
                error=(
                    "La fecha seleccionada "
                    "ya no está disponible."
                )
            )

        fecha_viaje = salida["fecha_salida"]

        # -----------------------------------------------------
        # CANTIDAD DE VIAJEROS
        # -----------------------------------------------------

        try:

            adultos = max(
                1,
                int(
                    request.form.get(
                        "adultos",
                        "1"
                    )
                )
            )

            menores = max(
                0,
                int(
                    request.form.get(
                        "menores",
                        "0"
                    )
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=(
                    "La cantidad de viajeros "
                    "no es válida."
                )
            )

        total_personas = adultos + menores

        if total_personas < 1:

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=(
                    "Debes ingresar al menos "
                    "un viajero."
                )
            )

        # -----------------------------------------------------
        # DATOS GENERALES
        # -----------------------------------------------------

        alergias = (
            request.form
            .get(
                "alergias",
                ""
            )
            .strip()
        )

        observaciones = (
            request.form
            .get(
                "observaciones",
                ""
            )
            .strip()
        )

        plan = (
            request.form
            .get(
                "plan",
                "completo"
            )
            .strip()
        )

        mascotas = (
            request.form
            .get(
                "mascotas",
                "no"
            )
            .strip()
            .lower()
            == "si"
        )

        metodo_contacto = (
            request.form
            .get(
                "metodo_contacto",
                "correo"
            )
            .strip()
        )

        acepta = usuario.get(
            "acepta_politica_no_reembolso",
            False
        )

        if not acepta:

            acepta = (
                request.form
                .get(
                    "acepta_no_reembolso"
                )
                == "1"
            )

        if not acepta:

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=(
                    "Debes aceptar la política "
                    "de no reembolso."
                )
            )

        # -----------------------------------------------------
        # VIAJEROS
        # -----------------------------------------------------

        nombres = request.form.getlist(
            "viajero_nombre[]"
        )

        apellidos = request.form.getlist(
            "viajero_apellido[]"
        )

        tipos = request.form.getlist(
            "viajero_tipo_documento[]"
        )

        documentos = request.form.getlist(
            "viajero_documento[]"
        )

        idiomas = request.form.getlist(
            "viajero_idioma[]"
        )

        if (
            len(nombres) != total_personas
            or len(apellidos) != total_personas
            or len(tipos) != total_personas
            or len(documentos) != total_personas
            or len(idiomas) != total_personas
        ):

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=(
                    "Debes completar los datos "
                    "de todos los viajeros."
                )
            )

        viajeros = []

        for i in range(total_personas):

            nombre = nombres[i].strip()

            apellido = apellidos[i].strip()

            tipo = tipos[i].strip()

            documento = documentos[i].strip()

            idioma = idiomas[i].strip()

            if (
                not nombre
                or not apellido
                or not tipo
                or not documento
                or not idioma
            ):

                return render_template(
                    "cliente/reserva.html",
                    paquete=paquete,
                    salidas=self.salida_repository.obtener_por_paquete(
                        paquete["id_paquete"],
                        solo_disponibles=True
                    ),
                    error=(
                        f"Completa los datos "
                        f"del viajero {i + 1}."
                    )
                )

            viajeros.append(
                {
                    "nombre": nombre,
                    "apellido": apellido,
                    "tipo_documento": tipo,
                    "numero_documento": documento,
                    "idioma": idioma
                }
            )

        # -----------------------------------------------------
        # SERVICIOS EXTRA
        # -----------------------------------------------------

        extras_ids = []

        for extra in request.form.getlist(
            "extras"
        ):

            try:

                extras_ids.append(
                    int(extra)
                )

            except (ValueError, TypeError):

                continue

        # -----------------------------------------------------
        # CLIENTE
        # -----------------------------------------------------

        id_cliente = (
            usuario.get("id")
            or usuario.get("id_cliente")
        )

        # -----------------------------------------------------
        # VALOR REFERENCIAL
        # -----------------------------------------------------

        try:

            precio = float(
                paquete.get(
                    "precio",
                    0
                ) or 0
            )

        except (ValueError, TypeError):

            precio = 0

        valor_referencial = (
            precio * total_personas
        )

        # -----------------------------------------------------
        # DATOS DE RESERVA
        # -----------------------------------------------------

        resultado = (
            self.service.confirmar_reserva(

                id_cliente=id_cliente,

                id_paquete=paquete[
                    "id_paquete"
                ],

                id_salida=id_salida,

                fecha_viaje=fecha_viaje,

                cant_adultos=adultos,

                cant_menores=menores,

                observaciones=observaciones,

                acepta_no_reembolso=acepta,

                alergias=alergias,

                mascotas=mascotas,

                plan=plan,

                metodo_contacto=metodo_contacto,

                extras_ids=extras_ids,

                viajeros=viajeros,

                precio_total=valor_referencial
            )
        )

        if not resultado:

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=(
                    "No fue posible registrar "
                    "la reserva."
                )
            )

        if not resultado.get("ok"):

            return render_template(
                "cliente/reserva.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                error=resultado.get(
                    "error",
                    "No fue posible registrar "
                    "la reserva."
                )
            )

        # -----------------------------------------------------
        # DETALLE PARA CONFIRMACIÓN
        # -----------------------------------------------------

        detalle = resultado.copy()

        detalle.update(
            {
                "paquete": paquete,

                "id_salida": id_salida,

                "fecha_viaje": fecha_viaje,

                "fecha_regreso": (
                    salida["fecha_regreso"]
                ),

                "cant_adultos": adultos,

                "cant_menores": menores,

                "total_personas": total_personas,

                "valor_referencial":
                    valor_referencial,

                "viajeros": viajeros,

                "estado":
                    detalle.get(
                        "estado",
                        "solicitada"
                    ),

                "pago_directo": True
            }
        )

        session["detalle_reserva"] = detalle

        return redirect(
            url_for(
                "reserva.confirmacion"
            )
        )

    # =========================================================
    # CONFIRMACIÓN EDITABLE
    # =========================================================

    def mostrar_confirmacion_reserva(self, slug):

        if not session.get("usuario"):

            return redirect(
                url_for(
                    "auth.mostrar_login",
                    next=f"/reserva/confirmar/{slug}"
                )
            )

        paquete = (
            self.paquete_service.obtener_detalle(
                slug
            )
        )

        if not paquete:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        seleccion = session.get(
            "seleccion_reserva"
        )

        if (
            not seleccion
            or seleccion.get("slug") != slug
        ):

            return redirect(
                url_for(
                    "paquetes.ver_detalle",
                    slug=slug
                )
            )

        salidas = (
            self.salida_repository.obtener_por_paquete(
                paquete["id_paquete"],
                solo_disponibles=True
            )
        )

        salida = (
            self.salida_repository.obtener_por_id(
                seleccion["id_salida"]
            )
        )

        return render_template(
            "cliente/reserva_confirmar.html",
            paquete=paquete,
            salidas=salidas,
            salida=salida,
            seleccion=seleccion
        )

    # =========================================================
    # GUARDAR RESERVA
    # =========================================================

    def guardar_reserva(self, slug):

        usuario = session.get("usuario")

        if not usuario:

            return redirect(
                url_for(
                    "auth.mostrar_login",
                    next=f"/reserva/confirmar/{slug}"
                )
            )

        paquete = (
            self.paquete_service.obtener_detalle(
                slug
            )
        )

        if not paquete:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        seleccion = session.get(
            "seleccion_reserva"
        )

        if (
            not seleccion
            or seleccion.get("slug") != slug
        ):

            return redirect(
                url_for(
                    "paquetes.ver_detalle",
                    slug=slug
                )
            )

        seleccion = self._leer_seleccion_form(
            seleccion,
            paquete=paquete
        )

        session["seleccion_reserva"] = seleccion

        id_form = (
            request.form
            .get(
                "id_salida",
                ""
            )
            .strip()
        )

        if id_form.isdigit():

            id_salida = int(id_form)

        else:

            id_salida = seleccion["id_salida"]

        salida = (
            self.salida_repository.obtener_por_id(
                id_salida
            )
        )

        if (
            not salida
            or salida["id_paquete"] != paquete["id_paquete"]
            or salida["estado"] not in (
                "programada",
                "disponible"
            )
        ):

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=self.salida_repository.obtener_por_id(
                    seleccion["id_salida"]
                ),
                seleccion=seleccion,
                error=(
                    "La fecha seleccionada "
                    "ya no está disponible."
                )
            )

        fecha_viaje = salida["fecha_salida"]

        # -----------------------------------------------------
        # CANTIDAD DE VIAJEROS
        # -----------------------------------------------------

        try:

            adultos = max(
                1,
                int(
                    request.form.get(
                        "adultos",
                        "1"
                    )
                )
            )

            menores = max(
                0,
                int(
                    request.form.get(
                        "menores",
                        "0"
                    )
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=salida,
                seleccion=seleccion,
                error=(
                    "La cantidad de viajeros "
                    "no es válida."
                )
            )

        total_personas = (
            adultos + menores
        )

        if total_personas < 1:

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=salida,
                seleccion=seleccion,
                error=(
                    "Debes ingresar al menos "
                    "un viajero."
                )
            )

        # -----------------------------------------------------
        # DATOS GENERALES
        # -----------------------------------------------------

        alergias = (
            request.form
            .get(
                "alergias",
                ""
            )
            .strip()
        )

        observaciones = (
            request.form
            .get(
                "observaciones",
                ""
            )
            .strip()
        )

        plan = (
            request.form
            .get(
                "plan",
                "completo"
            )
            .strip()
        )

        mascotas = (
            request.form
            .get(
                "mascotas",
                "no"
            )
            .strip()
            .lower()
            == "si"
        )

        metodo_contacto = (
            request.form
            .get(
                "metodo_contacto",
                "correo"
            )
            .strip()
        )

        acepta = usuario.get(
            "acepta_politica_no_reembolso",
            False
        )

        if not acepta:

            acepta = (
                request.form
                .get(
                    "acepta_no_reembolso"
                )
                == "1"
            )

        if not acepta:

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=salida,
                seleccion=seleccion,
                error=(
                    "Debes aceptar la política "
                    "de no reembolso."
                )
            )

        # -----------------------------------------------------
        # VIAJEROS
        # -----------------------------------------------------

        nombres = request.form.getlist(
            "viajero_nombre[]"
        )

        apellidos = request.form.getlist(
            "viajero_apellido[]"
        )

        tipos = request.form.getlist(
            "viajero_tipo_documento[]"
        )

        documentos = request.form.getlist(
            "viajero_documento[]"
        )

        idiomas = request.form.getlist(
            "viajero_idioma[]"
        )

        if (
            len(nombres) != total_personas
            or len(apellidos) != total_personas
            or len(tipos) != total_personas
            or len(documentos) != total_personas
            or len(idiomas) != total_personas
        ):

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=salida,
                seleccion=seleccion,
                error=(
                    "Debes completar los datos "
                    "de todos los viajeros."
                )
            )

        viajeros = []

        for i in range(total_personas):

            nombre = nombres[i].strip()

            apellido = apellidos[i].strip()

            tipo = tipos[i].strip()

            documento = documentos[i].strip()

            idioma = idiomas[i].strip()

            if not (
                nombre
                and apellido
                and tipo
                and documento
                and idioma
            ):

                return render_template(
                    "cliente/reserva_confirmar.html",
                    paquete=paquete,
                    salidas=self.salida_repository.obtener_por_paquete(
                        paquete["id_paquete"],
                        solo_disponibles=True
                    ),
                    salida=salida,
                    seleccion=seleccion,
                    error=(
                        f"Completa los datos "
                        f"del viajero {i + 1}."
                    )
                )

            viajeros.append(
                {
                    "nombre": nombre,
                    "apellido": apellido,
                    "tipo_documento": tipo,
                    "numero_documento": documento,
                    "idioma": idioma
                }
            )

        # -----------------------------------------------------
        # SERVICIOS EXTRA
        # -----------------------------------------------------

        extras_ids = [
            int(extra)
            for extra in request.form.getlist(
                "extras"
            )
            if extra.isdigit()
        ]

        id_cliente = (
            usuario.get("id")
            or usuario.get("id_cliente")
        )

        # -----------------------------------------------------
        # VALOR REFERENCIAL
        # -----------------------------------------------------

        try:

            precio = float(
                paquete.get(
                    "precio",
                    0
                ) or 0
            )

        except (ValueError, TypeError):

            precio = 0

        valor_referencial = (
            precio * total_personas
        )

        precio_total = (
            ReservaController._calcular_precio_total(
                paquete,
                seleccion,
                total_personas
            )
        )

        # -----------------------------------------------------
        # PERSONALIZACIÓN
        # -----------------------------------------------------

        personalizacion = (
            self._construir_personalizacion(
                paquete,
                seleccion
            )
        )

        if observaciones:

            personalizacion = (
                personalizacion
                + "\nSolicitudes especiales: "
                + observaciones
            )

        # -----------------------------------------------------
        # CREAR RESERVA
        # -----------------------------------------------------

        resultado = (
            self.service.confirmar_reserva(

                id_cliente=id_cliente,

                id_paquete=paquete[
                    "id_paquete"
                ],

                id_salida=id_salida,

                fecha_viaje=fecha_viaje,

                cant_adultos=adultos,

                cant_menores=menores,

                observaciones=personalizacion,

                acepta_no_reembolso=acepta,

                alergias=alergias,

                mascotas=mascotas,

                plan=plan,

                metodo_contacto=metodo_contacto,

                extras_ids=extras_ids,

                viajeros=viajeros,

                precio_total=precio_total
            )
        )

        if not resultado or not resultado.get("ok"):

            return render_template(
                "cliente/reserva_confirmar.html",
                paquete=paquete,
                salidas=self.salida_repository.obtener_por_paquete(
                    paquete["id_paquete"],
                    solo_disponibles=True
                ),
                salida=salida,
                seleccion=seleccion,
                error=(
                    resultado.get(
                        "error",
                        "No fue posible registrar "
                        "la reserva."
                    )
                    if resultado
                    else
                    "No fue posible registrar "
                    "la reserva."
                )
            )

        # -----------------------------------------------------
        # DETALLE PARA CONFIRMACIÓN
        # -----------------------------------------------------

        obj_extras = self._resolver_items(
            paquete,
            extras_ids
        )

        detalle = resultado.copy()

        detalle.update(
            {
                "paquete": paquete,

                "id_salida": id_salida,

                "fecha_viaje": fecha_viaje,

                "fecha_regreso": (
                    salida["fecha_regreso"]
                ),

                "cant_adultos": adultos,

                "cant_menores": menores,

                "total_personas": total_personas,

                "valor_referencial":
                    valor_referencial,

                "precio_total":
                    precio_total,

                "viajeros":
                    viajeros,

                "paquete_nombre":
                    paquete["nombre"],

                "destino":
                    paquete.get(
                        "nombre_destino",
                        ""
                    ),

                "duracion":
                    (
                        f"{paquete.get('duracion_dias', 0)} "
                        f"días · "
                        f"{paquete.get('duracion_noches', 0)} "
                        f"noches"
                    ),

                "adultos":
                    adultos,

                "menores":
                    menores,

                "extras":
                    obj_extras,

                "alojamientos":
                    self._seleccionados_alojamientos(
                        paquete,
                        seleccion
                    ),

                "alimentacion":
                    self._seleccionados_alimentacion(
                        paquete,
                        seleccion
                    ),

                "transportes":
                    self._seleccionados_transportes(
                        paquete,
                        seleccion
                    ),

                "actividades":
                    self._seleccionados_actividades(
                        paquete,
                        seleccion
                    ),

                "seguros":
                    self._seleccionados_seguros(
                        paquete,
                        seleccion
                    ),

                "personalizacion":
                    personalizacion,

                "notas":
                    observaciones,

                "alergias":
                    alergias,

                "estado":
                    detalle.get(
                        "estado",
                        "solicitada"
                    ),

                "pago_directo":
                    True
            }
        )

        session["detalle_reserva"] = detalle

        session.pop(
            "seleccion_reserva",
            None
        )

        # Limpia cualquier simulación anterior
        # para esta nueva reserva.
        session.pop(
            "pago_simulado",
            None
        )

        return redirect(
            url_for(
                "reserva.confirmacion"
            )
        )

    # =========================================================
    # HELPERS DE SELECCIÓN
    # =========================================================

    @staticmethod
    def _ids_form(campo):

        resultado = []

        for valor in request.form.getlist(campo):

            try:

                resultado.append(
                    int(valor)
                )

            except (ValueError, TypeError):

                continue

        return resultado

    def _leer_seleccion_form(
        self,
        base,
        paquete=None
    ):

        seleccion = dict(base)

        seleccion.update(
            {
                "alojamiento":
                    self._ids_form(
                        "alojamiento"
                    ),

                "alimentacion":
                    self._ids_form(
                        "alimentacion"
                    ),

                "transporte":
                    self._ids_form(
                        "transporte"
                    ),

                "actividades":
                    self._ids_form(
                        "actividades"
                    ),

                "seguros":
                    self._ids_form(
                        "seguros"
                    ),

                "extras":
                    self._ids_form(
                        "extras"
                    ),
            }
        )

        if paquete:

            ids = set(
                seleccion["seguros"]
            )

            for seguro in paquete.get(
                "seguros",
                []
            ):

                if seguro.get(
                    "es_obligatorio"
                ):

                    ids.add(
                        seguro.get(
                            "id_seguro"
                        )
                    )

            seleccion["seguros"] = sorted(
                ids
            )

        return seleccion

    @staticmethod
    def _resolver_items(
        paquete,
        ids
    ):

        disponibles = paquete.get(
            "servicios_extra",
            []
        )

        return [
            item
            for item in disponibles
            if item.get("id") in ids
        ]

    @staticmethod
    def _seleccionados_alojamientos(
        paquete,
        seleccion
    ):

        return [
            item
            for item in paquete.get(
                "alojamientos",
                []
            )
            if item.get(
                "id_alojamiento"
            ) in seleccion.get(
                "alojamiento",
                []
            )
        ]

    @staticmethod
    def _seleccionados_alimentacion(
        paquete,
        seleccion
    ):

        return [
            item
            for item in paquete.get(
                "alimentacion",
                []
            )
            if item.get(
                "id_alimentacion"
            ) in seleccion.get(
                "alimentacion",
                []
            )
        ]

    @staticmethod
    def _seleccionados_transportes(
        paquete,
        seleccion
    ):

        return [
            item
            for item in paquete.get(
                "transportes",
                []
            )
            if item.get(
                "id_transporte"
            ) in seleccion.get(
                "transporte",
                []
            )
        ]

    @staticmethod
    def _seleccionados_actividades(
        paquete,
        seleccion
    ):

        return [
            item
            for item in paquete.get(
                "actividades",
                []
            )
            if item.get(
                "id_actividad"
            ) in seleccion.get(
                "actividades",
                []
            )
        ]

    @staticmethod
    def _seleccionados_seguros(
        paquete,
        seleccion
    ):

        return [
            item
            for item in paquete.get(
                "seguros",
                []
            )
            if item.get(
                "id_seguro"
            ) in seleccion.get(
                "seguros",
                []
            )
        ]

    @staticmethod
    def _construir_personalizacion(
        paquete,
        seleccion
    ):

        lineas = []

        alojamientos = (
            ReservaController
            ._seleccionados_alojamientos(
                paquete,
                seleccion
            )
        )

        if alojamientos:

            lineas.append(
                "Alojamiento: "
                + ", ".join(
                    a["nombre"]
                    for a in alojamientos
                )
            )

        alimentacion = (
            ReservaController
            ._seleccionados_alimentacion(
                paquete,
                seleccion
            )
        )

        if alimentacion:

            lineas.append(
                "Alimentación: "
                + ", ".join(
                    a["restaurante"]
                    for a in alimentacion
                )
            )

        transportes = (
            ReservaController
            ._seleccionados_transportes(
                paquete,
                seleccion
            )
        )

        if transportes:

            lineas.append(
                "Transporte: "
                + ", ".join(
                    f"{t['empresa']} ({t['tipo']})"
                    for t in transportes
                )
            )

        actividades = (
            ReservaController
            ._seleccionados_actividades(
                paquete,
                seleccion
            )
        )

        if actividades:

            lineas.append(
                "Actividades: "
                + ", ".join(
                    a["nombre"]
                    for a in actividades
                )
            )

        seguros = (
            ReservaController
            ._seleccionados_seguros(
                paquete,
                seleccion
            )
        )

        if seguros:

            lineas.append(
                "Seguro: "
                + ", ".join(
                    s["nombre"]
                    for s in seguros
                )
            )

        extras = (
            ReservaController
            ._resolver_items(
                paquete,
                seleccion.get(
                    "extras",
                    []
                )
            )
        )

        if extras:

            lineas.append(
                "Servicios extra: "
                + ", ".join(
                    e["nombre"]
                    for e in extras
                )
            )

        if not lineas:

            lineas.append(
                "Composición estándar del paquete."
            )

        return "\n".join(lineas)

    @staticmethod
    def _calcular_precio_total(
        paquete,
        seleccion,
        total_personas
    ):

        try:

            base = float(
                paquete.get(
                    "precio",
                    0
                ) or 0
            )

        except (ValueError, TypeError):

            base = 0

        for item in (
            ReservaController
            ._seleccionados_alimentacion(
                paquete,
                seleccion
            )
        ):

            base += float(
                item.get(
                    "precio",
                    0
                ) or 0
            )

        for item in (
            ReservaController
            ._seleccionados_actividades(
                paquete,
                seleccion
            )
        ):

            base += float(
                item.get(
                    "costo",
                    0
                ) or 0
            )

        for item in (
            ReservaController
            ._seleccionados_seguros(
                paquete,
                seleccion
            )
        ):

            base += float(
                item.get(
                    "precio",
                    0
                ) or 0
            )

        for item in (
            ReservaController
            ._resolver_items(
                paquete,
                seleccion.get(
                    "extras",
                    []
                )
            )
        ):

            base += float(
                item.get(
                    "precio",
                    0
                ) or 0
            )

        return round(
            base * total_personas,
            2
        )

    # =========================================================
    # CONFIRMACIÓN
    # =========================================================

    def mostrar_confirmacion(self):

        detalle = session.get(
            "detalle_reserva"
        )

        if not detalle:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        return render_template(
            "principal/reserva_confirmada.html",
            reserva=detalle,
            detalle=detalle
        )

    # =========================================================
    # PAGO SIMULADO
    # =========================================================

    def mostrar_pago(self):

        if not session.get("usuario"):

            return redirect(
                url_for(
                    "auth.mostrar_login"
                )
            )

        detalle = session.get(
            "detalle_reserva"
        )

        if not detalle:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        pago = session.get(
            "pago_simulado"
        )

        if (
            pago
            and pago.get("realizado")
        ):

            return redirect(
                url_for(
                    "reserva.pago_exitoso"
                )
            )

        return render_template(
            "cliente/pago.html",
            reserva=detalle,
            error=None
        )

    # =========================================================
    # PROCESAR PAGO SIMULADO
    # =========================================================

    def procesar_pago(self):

        if not session.get("usuario"):

            return redirect(
                url_for(
                    "auth.mostrar_login"
                )
            )

        detalle = session.get(
            "detalle_reserva"
        )

        if not detalle:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        pago_anterior = session.get(
            "pago_simulado"
        )

        if (
            pago_anterior
            and pago_anterior.get("realizado")
        ):

            return redirect(
                url_for(
                    "reserva.pago_exitoso"
                )
            )

        metodo = (
            request.form
            .get(
                "metodo_pago",
                ""
            )
            .strip()
            .lower()
        )

        metodos_validos = {
            "nequi",
            "pse",
            "tarjeta"
        }

        if metodo not in metodos_validos:

            return render_template(
                "cliente/pago.html",
                reserva=detalle,
                error=(
                    "Debes seleccionar "
                    "un método de pago válido."
                )
            )

        # =====================================================
        # NEQUI
        # =====================================================

        if metodo == "nequi":

            telefono = (
                request.form
                .get(
                    "nequi_telefono",
                    ""
                )
                .strip()
            )

            if not telefono:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes ingresar "
                        "el número de celular."
                    )
                )

            if not telefono.isdigit():

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El número de Nequi "
                        "solo debe contener números."
                    )
                )

            if len(telefono) != 10:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El número de Nequi "
                        "debe tener exactamente 10 dígitos."
                    )
                )

            if not telefono.startswith("3"):

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El número de Nequi "
                        "debe comenzar por 3."
                    )
                )

        # =====================================================
        # PSE
        # =====================================================

        elif metodo == "pse":

            banco = (
                request.form
                .get(
                    "pse_banco",
                    ""
                )
                .strip()
            )

            tipo_documento = (
                request.form
                .get(
                    "pse_tipo_documento",
                    ""
                )
                .strip()
                .upper()
            )

            documento = (
                request.form
                .get(
                    "pse_documento",
                    ""
                )
                .strip()
            )

            bancos_validos = {
                "Bancolombia",
                "Davivienda",
                "Banco de Bogotá",
                "BBVA",
                "Banco de Occidente"
            }

            tipos_validos = {
                "CC",
                "CE",
                "TI",
                "NIT"
            }

            if banco not in bancos_validos:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes seleccionar "
                        "un banco válido."
                    )
                )

            if tipo_documento not in tipos_validos:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes seleccionar "
                        "un tipo de documento válido."
                    )
                )

            if not documento:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes ingresar "
                        "el número de documento."
                    )
                )

            if not documento.isdigit():

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El documento debe contener "
                        "solo números."
                    )
                )

            if not (
                6 <= len(documento) <= 12
            ):

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El documento debe tener "
                        "entre 6 y 12 dígitos."
                    )
                )

        # =====================================================
        # TARJETA
        # =====================================================

        elif metodo == "tarjeta":

            numero = (
                request.form
                .get(
                    "tarjeta_numero",
                    ""
                )
                .replace(
                    " ",
                    ""
                )
                .strip()
            )

            titular = (
                request.form
                .get(
                    "tarjeta_titular",
                    ""
                )
                .strip()
            )

            vencimiento = (
                request.form
                .get(
                    "tarjeta_vencimiento",
                    ""
                )
                .strip()
            )

            cvv = (
                request.form
                .get(
                    "tarjeta_cvv",
                    ""
                )
                .strip()
            )

            if not numero:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes ingresar "
                        "el número de tarjeta."
                    )
                )

            if not numero.isdigit():

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El número de tarjeta "
                        "solo debe contener números."
                    )
                )

            if len(numero) != 16:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El número de tarjeta "
                        "debe tener exactamente 16 dígitos."
                    )
                )

            if not titular:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes ingresar "
                        "el nombre del titular."
                    )
                )

            if len(titular) < 3:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El nombre del titular "
                        "no es válido."
                    )
                )

            # -------------------------------------------------
            # VENCIMIENTO
            # -------------------------------------------------

            if not re.fullmatch(
                r"(0[1-9]|1[0-2])/[0-9]{2}",
                vencimiento
            ):

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El vencimiento debe tener "
                        "el formato MM/AA."
                    )
                )

            mes = int(
                vencimiento[:2]
            )

            anio = int(
                vencimiento[3:]
            )

            anio_completo = 2000 + anio

            fecha_actual = datetime.now()

            if (
                anio_completo < fecha_actual.year
                or (
                    anio_completo == fecha_actual.year
                    and mes < fecha_actual.month
                )
            ):

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "La tarjeta está vencida."
                    )
                )

            # -------------------------------------------------
            # CVV
            # -------------------------------------------------

            if not cvv:

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "Debes ingresar "
                        "el CVV."
                    )
                )

            if not cvv.isdigit():

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El CVV solo debe contener números."
                    )
                )

            if len(cvv) not in (3, 4):

                return render_template(
                    "cliente/pago.html",
                    reserva=detalle,
                    error=(
                        "El CVV debe tener "
                        "3 o 4 dígitos."
                    )
                )

        # =====================================================
        # PAGO SIMULADO EXITOSO
        # =====================================================
        #
        # IMPORTANTE:
        # No se guardan:
        # - número de tarjeta
        # - CVV
        # - documento
        # - teléfono
        # - banco
        # - datos del titular
        #
        # Solo se guarda el resultado de la simulación.
        # =====================================================

        session["pago_simulado"] = {
            "realizado": True,
            "metodo": metodo.capitalize()
        }

        return redirect(
            url_for(
                "reserva.pago_exitoso"
            )
        )

    # =========================================================
    # PDF
    # =========================================================

    def descargar_pdf(self):

        detalle = session.get(
            "detalle_reserva"
        )

        if not detalle:

            return redirect(
                url_for(
                    "paquetes.listar_catalogo"
                )
            )

        return self.pdf_service.generar_resumen_reserva(
            detalle
        )

    # =========================================================
    # RESERVAS CLIENTE
    # =========================================================

    def listar_reservas_cliente(
        self,
        id_cliente
    ):

        return self.repo.listar_reservas_cliente(
            id_cliente
        )