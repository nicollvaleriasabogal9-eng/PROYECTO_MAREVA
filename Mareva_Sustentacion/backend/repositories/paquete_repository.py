from config.conexion import Conexion


COLUMNAS_PAQUETE = [
    "id_paquete",
    "nombre",
    "slug",
    "descripcion",
    "precio",
    "duracion_dias",
    "duracion_noches",
    "cupos_totales",
    "cupos_disponibles",
    "fecha_inicio",
    "fecha_fin",
    "imagen_url",
    "estado",
    "id_destino",
    "id_guia",
    "categoria",
    "nombre_destino",
    "departamento",
    "emoji",
]


QUERY_BASE = """
    SELECT
        p.id_paquete,
        p.nombre,
        p.slug,
        p.descripcion,
        p.precio,
        p.duracion_dias,
        p.duracion_noches,
        p.cupos_totales,
        p.cupos_disponibles,
        p.fecha_inicio,
        p.fecha_fin,
        p.imagen_url,
        p.estado,
        p.id_destino,
        p.id_guia,
        d.categoria AS categoria,
        d.nombre_destino,
        d.departamento,
        p.emoji
    FROM paquete_turistico p
    JOIN destino d
        ON p.id_destino = d.id_destino
"""


class PaqueteRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    # ============================================================
    # UTILIDAD
    # ============================================================

    def _fila_a_dict(self, fila):
        return dict(zip(COLUMNAS_PAQUETE, fila))

    # ============================================================
    # PAQUETES
    # ============================================================

    def obtener_todos(self, solo_activos=True):
        cursor = self.conexion.cursor()

        query = QUERY_BASE

        if solo_activos:
            query += " WHERE p.estado = 'activo'"

        query += " ORDER BY p.id_paquete"

        cursor.execute(query)

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    def obtener_por_slug(self, slug):
        cursor = self.conexion.cursor()

        cursor.execute(
            QUERY_BASE + " WHERE p.slug = %s",
            (slug,)
        )

        fila = cursor.fetchone()

        cursor.close()

        if fila is None:
            return None

        return self._fila_a_dict(fila)

    def obtener_por_id(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            QUERY_BASE + " WHERE p.id_paquete = %s",
            (id_paquete,)
        )

        fila = cursor.fetchone()

        cursor.close()

        if fila is None:
            return None

        return self._fila_a_dict(fila)

    def obtener_por_ids(self, ids_paquetes):
        if not ids_paquetes:
            return []

        cursor = self.conexion.cursor()

        cursor.execute(
            QUERY_BASE + """
                WHERE p.id_paquete = ANY(%s)
                  AND p.estado = 'activo'
                ORDER BY p.id_paquete
            """,
            (ids_paquetes,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    # ============================================================
    # SERVICIOS EXTRA
    # ============================================================

    def obtener_servicios_extra(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                id_servicio_extra,
                nombre,
                precio,
                descripcion
            FROM servicio_extra
            WHERE id_paquete = %s
              AND estado = TRUE
            ORDER BY nombre
            """,
            (id_paquete,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id": fila[0],
                "nombre": fila[1],
                "precio": float(fila[2]) if fila[2] is not None else 0,
                "descripcion": fila[3],
            }
            for fila in filas
        ]

    # ============================================================
    # ALOJAMIENTOS
    # ============================================================

    def obtener_alojamientos_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                a.id_alojamiento,
                a.nombre,
                a.tipo_alojamiento,
                a.ciudad,
                a.servicios,
                p.nombre AS proveedor
            FROM paquete_alojamiento pa
            JOIN alojamiento a
                ON a.id_alojamiento = pa.id_alojamiento
            LEFT JOIN proveedor p
                ON p.id_proveedor = a.id_proveedor
            WHERE pa.id_paquete = %s
            ORDER BY a.nombre
            """,
            (id_paquete,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_alojamiento": fila[0],
                "nombre": fila[1],
                "tipo_alojamiento": fila[2],
                "ciudad": fila[3],
                "servicios": fila[4],
                "proveedor": fila[5],
            }
            for fila in filas
        ]

    # ============================================================
    # ALIMENTACIÓN
    # ============================================================

    def obtener_alimentacion_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                a.id_alimentacion,
                a.restaurante,
                a.tipo_comida,
                a.tipo_servicio,
                a.incluye_bebidas,
                a.precio,
                p.nombre AS proveedor
            FROM paquete_alimentacion pa
            JOIN alimentacion a
                ON a.id_alimentacion = pa.id_alimentacion
            LEFT JOIN proveedor p
                ON p.id_proveedor = a.id_proveedor
            WHERE pa.id_paquete = %s
            ORDER BY a.restaurante, a.tipo_comida
            """,
            (id_paquete,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_alimentacion": fila[0],
                "restaurante": fila[1],
                "tipo_comida": fila[2],
                "tipo_servicio": fila[3],
                "incluye_bebidas": fila[4],
                "precio": (
                    float(fila[5])
                    if fila[5] is not None
                    else 0
                ),
                "proveedor": fila[6],
            }
            for fila in filas
        ]

    # ============================================================
    # TRANSPORTE
    # ============================================================

    def obtener_transportes_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                t.id_transporte,
                t.tipo,
                t.empresa,
                t.ruta,
                t.hora_salida,
                t.hora_regreso,
                t.fecha_inicio,
                t.fecha_fin,
                p.nombre AS proveedor
            FROM paquete_transporte pt
            JOIN transporte t
                ON t.id_transporte = pt.id_transporte
            LEFT JOIN proveedor p
                ON p.id_proveedor = t.id_proveedor
            WHERE pt.id_paquete = %s
            ORDER BY
                t.hora_salida NULLS LAST,
                t.id_transporte
            """,
            (id_paquete,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_transporte": fila[0],
                "tipo": fila[1],
                "empresa": fila[2],
                "ruta": fila[3],
                "hora_salida": (
                    str(fila[4])[:5]
                    if fila[4]
                    else None
                ),
                "hora_regreso": (
                    str(fila[5])[:5]
                    if fila[5]
                    else None
                ),
                "fecha_inicio": (
                    str(fila[6])
                    if fila[6]
                    else None
                ),
                "fecha_fin": (
                    str(fila[7])
                    if fila[7]
                    else None
                ),
                "proveedor": fila[8],
            }
            for fila in filas
        ]

    # ============================================================
    # ACTIVIDADES
    # ============================================================

    def obtener_actividades_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                a.id_actividad,
                a.nombre,
                a.tipo,
                a.duracion_horas,
                a.costo,
                d.nombre_destino,
                g.nombre,
                g.apellido,
                g.idiomas,
                g.especialidad
            FROM paquete_actividad pa
            JOIN actividad_turistica a
                ON a.id_actividad = pa.id_actividad
            LEFT JOIN destino d
                ON d.id_destino = a.id_destino
            LEFT JOIN guia_turistico g
                ON g.id_guia = a.id_guia
            WHERE pa.id_paquete = %s
            ORDER BY a.nombre
            """,
            (id_paquete,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_actividad": fila[0],
                "nombre": fila[1],
                "tipo": fila[2],
                "duracion_horas": (
                    float(fila[3])
                    if fila[3] is not None
                    else None
                ),
                "costo": (
                    float(fila[4])
                    if fila[4] is not None
                    else 0
                ),
                "destino": fila[5],
                "guia": (
                    f"{fila[6]} {fila[7]}"
                    if fila[6] and fila[7]
                    else None
                ),
                "guia_idiomas": fila[8],
                "guia_especialidad": fila[9],
            }
            for fila in filas
        ]

    # ============================================================
    # GUÍA DEL PAQUETE
    # ============================================================

    def obtener_guia_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                g.id_guia,
                g.nombre,
                g.apellido,
                g.idiomas,
                g.especialidad,
                g.telefono,
                g.correo
            FROM paquete_turistico p
            JOIN guia_turistico g
                ON g.id_guia = p.id_guia
            WHERE p.id_paquete = %s
              AND g.estado = TRUE
            """,
            (id_paquete,)
        )

        fila = cursor.fetchone()

        cursor.close()

        if not fila:
            return None

        return {
            "id_guia": fila[0],
            "nombre": fila[1],
            "apellido": fila[2],
            "nombre_completo": f"{fila[1]} {fila[2]}",
            "idiomas": fila[3],
            "especialidad": fila[4],
            "telefono": fila[5],
            "correo": fila[6],
        }

    # ============================================================
    # SEGUROS
    # ============================================================

    def obtener_seguros_paquete(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT DISTINCT
                s.id_seguro,
                s.nombre,
                s.cobertura,
                s.precio,
                s.es_obligatorio,
                s.descripcion,
                ts.nombre AS tipo_seguro
            FROM seguro_servicio ss
            JOIN seguro s
                ON s.id_seguro = ss.id_seguro
            JOIN tipo_seguro ts
                ON ts.id_tipo_seguro = s.id_tipo_seguro
            WHERE s.estado = TRUE
              AND (
                    ss.id_alojamiento IN (
                        SELECT pa.id_alojamiento
                        FROM paquete_alojamiento pa
                        WHERE pa.id_paquete = %s
                    )
                    OR
                    ss.id_alimentacion IN (
                        SELECT pal.id_alimentacion
                        FROM paquete_alimentacion pal
                        WHERE pal.id_paquete = %s
                    )
                    OR
                    ss.id_transporte IN (
                        SELECT pt.id_transporte
                        FROM paquete_transporte pt
                        WHERE pt.id_paquete = %s
                    )
                    OR
                    ss.id_actividad IN (
                        SELECT pact.id_actividad
                        FROM paquete_actividad pact
                        WHERE pact.id_paquete = %s
                    )
              )
            ORDER BY
                s.es_obligatorio DESC,
                s.nombre
            """,
            (
                id_paquete,
                id_paquete,
                id_paquete,
                id_paquete,
            )
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_seguro": fila[0],
                "nombre": fila[1],
                "cobertura": fila[2],
                "precio": (
                    float(fila[3])
                    if fila[3] is not None
                    else 0
                ),
                "es_obligatorio": fila[4],
                "descripcion": fila[5],
                "tipo_seguro": fila[6],
            }
            for fila in filas
        ]

    # ============================================================
    # DESTINOS
    # ============================================================

    def obtener_destinos(self):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                id_destino,
                nombre_destino
            FROM destino
            WHERE estado = TRUE
            ORDER BY nombre_destino
            """
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_destino": fila[0],
                "nombre_destino": fila[1],
            }
            for fila in filas
        ]

    # ============================================================
    # GUÍAS
    # ============================================================

    def obtener_guias(self):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                id_guia,
                nombre,
                apellido
            FROM guia_turistico
            WHERE estado = TRUE
            ORDER BY nombre
            """
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_guia": fila[0],
                "nombre_completo": f"{fila[1]} {fila[2]}",
            }
            for fila in filas
        ]

    # ============================================================
    # QUÉ INCLUYE EL PAQUETE
    # ============================================================

    def obtener_incluye(self, id_paquete):
        cursor = self.conexion.cursor()

        incluye = []

        cursor.execute(
            """
            SELECT 1
            FROM paquete_alojamiento
            WHERE id_paquete = %s
            LIMIT 1
            """,
            (id_paquete,)
        )

        if cursor.fetchone():
            incluye.append("alojamiento")

        cursor.execute(
            """
            SELECT 1
            FROM paquete_transporte
            WHERE id_paquete = %s
            LIMIT 1
            """,
            (id_paquete,)
        )

        if cursor.fetchone():
            incluye.append("transporte")

        cursor.execute(
            """
            SELECT 1
            FROM paquete_alimentacion
            WHERE id_paquete = %s
            LIMIT 1
            """,
            (id_paquete,)
        )

        if cursor.fetchone():
            incluye.append("alimentacion")

        cursor.execute(
            """
            SELECT 1
            FROM paquete_actividad
            WHERE id_paquete = %s
            LIMIT 1
            """,
            (id_paquete,)
        )

        if cursor.fetchone():
            incluye.append("guia")

        cursor.close()

        return incluye

    # ============================================================
    # DISPONIBILIDAD LEGACY
    # ============================================================
    # Se conserva para no romper código antiguo.
    # Las nuevas reservas deben utilizar salida_paquete.

    def obtener_disponibilidad(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                fecha_inicio,
                fecha_fin,
                cupos_disponibles
            FROM paquete_turistico
            WHERE id_paquete = %s
            """,
            (id_paquete,)
        )

        fila = cursor.fetchone()

        cursor.close()

        if not fila:
            return None

        return {
            "fecha_inicio": (
                str(fila[0])
                if fila[0]
                else None
            ),
            "fecha_fin": (
                str(fila[1])
                if fila[1]
                else None
            ),
            "cupos_disponibles": fila[2],
        }

    # ============================================================
    # FILTROS
    # ============================================================

    def filtrar(
        self,
        termino,
        categoria,
        duracion,
        precio_max,
        incluye,
        destino=None,
        precio_min=None,
        fecha_desde=None,
        solo_disponibles=False,
        ordenar="recomendados",
    ):
        sql = QUERY_BASE + """
            WHERE p.estado = 'activo'
        """

        valores = []

        # --------------------------------------------------------
        # BÚSQUEDA
        # --------------------------------------------------------

        if termino:
            patron = f"%{termino}%"

            sql += """
                AND (
                    p.nombre ILIKE %s
                    OR p.descripcion ILIKE %s
                    OR d.nombre_destino ILIKE %s
                    OR d.departamento ILIKE %s
                    OR d.categoria ILIKE %s
                )
            """

            valores.extend([
                patron,
                patron,
                patron,
                patron,
                patron,
            ])

        # --------------------------------------------------------
        # CATEGORÍA
        # --------------------------------------------------------

        if categoria == "todos":
            categoria = ""

        if categoria:
            sql += """
                AND d.categoria = %s
            """

            valores.append(categoria)

        # --------------------------------------------------------
        # DURACIÓN
        # --------------------------------------------------------

        if duracion:
            duraciones = []

            if "corto" in duracion:
                duraciones.append(
                    "p.duracion_dias BETWEEN 1 AND 3"
                )

            if "medio" in duracion:
                duraciones.append(
                    "p.duracion_dias BETWEEN 4 AND 7"
                )

            if "largo" in duracion:
                duraciones.append(
                    "p.duracion_dias >= 8"
                )

            if duraciones:
                sql += " AND (" + " OR ".join(duraciones) + ")"

        # --------------------------------------------------------
        # PRECIO MÁXIMO
        # --------------------------------------------------------

        if precio_max:
            sql += """
                AND p.precio <= %s
            """

            valores.append(precio_max)

        # --------------------------------------------------------
        # INCLUYE
        # --------------------------------------------------------

        if incluye:
            condiciones_incluye = []

            if "alojamiento" in incluye:
                condiciones_incluye.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM paquete_alojamiento pa
                        WHERE pa.id_paquete = p.id_paquete
                    )
                    """
                )

            if "transporte" in incluye:
                condiciones_incluye.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM paquete_transporte pt
                        WHERE pt.id_paquete = p.id_paquete
                    )
                    """
                )

            if "alimentacion" in incluye:
                condiciones_incluye.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM paquete_alimentacion pal
                        WHERE pal.id_paquete = p.id_paquete
                    )
                    """
                )

            if "guia" in incluye:
                condiciones_incluye.append(
                    """
                    p.id_guia IS NOT NULL
                    """
                )

            if "seguro" in incluye:
                condiciones_incluye.append(
                    """
                    (
                        EXISTS (
                            SELECT 1
                            FROM paquete_alojamiento pa
                            JOIN seguro_servicio ss
                                ON ss.id_alojamiento =
                                   pa.id_alojamiento
                            WHERE pa.id_paquete = p.id_paquete
                        )
                        OR
                        EXISTS (
                            SELECT 1
                            FROM paquete_transporte pt
                            JOIN seguro_servicio ss
                                ON ss.id_transporte =
                                   pt.id_transporte
                            WHERE pt.id_paquete = p.id_paquete
                        )
                    )
                    """
                )

            if condiciones_incluye:
                sql += """
                    AND (
                """ + " OR ".join(condiciones_incluye) + """
                    )
                """

        # --------------------------------------------------------
        # DESTINO
        # --------------------------------------------------------

        if destino:
            sql += """
                AND (
                    CAST(p.id_destino AS TEXT) = %s
                    OR d.nombre_destino ILIKE %s
                    OR d.ciudad ILIKE %s
                )
            """

            patron_destino = f"%{destino}%"

            valores.extend([
                str(destino),
                patron_destino,
                patron_destino,
            ])

        # --------------------------------------------------------
        # PRECIO MÍNIMO
        # --------------------------------------------------------

        if precio_min:
            sql += """
                AND p.precio >= %s
            """

            valores.append(precio_min)

        # --------------------------------------------------------
        # FECHA
        # --------------------------------------------------------

        if fecha_desde:
            sql += """
                AND (
                    p.fecha_fin IS NULL
                    OR p.fecha_fin >= %s
                )
            """

            valores.append(fecha_desde)

        # --------------------------------------------------------
        # DISPONIBILIDAD LEGACY
        # --------------------------------------------------------

        if solo_disponibles:
            sql += """
                AND p.cupos_disponibles > 0
            """

        # --------------------------------------------------------
        # ORDEN
        # --------------------------------------------------------

        ordenes = {
            "precio_asc":
                "p.precio ASC",

            "precio_desc":
                "p.precio DESC",

            "duracion_asc":
                "p.duracion_dias ASC, p.precio ASC",

            "duracion_desc":
                "p.duracion_dias DESC, p.precio ASC",

            "disponibilidad":
                "p.cupos_disponibles DESC, p.precio ASC",

            "recomendados":
                "p.cupos_disponibles DESC, p.id_paquete",
        }

        sql += """
            ORDER BY
        """ + ordenes.get(
            ordenar,
            ordenes["recomendados"]
        )

        cursor = self.conexion.cursor()

        cursor.execute(sql, valores)

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    # ============================================================
    # PROMOCIONES
    # ============================================================

    def obtener_promociones_activas(self, limite=8):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT
                pr.id_promocion,
                pr.codigo,
                pr.descuento,
                pr.descripcion,
                pr.fecha_inicio,
                pr.fecha_fin,
                pr.tipo_promocion,
                p.id_paquete,
                p.nombre,
                p.slug,
                p.precio,
                p.imagen_url,
                d.nombre_destino,
                d.categoria
            FROM promocion pr
            LEFT JOIN paquete_turistico p
                ON p.id_paquete = pr.id_paquete
            LEFT JOIN destino d
                ON d.id_destino = p.id_destino
            WHERE
                (
                    pr.fecha_inicio IS NULL
                    OR pr.fecha_inicio <= CURRENT_DATE
                )
                AND
                (
                    pr.fecha_fin IS NULL
                    OR pr.fecha_fin >= CURRENT_DATE
                )
                AND
                (
                    p.id_paquete IS NULL
                    OR p.estado = 'activo'
                )
            ORDER BY
                pr.descuento DESC,
                pr.id_promocion
            LIMIT %s
            """,
            (limite,)
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            {
                "id_promocion": fila[0],
                "codigo": fila[1],
                "descuento": (
                    float(fila[2])
                    if fila[2] is not None
                    else 0
                ),
                "descripcion": fila[3],
                "fecha_inicio": fila[4],
                "fecha_fin": fila[5],
                "tipo_promocion": fila[6],
                "id_paquete": fila[7],
                "nombre": fila[8],
                "slug": fila[9],
                "precio": (
                    float(fila[10])
                    if fila[10] is not None
                    else None
                ),
                "imagen_url": fila[11],
                "nombre_destino": fila[12],
                "categoria": fila[13],
            }
            for fila in filas
        ]

    # ============================================================
    # PAQUETES POR DESTINO
    # ============================================================

    def obtener_paquetes_destino(self, id_destino, limite=12):
        cursor = self.conexion.cursor()

        cursor.execute(
            QUERY_BASE + """
                WHERE p.id_destino = %s
                  AND p.estado = 'activo'
                ORDER BY
                    p.cupos_disponibles DESC,
                    p.precio ASC
                LIMIT %s
            """,
            (
                id_destino,
                limite,
            )
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    # ============================================================
    # RESERVAS
    # ============================================================

    def contar_reservas_no_canceladas(self, id_paquete):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM reserva
            WHERE id_paquete = %s
              AND estado <> 'cancelada'
            """,
            (id_paquete,)
        )

        total = cursor.fetchone()[0]

        cursor.close()

        return total

    def cancelar_reservas_por_contingencia(
        self,
        id_paquete,
        motivo,
    ):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            UPDATE reserva
            SET
                estado = 'cancelada',
                motivo_cancelacion = %s,
                reembolso_estado = 'pendiente',
                reembolso_fecha = NULL
            WHERE id_paquete = %s
              AND estado <> 'cancelada'
            """,
            (
                motivo,
                id_paquete,
            )
        )

        afectadas = cursor.rowcount

        cursor.execute(
            """
            UPDATE paquete_turistico
            SET estado = 'suspendido'
            WHERE id_paquete = %s
            """,
            (id_paquete,)
        )

        self.conexion.commit()

        cursor.close()

        return afectadas

    # ============================================================
    # BÚSQUEDA
    # ============================================================

    def buscar(self, termino):
        cursor = self.conexion.cursor()

        patron = f"%{termino}%"

        cursor.execute(
            QUERY_BASE + """
                WHERE p.estado = 'activo'
                  AND (
                        p.nombre ILIKE %s
                        OR p.descripcion ILIKE %s
                        OR d.nombre_destino ILIKE %s
                        OR d.departamento ILIKE %s
                        OR d.categoria ILIKE %s
                  )
                ORDER BY p.id_paquete
            """,
            (
                patron,
                patron,
                patron,
                patron,
                patron,
            )
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    # ============================================================
    # CREAR
    # ============================================================

    def crear(self, datos):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            INSERT INTO paquete_turistico
            (
                nombre,
                slug,
                descripcion,
                precio,
                duracion_dias,
                duracion_noches,
                cupos_totales,
                cupos_disponibles,
                fecha_inicio,
                fecha_fin,
                estado,
                id_destino,
                id_guia,
                imagen_url,
                personalizable,
                emoji
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, 'activo',
                %s, %s, %s, %s, %s
            )
            RETURNING id_paquete
            """,
            (
                datos["nombre"],
                datos["slug"],
                datos["descripcion"],
                datos["precio"],
                datos["duracion_dias"],
                datos["duracion_noches"],
                datos["cupos_totales"],
                datos["cupos_totales"],
                datos["fecha_inicio"],
                datos["fecha_fin"],
                datos["id_destino"],
                datos["id_guia"],
                datos.get("imagen_url"),
                datos.get("personalizable", False),
                datos.get("emoji", "🧳"),
            )
        )

        nuevo_id = cursor.fetchone()[0]

        self.conexion.commit()

        cursor.close()

        return nuevo_id

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    def actualizar(self, id_paquete, datos):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM reserva
            WHERE id_paquete = %s
              AND estado <> 'cancelada'
            """,
            (id_paquete,)
        )

        reservas_activas = cursor.fetchone()[0]

        if datos.get("cupos_totales", 0) < reservas_activas:
            cursor.close()

            raise ValueError(
                f"No puedes establecer menos de "
                f"{reservas_activas} cupos: "
                "ya existen reservas activas."
            )

        cursor.execute(
            """
            UPDATE paquete_turistico
            SET
                nombre = %s,
                descripcion = %s,
                precio = %s,
                duracion_dias = %s,
                duracion_noches = %s,
                fecha_inicio = %s,
                fecha_fin = %s,
                id_destino = %s,
                id_guia = %s,
                emoji = %s,
                imagen_url = %s,
                personalizable = %s,
                cupos_totales = %s,
                cupos_disponibles = %s
            WHERE id_paquete = %s
            """,
            (
                datos["nombre"],
                datos["descripcion"],
                datos["precio"],
                datos["duracion_dias"],
                datos["duracion_noches"],
                datos["fecha_inicio"],
                datos["fecha_fin"],
                datos["id_destino"],
                datos["id_guia"],
                datos.get("emoji", "🧳"),
                datos.get("imagen_url"),
                datos.get("personalizable", False),
                datos["cupos_totales"],
                max(
                    0,
                    datos["cupos_totales"] - reservas_activas
                ),
                id_paquete,
            )
        )

        actualizado = cursor.rowcount > 0

        self.conexion.commit()

        cursor.close()

        return actualizado

    # ============================================================
    # CAMBIAR ESTADO
    # ============================================================

    def cambiar_estado(self, id_paquete, estado):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            UPDATE paquete_turistico
            SET estado = %s
            WHERE id_paquete = %s
            """,
            (
                estado,
                id_paquete,
            )
        )

        cambiado = cursor.rowcount > 0

        self.conexion.commit()

        cursor.close()

        return cambiado

    # ============================================================
    # COMPARACIÓN
    # ============================================================

    def obtener_comparacion(self, ids_paquetes):
        if not ids_paquetes:
            return []

        cursor = self.conexion.cursor()

        cursor.execute(
            QUERY_BASE + """
                WHERE p.id_paquete = ANY(%s)
                ORDER BY array_position(
                    %s::int[],
                    p.id_paquete
                )
            """,
            (
                ids_paquetes,
                ids_paquetes,
            )
        )

        filas = cursor.fetchall()

        cursor.close()

        return [
            self._fila_a_dict(fila)
            for fila in filas
        ]

    # ============================================================
    # FAVORITOS
    # ============================================================

    def obtener_favoritos_cliente(self, id_cliente):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            SELECT id_paquete
            FROM favoritos
            WHERE id_cliente = %s
            ORDER BY fecha_agregado DESC
            """,
            (id_cliente,)
        )

        ids = [
            fila[0]
            for fila in cursor.fetchall()
        ]

        cursor.close()

        return ids

    def agregar_favorito(
        self,
        id_cliente,
        id_paquete,
    ):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            INSERT INTO favoritos
            (
                id_cliente,
                id_paquete
            )
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                id_cliente,
                id_paquete,
            )
        )

        self.conexion.commit()

        cursor.close()

    def quitar_favorito(
        self,
        id_cliente,
        id_paquete,
    ):
        cursor = self.conexion.cursor()

        cursor.execute(
            """
            DELETE FROM favoritos
            WHERE id_cliente = %s
              AND id_paquete = %s
            """,
            (
                id_cliente,
                id_paquete,
            )
        )

        self.conexion.commit()

        cursor.close()

    def obtener_paquetes_para_comparar(self, ids):
        if not ids:
            return []

        placeholders = ",".join(["%s"] * len(ids))

        query = QUERY_BASE + f"""
            WHERE p.id_paquete IN ({placeholders})
            ORDER BY p.precio ASC
        """

        try:
                    cursor = self.conexion.cursor()
                    cursor.execute(query, ids)

                    filas = cursor.fetchall()

                    columnas = [
                        "id_paquete",
                        "nombre",
                        "slug",
                        "descripcion",
                        "precio",
                        "duracion_dias",
                        "duracion_noches",
                        "cupos_totales",
                        "cupos_disponibles",
                        "fecha_inicio",
                        "fecha_fin",
                        "imagen_url",
                        "estado",
                        "id_destino",
                        "id_guia",
                        "categoria",
                        "nombre_destino",
                        "departamento",
                        "emoji",
                    ]

                    return [
                        dict(zip(columnas, fila))
                        for fila in filas
                    ]

        except Exception as e:
            print(f"Error al obtener paquetes para comparar: {e}")
            return []