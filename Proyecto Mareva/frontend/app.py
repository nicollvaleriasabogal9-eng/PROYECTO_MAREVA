from flask import Flask, render_template, request, redirect, url_for, session
from abc import ABC, abstractmethod

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

@app.route("/")
def inicio():
    destacados = PAQUETES[:6]
    reserva_confirmada = session.pop("ultima_reserva", None)
    return render_template("index.html", destacados=destacados, reserva_confirmada=reserva_confirmada)

@app.route("/paquetes")
def paquetes():
    query = request.args.get("q", "")

    paquetes_poo = paquetes_con_precio_poo()

    return render_template(
        "paquetes.html",
        query=query,
        paquetes=paquetes_poo
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")
        # Usuario de prueba 
        if correo == "yadira@test.co" and password == "cliente_prueba":
            session["usuario"] = {
                "nombre": "Yadira",
                "apellido": "Narvaez",
                "correo": correo,
                "nivel": "Explorador",
                "insignias": []
            }
            next_url = request.args.get("next", url_for("inicio"))
            return redirect(next_url)
        return render_template("login.html", error="Correo o contraseña incorrectos.")
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        session["usuario"] = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "correo": request.form.get("correo"),
            "nivel": "Explorador",
            "insignias": []
        }
        return redirect(url_for("inicio"))
    return render_template("registro.html")

@app.route('/destinos')
def destinos():
    return render_template('destinos.html', destinos=DESTINOS)

@app.route('/detalle/<slug>')
def detalle_paquete(slug):
    paquete = next((p for p in PAQUETES if p['slug'] == slug), None)
    if not paquete:
        return redirect(url_for('paquetes'))
    return render_template('detalle_paquete.html', paquete=paquete)

@app.route('/reserva/<slug>')
def reserva(slug):
    if 'usuario' not in session:
        return redirect(url_for('login') + f'?next=/reserva/{slug}')
    paquete = next((p for p in PAQUETES if p['slug'] == slug), None)
    if not paquete:
        return redirect(url_for('paquetes'))
    return render_template('reserva.html', paquete=paquete)

@app.route('/confirmar-reserva', methods=['POST'])
def confirmar_reserva():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    datos = request.form
    session['ultima_reserva'] = {
        'paquete': datos.get('paquete'),
        'adultos': datos.get('adultos'),
        'menores': datos.get('menores'),
        'bebes': datos.get('bebes'),
    }
    return redirect(url_for('inicio'))

@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

if __name__ == "__main__":
    app.run(debug=True)
