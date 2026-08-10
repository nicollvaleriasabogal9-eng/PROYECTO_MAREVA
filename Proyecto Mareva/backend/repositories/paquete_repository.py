from config.conexion import Conexion

COLUMNAS_PAQUETE = [
    "id_paquete", "nombre", "slug", "descripcion", "precio",
    "duracion_dias", "duracion_noches", "cupos_totales", "cupos_disponibles",
    "fecha_inicio", "fecha_fin", "emoji", "estado", "id_destino", "id_guia",
    "categoria", "nombre_destino", "departamento"
]

QUERY_BASE = """
    SELECT p.id_paquete, p.nombre, p.slug, p.descripcion, p.precio,
           p.duracion_dias, p.duracion_noches, p.cupos_totales, p.cupos_disponibles,
           p.fecha_inicio, p.fecha_fin, p.emoji, p.estado, p.id_destino, p.id_guia,
           d.categoria, d.nombre_destino, d.departamento
      FROM paquete_turistico p
      JOIN destino d ON d.id_destino = p.id_destino
"""


class PaqueteRepository:

    def __init__(self):
        self.conexion = Conexion().obtener_conexion()

    def _fila_a_dict(self, fila):
        return dict(zip(COLUMNAS_PAQUETE, fila))

    def obtener_todos(self, solo_activos=True):
        cursor = self.conexion.cursor()

        query = QUERY_BASE
        if solo_activos:
            query += " WHERE p.estado = 'activo'"
        query += " ORDER BY p.id_paquete"

        cursor.execute(query)
        filas = cursor.fetchall()
        cursor.close()

        return [self._fila_a_dict(f) for f in filas]

    def obtener_por_slug(self, slug):
        cursor = self.conexion.cursor()
        cursor.execute(QUERY_BASE + " WHERE p.slug = %s", (slug,))
        fila = cursor.fetchone()
        cursor.close()

        if fila is None:
            return None
        return self._fila_a_dict(fila)

    def obtener_por_id(self, id_paquete):
        cursor = self.conexion.cursor()
        cursor.execute(QUERY_BASE + " WHERE p.id_paquete = %s", (id_paquete,))
        fila = cursor.fetchone()
        cursor.close()

        if fila is None:
            return None
        return self._fila_a_dict(fila)

    def obtener_servicios_extra(self, id_paquete):
        cursor = self.conexion.cursor()
        cursor.execute(
            "SELECT id_servicio_extra, nombre, precio, descripcion "
            "FROM servicio_extra WHERE id_paquete = %s AND estado = TRUE",
            (id_paquete,)
        )
        filas = cursor.fetchall()
        cursor.close()
        return [{"id": f[0], "nombre": f[1], "precio": float(f[2]), "descripcion": f[3]} for f in filas]

    def obtener_destinos(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_destino, nombre_destino FROM destino WHERE estado = TRUE ORDER BY nombre_destino")
        filas = cursor.fetchall()
        cursor.close()
        return [{"id_destino": f[0], "nombre_destino": f[1]} for f in filas]

    def obtener_guias(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_guia, nombre, apellido FROM guia_turistico WHERE estado = TRUE ORDER BY nombre")
        filas = cursor.fetchall()
        cursor.close()
        return [{"id_guia": f[0], "nombre_completo": f"{f[1]} {f[2]}"} for f in filas]

    # ---------- Admin: escritura ----------

    def crear(self, datos):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO paquete_turistico
                (nombre, slug, descripcion, precio, duracion_dias, duracion_noches,
                 cupos_totales, cupos_disponibles, fecha_inicio, fecha_fin,
                 estado, id_destino, id_guia, emoji)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'activo', %s, %s, %s)
            RETURNING id_paquete
        """, (
            datos["nombre"], datos["slug"], datos["descripcion"], datos["precio"],
            datos["duracion_dias"], datos["duracion_noches"], datos["cupos_totales"],
            datos["cupos_totales"], datos["fecha_inicio"], datos["fecha_fin"],
            datos["id_destino"], datos["id_guia"], datos["emoji"]
        ))
        nuevo_id = cursor.fetchone()[0]
        self.conexion.commit()
        cursor.close()
        return nuevo_id

    def actualizar(self, id_paquete, datos):
        cursor = self.conexion.cursor()
        cursor.execute("""
            UPDATE paquete_turistico
               SET nombre=%s, descripcion=%s, precio=%s, duracion_dias=%s,
                   duracion_noches=%s, fecha_inicio=%s, fecha_fin=%s,
                   id_destino=%s, id_guia=%s, emoji=%s
             WHERE id_paquete=%s
        """, (
            datos["nombre"], datos["descripcion"], datos["precio"], datos["duracion_dias"],
            datos["duracion_noches"], datos["fecha_inicio"], datos["fecha_fin"],
            datos["id_destino"], datos["id_guia"], datos["emoji"], id_paquete
        ))
        actualizado = cursor.rowcount > 0
        self.conexion.commit()
        cursor.close()
        return actualizado

    def cambiar_estado(self, id_paquete, estado):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE paquete_turistico SET estado=%s WHERE id_paquete=%s", (estado, id_paquete))
        cambiado = cursor.rowcount > 0
        self.conexion.commit()
        cursor.close()
        return cambiado
    def obtener_incluye(self, id_paquete):
        cursor = self.conexion.cursor()
    incluye = []

    def obtener_incluye(self, id_paquete):
        cursor = self.conexion.cursor()
        incluye = []

        cursor.execute("SELECT 1 FROM paquete_alojamiento WHERE id_paquete = %s LIMIT 1", (id_paquete,))
        if cursor.fetchone():
            incluye.append("alojamiento")

        cursor.execute("SELECT 1 FROM paquete_transporte WHERE id_paquete = %s LIMIT 1", (id_paquete,))
        if cursor.fetchone():
            incluye.append("transporte")

        cursor.execute("SELECT 1 FROM paquete_alimentacion WHERE id_paquete = %s LIMIT 1", (id_paquete,))
        if cursor.fetchone():
            incluye.append("alimentacion")

        cursor.execute("SELECT 1 FROM paquete_actividad WHERE id_paquete = %s LIMIT 1", (id_paquete,))
        if cursor.fetchone():
            incluye.append("guia")

        cursor.close()
        return incluye

    def obtener_disponibilidad(self, id_paquete):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT fecha_inicio, fecha_fin, cupos_disponibles
            FROM paquete_turistico
            WHERE id_paquete = %s
        """, (id_paquete,))
        fila = cursor.fetchone()
        cursor.close()
        if not fila:
            return None
        return {
            "fecha_inicio": str(fila[0]) if fila[0] else None,
            "fecha_fin": str(fila[1]) if fila[1] else None,
            "cupos_disponibles": fila[2],
        }