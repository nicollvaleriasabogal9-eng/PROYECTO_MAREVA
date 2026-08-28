from flask import Flask, render_template, request, redirect, url_for, session
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import psycopg2
import uuid

PAQUETES = [
    {"slug":"cartagena-magica","nombre":"Cartagena Mágica","categoria":"playa","precio":1850000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Descubre la ciudad amurallada con playas privadas e historia colonial.","emoji":"🏰","destino":"Cartagena","departamento":"Bolívar","incluye":["alojamiento","transporte","guia"],"servicios_extra":[{"nombre":"Snorkel en Islas del Rosario","precio":180000},{"nombre":"Foto profesional en la Muralla","precio":120000}]},
    {"slug":"medellin-innovadora","nombre":"Medellín Innovadora","categoria":"ciudad","precio":1200000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Conoce la ciudad más transformadora de América Latina.","emoji":"🚡","destino":"Medellín","departamento":"Antioquia","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"guatape-extremo","nombre":"Guatapé Extremo","categoria":"aventura","precio":890000,"duracion_dias":3,"duracion_noches":2,"descripcion":"Adrenalina pura: sube la Piedra del Peñol y navega el embalse.","emoji":"🪨","destino":"Guatapé","departamento":"Antioquia","incluye":["alojamiento","guia"],"servicios_extra":[{"nombre":"Kayak en el embalse","precio":95000},{"nombre":"Rappel en La Piedra","precio":140000}]},
    {"slug":"san-andres-todo-incluido","nombre":"San Andrés Todo Incluido","categoria":"playa","precio":3200000,"duracion_dias":7,"duracion_noches":6,"descripcion":"El mar de los siete colores con todo incluido en resort 5 estrellas.","emoji":"🏝️","destino":"San Andrés","departamento":"San Andrés","incluye":["alojamiento","vuelo","transporte","seguro"],"servicios_extra":[]},
    {"slug":"tayrona-salvaje","nombre":"Tayrona Salvaje","categoria":"ecoturismo","precio":1450000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Selva, playas vírgenes y ecosistemas únicos en el Parque Tayrona.","emoji":"🌴","destino":"Parque Tayrona","departamento":"Magdalena","incluye":["alojamiento","transporte","seguro"],"servicios_extra":[{"nombre":"Buceo certificado","precio":350000},{"nombre":"Senderismo nocturno","precio":120000}]},
    {"slug":"valle-cocora-mistico","nombre":"Valle del Cocora Místico","categoria":"ecoturismo","precio":980000,"duracion_dias":3,"duracion_noches":2,"descripcion":"Caminata entre palmas de cera y fincas cafeteras del Quindío.","emoji":"🌿","destino":"Valle del Cocora","departamento":"Quindío","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"amazonas-aventura","nombre":"Amazonas Aventura","categoria":"aventura","precio":2750000,"duracion_dias":6,"duracion_noches":5,"descripcion":"Explora la selva amazónica y conoce comunidades indígenas.","emoji":"🦜","destino":"Leticia","departamento":"Amazonas","incluye":["alojamiento","vuelo","guia","seguro"],"servicios_extra":[]},
    {"slug":"tatacoa","nombre":"Desierto de la Tatacoa","categoria":"aventura","precio":750000,"duracion_dias":3,"duracion_noches":2,"descripcion":"Observación astronómica y recorridos por paisajes únicos.","emoji":"🌵","destino":"Desierto Tatacoa","departamento":"Huila","incluye":["transporte","guia"],"servicios_extra":[]},
    {"slug":"cano-cristales","nombre":"Caño Cristales Premium","categoria":"aventura","precio":2950000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Visita el río más hermoso del mundo con guía especializado.","emoji":"🌈","destino":"Caño Cristales","departamento":"Meta","incluye":["alojamiento","vuelo","guia","seguro"],"servicios_extra":[]},
    {"slug":"eje-cafetero","nombre":"Eje Cafetero Tradicional","categoria":"cultural","precio":1350000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Recorrido por fincas cafeteras y pueblos patrimonio.","emoji":"☕","destino":"Armenia","departamento":"Quindío","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"nuqui-ecoturismo","nombre":"Nuquí Ecoturismo","categoria":"playa","precio":2400000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Avistamiento de ballenas y playas vírgenes del Pacífico.","emoji":"🐋","destino":"Nuquí","departamento":"Chocó","incluye":["alojamiento","transporte","guia"],"servicios_extra":[]},
    {"slug":"barichara-colonial","nombre":"Barichara Colonial","categoria":"cultural","precio":890000,"duracion_dias":3,"duracion_noches":2,"descripcion":"Conoce uno de los pueblos más bellos de Colombia.","emoji":"🏘️","destino":"Barichara","departamento":"Santander","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"santuario-las-lajas","nombre":"Santuario Las Lajas","categoria":"cultural","precio":680000,"duracion_dias":3,"duracion_noches":2,"descripcion":"Basílica neogótica construida sobre un cañón.","emoji":"⛪","destino":"Ipiales","departamento":"Nariño","incluye":["transporte","guia"],"servicios_extra":[]},
    {"slug":"boyaca-historica","nombre":"Boyacá Histórica","categoria":"cultural","precio":980000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Villa de Leyva, Ráquira y monumentos históricos.","emoji":"🏛️","destino":"Villa de Leyva","departamento":"Boyacá","incluye":["alojamiento","transporte","guia"],"servicios_extra":[]},
    {"slug":"canon-del-chicamocha","nombre":"Cañón del Chicamocha","categoria":"aventura","precio":1150000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Deportes extremos y paisajes espectaculares.","emoji":"🪂","destino":"San Gil","departamento":"Santander","incluye":["alojamiento","guia","seguro"],"servicios_extra":[]},
    {"slug":"mompox-patrimonial","nombre":"Mompox Patrimonial","categoria":"cultural","precio":1250000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Historia, arquitectura colonial y cultura ribereña.","emoji":"⛵","destino":"Mompox","departamento":"Bolívar","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"sierra-nevada-ancestral","nombre":"Sierra Nevada Ancestral","categoria":"aventura","precio":2100000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Conexión con comunidades indígenas y naturaleza.","emoji":"🏔️","destino":"Santa Marta","departamento":"Magdalena","incluye":["alojamiento","guia","seguro"],"servicios_extra":[]},
    {"slug":"tolu-covenas-relax","nombre":"Tolú y Coveñas Relax","categoria":"playa","precio":1100000,"duracion_dias":4,"duracion_noches":3,"descripcion":"Playas tranquilas y actividades acuáticas.","emoji":"🏖️","destino":"Tolú","departamento":"Sucre","incluye":["alojamiento","transporte"],"servicios_extra":[]},
    {"slug":"isla-gorgona-explorer","nombre":"Isla Gorgona Explorer","categoria":"aventura","precio":2800000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Naturaleza, senderismo y biodiversidad marina.","emoji":"🦈","destino":"Guapi","departamento":"Cauca","incluye":["alojamiento","guia","seguro"],"servicios_extra":[]},
    {"slug":"capurgana-paraiso","nombre":"Capurganá Paraíso","categoria":"playa","precio":1900000,"duracion_dias":5,"duracion_noches":4,"descripcion":"Playas cristalinas y ecoturismo en el Caribe colombiano.","emoji":"🐠","destino":"Acandí","departamento":"Chocó","incluye":["alojamiento","guia"],"servicios_extra":[]},
]

DESTINOS = [
    {"nombre_destino":"Cartagena de Indias","departamento":"Bolívar","ciudad":"Cartagena","categoria":"playa","descripcion":"Ciudad amurallada Patrimonio de la Humanidad con playas caribeñas.","emoji":"🏰"},
    {"nombre_destino":"Medellín","departamento":"Antioquia","ciudad":"Medellín","categoria":"ciudad","descripcion":"La ciudad de la eterna primavera, innovadora y cultural.","emoji":"🚡"},
    {"nombre_destino":"Guatapé","departamento":"Antioquia","ciudad":"Guatapé","categoria":"aventura","descripcion":"Pueblo colorido con la imponente Piedra del Peñol.","emoji":"🪨"},
    {"nombre_destino":"San Andrés","departamento":"San Andrés","ciudad":"San Andrés","categoria":"playa","descripcion":"El mar de los siete colores en el Caribe colombiano.","emoji":"🏝️"},
    {"nombre_destino":"Parque Tayrona","departamento":"Magdalena","ciudad":"Santa Marta","categoria":"playa","descripcion":"Naturaleza salvaje: selva tropical y playas vírgenes.","emoji":"🌴"},
    {"nombre_destino":"Valle del Cocora","departamento":"Quindío","ciudad":"Salento","categoria":"montaña","descripcion":"Hogar de las palmas de cera, árbol nacional de Colombia.","emoji":"🌿"},
    {"nombre_destino":"Barichara","departamento":"Santander","ciudad":"Barichara","categoria":"cultural","descripcion":"El pueblo más bonito de Colombia, arquitectura colonial.","emoji":"🏘️"},
    {"nombre_destino":"Leticia","departamento":"Amazonas","ciudad":"Leticia","categoria":"aventura","descripcion":"Puerta de entrada a la Amazonía colombiana.","emoji":"🦜"},
    {"nombre_destino":"Caño Cristales","departamento":"Meta","ciudad":"La Macarena","categoria":"aventura","descripcion":"El río más hermoso del mundo, famoso por sus colores únicos.","emoji":"🌈"},
    {"nombre_destino":"Eje Cafetero","departamento":"Quindío","ciudad":"Armenia","categoria":"cultural","descripcion":"Paisaje Cultural Cafetero, Patrimonio de la Humanidad.","emoji":"☕"},
    {"nombre_destino":"Nuquí","departamento":"Chocó","ciudad":"Nuquí","categoria":"playa","descripcion":"Paraíso del Pacífico colombiano, avistamiento de ballenas jorobadas.","emoji":"🐋"},
    {"nombre_destino":"Barichara Colonial","departamento":"Santander","ciudad":"Barichara","categoria":"cultural","descripcion":"Arquitectura colonial de piedra y el Camino Real hacia Guane.","emoji":"🏛️"},
    {"nombre_destino":"Las Lajas","departamento":"Nariño","ciudad":"Ipiales","categoria":"cultural","descripcion":"Basílica neogótica construida sobre un cañón, ícono religioso.","emoji":"⛪"},
    {"nombre_destino":"Villa de Leyva","departamento":"Boyacá","ciudad":"Villa de Leyva","categoria":"cultural","descripcion":"Plaza empedrada más grande de Colombia, arquitectura colonial.","emoji":"🏰"},
    {"nombre_destino":"Cañón del Chicamocha","departamento":"Santander","ciudad":"San Gil","categoria":"aventura","descripcion":"Capital colombiana de los deportes extremos y paisajes épicos.","emoji":"🪂"},
    {"nombre_destino":"Mompox","departamento":"Bolívar","ciudad":"Mompox","categoria":"cultural","descripcion":"Ciudad Patrimonio de la Humanidad a orillas del río Magdalena.","emoji":"⛵"},
    {"nombre_destino":"Sierra Nevada","departamento":"Magdalena","ciudad":"Santa Marta","categoria":"aventura","descripcion":"La montaña costera más alta del mundo y territorios indígenas.","emoji":"🏔️"},
    {"nombre_destino":"Tolú y Coveñas","departamento":"Sucre","ciudad":"Tolú","categoria":"playa","descripcion":"Playas tranquilas del Caribe colombiano, ideal para el descanso.","emoji":"🏖️"},
    {"nombre_destino":"Isla Gorgona","departamento":"Cauca","ciudad":"Guapi","categoria":"aventura","descripcion":"Parque Nacional Natural, antigua prisión y reserva marina única.","emoji":"🦈"},
    {"nombre_destino":"Capurganá","departamento":"Chocó","ciudad":"Acandí","categoria":"playa","descripcion":"Pueblo caribeño sin carreteras, paraíso de buceadores.","emoji":"🐠"},
]

INSIGNIAS = [
    {"nombre":"Explorador","descripcion":"Has explorado 5 destinos diferentes.","icono":"🧭","progreso":"2","meta":"4"},
    {"nombre":"Aventurero","descripcion":"Has reservado 3 paquetes de aventura.","icono":"🏔️","progreso":"1","meta":"3"},
    {"nombre":"Cultural","descripcion":"Has visitado 4 destinos culturales.","icono":"🏛️","progreso":"3","meta":"4"},
    {"nombre":"Amante del Mar","descripcion":"Has disfrutado de 3 paquetes de playa.","icono":"🏖️","progreso":"2","meta":"3"},
    {"nombre":"Eco-Consciente","descripcion":"Has participado en 2 paquetes de ecoturismo.","icono":"🌿","progreso":"1","meta":"2"}
]

NIVELES = [
    {"nivel":"Bronce","nombre":"Explorador","experiencia":"0-400XP","estado":"Bloqueado"},
    {"nivel":"Plata","nombre":"Aventurero","experiencia":"500-900XP","estado":"Bloqueado"},
    {"nivel":"Oro","nombre":"Experto","experiencia":"1000-1500XP","estado":"Bloqueado"},
    {"nivel":"Diamante","nombre":"Profesional","experiencia":"1600-2000XP","estado":"Bloqueado"}
]

class PaqueteBase(ABC):
    def __init__(self, paquete_dict):
        self._data = paquete_dict

    def get_nombre(self):
        return self._data["nombre"]

    def get_precio(self):
        return self._data["precio"]

    def get_categoria(self):
        return self._data["categoria"]

    @abstractmethod
    def calcular_precio_final(self):
        pass

class Playa(PaqueteBase):
    def calcular_precio_final(self):
        return self._data["precio"] * 1.10

class Aventura(PaqueteBase):
    def calcular_precio_final(self):
        return self._data["precio"] * 1.15

class Ecoturismo(PaqueteBase):
    def calcular_precio_final(self):
        return self._data["precio"] * 1.08

class Cultural(PaqueteBase):
    def calcular_precio_final(self):
        return self._data["precio"] * 0.95

def factory_paquete(paquete_dict):
    categoria = paquete_dict["categoria"]

    if categoria == "playa":
        return Playa(paquete_dict)
    elif categoria == "aventura":
        return Aventura(paquete_dict)
    elif categoria == "ecoturismo":
        return Ecoturismo(paquete_dict)
    else:
        return Cultural(paquete_dict)

def obtener_paquetes_poo():
    return [factory_paquete(p) for p in PAQUETES]

def paquetes_con_precio_poo():
    paquetes_obj = obtener_paquetes_poo()

    return [
        {
            "slug": p._data["slug"],
            "nombre": p.get_nombre(),
            "categoria": p.get_categoria(),
            "precio": p.get_precio(),
            "precio_final": p.calcular_precio_final(),
            "emoji": p._data["emoji"],
            "departamento": p._data["departamento"],
            "descripcion": p._data["descripcion"],
            "duracion_dias": p._data["duracion_dias"],
            "incluye": p._data["incluye"]
        }
        for p in paquetes_obj
    ]

app = Flask(__name__, template_folder="templates", static_folder="static")

app.secret_key = "mareva_secret_2026"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "MAREVA",
    "user": "postgres",
    "password": "1234"
}

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

def obtener_paquete_bd(slug):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id_paquete,
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
            personalizable,
            estado
        FROM paquete_turistico
        WHERE slug = %s
    """, (slug,))

    fila = cursor.fetchone()

    if not fila:
        cursor.close()
        conexion.close()
        return None

    paquete = {
        "id_paquete": fila[0],
        "nombre": fila[1],
        "slug": fila[2],
        "descripcion": fila[3],
        "precio": float(fila[4]),
        "duracion_dias": fila[5],
        "duracion_noches": fila[6],
        "cupos_totales": fila[7],
        "cupos_disponibles": fila[8],
        "fecha_inicio": fila[9],
        "fecha_fin": fila[10],
        "personalizable": fila[11],
        "estado": fila[12],
        "servicios_extra": []
    }

    cursor.execute("""
        SELECT
            id_servicio_extra,
            nombre,
            precio,
            descripcion
        FROM servicio_extra
        WHERE id_paquete = %s
          AND estado = TRUE
        ORDER BY id_servicio_extra
    """, (fila[0],))

    extras = cursor.fetchall()

    for extra in extras:
        paquete["servicios_extra"].append({
            "id_servicio_extra": extra[0],
            "nombre": extra[1],
            "precio": float(extra[2]),
            "descripcion": extra[3]
        })

    cursor.close()
    conexion.close()

    return paquete

def obtener_id_cliente(correo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_cliente
        FROM cliente
        WHERE correo = %s
          AND estado = TRUE
    """, (correo,))

    fila = cursor.fetchone()

    cursor.close()
    conexion.close()

    return fila[0] if fila else None

def generar_codigo_reserva():
    return "MAR-" + uuid.uuid4().hex[:10].upper()

@app.route("/")
def inicio():
    destacados = PAQUETES[:6]
    reserva_confirmada = session.pop("ultima_reserva", None)

    return render_template(
        "/principal/index.html",
        destacados=destacados,
        reserva_confirmada=reserva_confirmada
    )

@app.route("/paquetes")
def paquetes():
    query = request.args.get("q", "")
    paquetes_poo = paquetes_con_precio_poo()

    return render_template(
        "/cliente/paquetes.html",
        query=query,
        paquetes=paquetes_poo
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        correo = request.form.get("correo")
        password = request.form.get("password")

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_cliente,
                nombre,
                apellido,
                correo,
                contrasena
            FROM cliente
            WHERE correo = %s
              AND estado = TRUE
        """, (correo,))

        cliente = cursor.fetchone()

        cursor.close()
        conexion.close()

        if cliente and cliente[4] == password:

            session["usuario"] = {
                "id_cliente": cliente[0],
                "nombre": cliente[1],
                "apellido": cliente[2],
                "correo": cliente[3],
                "nivel": "Explorador",
                "insignias": []
            }

            next_url = request.args.get(
                "next",
                url_for("inicio")
            )

            return redirect(next_url)

        return render_template(
            "login.html",
            error="Correo o contraseña incorrectos."
        )

    return render_template("/principal/login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":

        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        correo = request.form.get("correo")
        password = request.form.get("password")
        tipo_documento = request.form.get("tipo_documento", "CC")
        numero_documento = request.form.get("numero_documento")

        if not numero_documento:
            return render_template(
                "/principal/registro.html",
                error="El número de documento es obligatorio."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                INSERT INTO cliente
                (
                    nombre,
                    apellido,
                    tipo_documento,
                    numero_documento,
                    correo,
                    contrasena,
                    rol
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'cliente')
                RETURNING id_cliente
            """, (
                nombre,
                apellido,
                tipo_documento,
                numero_documento,
                correo,
                password
            ))

            id_cliente = cursor.fetchone()[0]

            conexion.commit()

            session["usuario"] = {
                "id_cliente": id_cliente,
                "nombre": nombre,
                "apellido": apellido,
                "correo": correo,
                "nivel": "Explorador",
                "insignias": []
            }

            return redirect(url_for("inicio"))

        except Exception:
            conexion.rollback()

            return render_template(
                "/principal/registro.html",
                error="No fue posible crear la cuenta. Verifica que el correo y documento no estén registrados."
            )

        finally:
            cursor.close()
            conexion.close()

    return render_template("/principal/registro.html")

@app.route('/destinos')
def destinos():
    return render_template(
        '/cliente/destinos.html',
        destinos=DESTINOS
    )

@app.route('/detalle')
def detalle_paquete():

    paquete_recibido = request.args.get('nombre')

    if not paquete_recibido:
        return redirect(url_for('paquetes'))

    paquete_buscado = paquete_recibido.lower().strip()
    paquete = None

    for p in PAQUETES:
        nombre_paquete = p.get('nombre', '').lower()
        slug_paquete = p.get('slug', '').lower()

        if (
            paquete_buscado == slug_paquete
            or paquete_buscado == nombre_paquete
            or paquete_buscado in nombre_paquete
        ):
            paquete = p
            break

    if not paquete:
        return redirect(url_for('paquetes'))

    return render_template(
        '/cliente/detalle_paquete.html',
        paquete=paquete
    )

@app.route('/reserva/<slug>')
def reserva(slug):

    if 'usuario' not in session:
        return redirect(
            url_for('login') +
            f'?next=/reserva/{slug}'
        )

    paquete = obtener_paquete_bd(slug)

    if not paquete:
        return redirect(url_for('paquetes'))

    if paquete["estado"] != "activo":
        return redirect(url_for('paquetes'))

    if paquete["cupos_disponibles"] <= 0:
        return render_template(
            '/cliente/reserva.html',
            paquete=paquete,
            error="Este paquete no tiene cupos disponibles."
        )

    return render_template(
        '/cliente/reserva.html',
        paquete=paquete
    )

@app.route('/confirmar-reserva', methods=['POST'])
def confirmar_reserva():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    datos = request.form

    slug = datos.get('paquete')

    adultos = int(datos.get('adultos') or 0)
    menores = int(datos.get('menores') or 0)
    bebes = int(datos.get('bebes') or 0)

    if adultos < 1 or menores < 0 or bebes < 0:
        return redirect(url_for('reserva', slug=slug))

    cantidad_viajeros = adultos + menores + bebes

    fecha_inicio_texto = datos.get('fecha_inicio')
    dias = int(datos.get('dias') or 0)

    if not fecha_inicio_texto or dias < 1:
        return redirect(url_for('reserva', slug=slug))

    try:
        fecha_inicio = datetime.strptime(
            fecha_inicio_texto,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return redirect(url_for('reserva', slug=slug))

    paquete = obtener_paquete_bd(slug)

    if not paquete:
        return redirect(url_for('paquetes'))

    if paquete["estado"] != "activo":
        return redirect(url_for('paquetes'))

    if paquete["fecha_inicio"] and fecha_inicio < paquete["fecha_inicio"]:
        return render_template(
            '/cliente/reserva.html',
            paquete=paquete,
            error="La fecha seleccionada es anterior a las fechas permitidas para este paquete."
        )

    fecha_regreso = fecha_inicio + timedelta(days=dias - 1)

    if paquete["fecha_fin"] and fecha_regreso > paquete["fecha_fin"]:
        return render_template(
            '/cliente/reserva.html',
            paquete=paquete,
            error="La fecha de regreso supera la fecha máxima disponible para este paquete."
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT
                id_paquete,
                precio,
                cupos_disponibles,
                fecha_inicio,
                fecha_fin
            FROM paquete_turistico
            WHERE slug = %s
              AND estado = 'activo'
            FOR UPDATE
        """, (slug,))

        paquete_bd = cursor.fetchone()

        if not paquete_bd:
            conexion.rollback()
            return redirect(url_for('paquetes'))

        id_paquete = paquete_bd[0]
        precio_paquete = float(paquete_bd[1])
        cupos_disponibles = paquete_bd[2]
        fecha_inicio_bd = paquete_bd[3]
        fecha_fin_bd = paquete_bd[4]

        if fecha_inicio_bd and fecha_inicio < fecha_inicio_bd:
            conexion.rollback()

            return render_template(
                '/cliente/reserva.html',
                paquete=paquete,
                error="La fecha seleccionada no está disponible."
            )

        if fecha_fin_bd and fecha_regreso > fecha_fin_bd:
            conexion.rollback()

            return render_template(
                '/cliente/reserva.html',
                paquete=paquete,
                error="La fecha de regreso no está dentro del periodo disponible."
            )

        if cantidad_viajeros > cupos_disponibles:
            conexion.rollback()

            return render_template(
                '/cliente/reserva.html',
                paquete=paquete,
                error=f"Solo quedan {cupos_disponibles} cupos disponibles."
            )

        nombres_extras = datos.getlist("extras")

        total_extras = 0
        ids_extras = []

        if nombres_extras:
            cursor.execute("""
                SELECT
                    id_servicio_extra,
                    nombre,
                    precio
                FROM servicio_extra
                WHERE id_paquete = %s
                  AND estado = TRUE
                  AND nombre = ANY(%s)
            """, (id_paquete, nombres_extras))

            extras_bd = cursor.fetchall()

            for extra in extras_bd:
                ids_extras.append(extra[0])
                total_extras += float(extra[2])

        valor_paquete = precio_paquete * cantidad_viajeros
        valor_total = valor_paquete + total_extras

        correo = session["usuario"]["correo"]
        id_cliente = obtener_id_cliente(correo)

        if not id_cliente:
            conexion.rollback()

            return redirect(url_for('logout'))

        codigo = generar_codigo_reserva()

        cursor.execute("""
            INSERT INTO reserva
            (
                codigo_unico,
                fecha_viaje,
                estado,
                valor_referencial,
                cant_adultos,
                cant_menores,
                observaciones,
                id_cliente,
                id_paquete
            )
            VALUES
            (
                %s,
                %s,
                'solicitada',
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id_reserva
        """, (
            codigo,
            fecha_inicio,
            valor_total,
            adultos,
            menores,
            datos.get("notas"),
            id_cliente,
            id_paquete
        ))

        id_reserva = cursor.fetchone()[0]

        for id_extra in ids_extras:
            cursor.execute("""
                INSERT INTO reserva_servicio_extra
                (
                    id_reserva,
                    id_servicio_extra
                )
                VALUES (%s, %s)
            """, (
                id_reserva,
                id_extra
            ))

        cursor.execute("""
            UPDATE paquete_turistico
            SET cupos_disponibles = cupos_disponibles - %s
            WHERE id_paquete = %s
              AND cupos_disponibles >= %s
        """, (
            cantidad_viajeros,
            id_paquete,
            cantidad_viajeros
        ))

        if cursor.rowcount != 1:
            conexion.rollback()

            return render_template(
                '/cliente/reserva.html',
                paquete=paquete,
                error="Los cupos cambiaron mientras realizabas la reserva. Intenta nuevamente."
            )

        conexion.commit()

        session["ultima_reserva"] = {
            "codigo": codigo,
            "paquete": paquete["nombre"],
            "destino": next(
                (
                    p["destino"]
                    for p in PAQUETES
                    if p["slug"] == slug
                ),
                paquete["nombre"]
            ),
            "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_regreso": fecha_regreso.strftime("%Y-%m-%d"),
            "adultos": adultos,
            "menores": menores,
            "bebes": bebes,
            "viajeros": cantidad_viajeros,
            "valor_total": valor_total
        }

        return redirect(url_for('perfil'))

    except Exception:
        conexion.rollback()

        return render_template(
            '/cliente/reserva.html',
            paquete=paquete,
            error="No fue posible guardar la reserva. Verifica la conexión con PostgreSQL."
        )

    finally:
        cursor.close()
        conexion.close()

@app.route('/perfil')
def perfil():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    id_cliente = session["usuario"].get("id_cliente")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            r.id_reserva,
            r.codigo_unico,
            r.fecha_reserva,
            r.fecha_viaje,
            r.estado,
            r.valor_referencial,
            r.cant_adultos,
            r.cant_menores,
            r.observaciones,
            p.nombre,
            p.slug,
            p.duracion_dias,
            d.nombre AS destino
        FROM reserva r
        INNER JOIN paquete_turistico p
            ON r.id_paquete = p.id_paquete
        LEFT JOIN destino d
            ON p.id_destino = d.id_destino
        WHERE r.id_cliente = %s
        ORDER BY r.id_reserva DESC
    """, (id_cliente,))

    filas = cursor.fetchall()

    reservas = []

    for fila in filas:
        fecha_regreso = None

        if fila[3] and fila[11]:
            fecha_regreso = fila[3] + timedelta(
                days=fila[11] - 1
            )

        reservas.append({
            "id_reserva": fila[0],
            "codigo_unico": fila[1],
            "fecha_reserva": fila[2],
            "fecha_viaje": fila[3],
            "fecha_regreso": fecha_regreso,
            "estado": fila[4],
            "valor_total": float(fila[5] or 0),
            "adultos": fila[6],
            "menores": fila[7],
            "observaciones": fila[8],
            "nombre_paquete": fila[9],
            "slug": fila[10],
            "duracion_dias": fila[11],
            "destino": fila[12] or "Destino no especificado"
        })

    cursor.close()
    conexion.close()

    usuario = session["usuario"].copy()

    usuario["reservas"] = reservas
    usuario["cantidad_reservas"] = len(reservas)

    if reservas:
        usuario["ultima_reserva"] = reservas[0]
    else:
        usuario.pop("ultima_reserva", None)

    return render_template(
        '/cliente/perfil.html',
        usuario=usuario,
        reservas=reservas,
        cantidad_reservas=len(reservas)
    )

@app.route('/insignias')
def insignias():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template(
        '/cliente/insignias.html',
        usuario=session['usuario'],
        insignias=INSIGNIAS
    )

@app.route("/niveles")
def niveles():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template(
        '/cliente/niveles.html',
        usuario=session['usuario']
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

if __name__ == "__main__":
    app.run(debug=True)
