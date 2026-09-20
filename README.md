# 🌊 MAREVA — Agencia de Viajes Digital

> Plataforma web para la organización de planes vacacionales personalizados en Colombia.
> Código del proyecto en la carpeta **`Mareva_Sustentacion/`**.

---

## 1. ¿Qué Problema Resuelve?

Hoy organizar unas vacaciones obliga a abrir decenas de pestañas: una para el tiquete, otra para el hotel, otra para las actividades. El resultado es desorden, tiempo perdido y gastos innecesarios.

**MAREVA** centraliza todo en un solo lugar: el usuario elige un destino, selecciona el paquete turístico, agrega servicios extra (buceo, kayak, senderismo nocturno…), aplica su seguro de viaje y confirma su reserva, sin salir de la plataforma. El administrador gestiona el catálogo desde el mismo sistema.

---

## 2. Usuarios del Sistema

| Rol | Descripción |
|---|---|
| **Cliente / Viajero** | Navega destinos, reserva paquetes, gestiona su perfil, guarda favoritos y acumula insignias |
| **Administrador** | Gestiona paquetes, destinos, proveedores, guías, niveles, reportes y audita el sistema |
| **Guía turístico** | Consulta su panel de viajes y actualiza el estado de las reservas asignadas |
| **Proveedor** | Consulta contratos y solicitudes de servicios |

---

## 3. Estructura del Proyecto

```
Mareva_Sustentacion/
├── backend/            → Aplicación Flask (N-Capas)
│   ├── config/         → Conexión a PostgreSQL
│   ├── controllers/    → Lógica de presentación (Flask)
│   ├── models/         → Entidades POO (Abstract Base Class + Factory)
│   ├── repositories/   → Persistencia (consultas SQL directas)
│   ├── routes/         → Definición de URLs (blueprints)
│   ├── services/       → Reglas de negocio
│   └── main.py         → Punto de entrada del servidor
├── frontend/           → HTML5 · CSS3 · JavaScript (Jinja2)
│   ├── static/         → CSS, JS, imágenes y videos
│   └── templates/      → Plantillas HTML
└── database/           → Scripts SQL y utilidades
    ├── mareva_unificado.sql        → Modelo completo + datos iniciales
    ├── migracion_caribe_2026.sql   → Migración de la versión Caribe
    └── hashear_passwords.py        → Hashea contraseñas en texto plano
```

---

## 4. Instalación y Ejecución

### Requisitos previos

- Python 3.10+
- PostgreSQL (se usan `psycopg[binary]` 3.x)
- Las dependencias del proyecto (`requirements.txt`)

### 4.1 Crear la base de datos

1. Crea una base de datos PostgreSQL (por ejemplo `mareva`).
2. Ejecuta el script de creación completo:

```sql
psql -U tu_usuario -d mareva -f database/mareva_unificado.sql
```

3. Si vienes de una base existente de la versión Caribe, aplica la migración:

```sql
psql -U tu_usuario -d mareva -f database/migracion_caribe_2026.sql
```

### 4.2 Crear y activar el entorno virtual

Entra a la carpeta del proyecto:

```bash
cd Mareva_Sustentacion
```

#### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### Windows (CMD)

```bat
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno esté activo, verás el nombre `(venv)` al inicio de la terminal.

### 4.3 Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4.4 Configurar `.env`

Crea un archivo `.env` en la raíz de `Mareva_Sustentacion/` (nunca lo subas al repositorio):

```env
DB_HOST=localhost
DB_NAME=mareva
DB_USER=postgres
DB_PASSWORD=tu_password
DB_PORT=5432
```

### 4.5 (Opcional) Hashear contraseñas legadas

Si la BD tiene contraseñas en texto plano, corre el script de hasheo (desde `backend/`):

```bash
cd backend
python ../database/hashear_passwords.py
```

### 4.6 Ejecutar la aplicación

El servidor se inicia desde la carpeta `backend/`:

```bash
cd backend
python main.py
```

### 4.7 Abrir el proyecto

Una vez iniciado el servidor, visita en tu navegador:

```
http://127.0.0.1:5000/
```

> **Nota:** el video de portada `videoinicio.mp4` (318 MB) supera el límite de archivos de GitHub (100 MB) por lo que **no se incluye en el repositorio**. Debe copiarse manualmente a `frontend/static/videos/` si se desea ese video en particular. El video alternativo `video_inicio2.mp4` sí está incluido.

---

## 5. Usuarios de Prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `nicoll@mareva.co` (o `cesar@mareva.co`, `andres@mareva.co`, `laura@mareva.co`, `sofia@mareva.co`) | `Admin_mareva01` |
| Cliente | `yadira@test.co` | `cliente_prueba` |
| Proveedor | (creado en `Proveedor_mareva01`) | `Proveedor_mareva01` |

---

## 6. Funcionalidades Principales

- Registro e inicio de sesión con hash de contraseña (werkzeug) y bloqueo por intentos fallidos
- Catálogo de **20 paquetes turísticos** con búsqueda, filtros (categoría, destino, duración, precio, incluye) y ordenamiento
- Detalle del paquete con calendario de salidas, servicios incluidos y extras opcionales
- **Comparador de paquetes** (hasta 3)
- **Favoritos**: agregar/quitar desde el catálogo, página de lista y contador en el navbar
- Flujo de reserva completo: selección de fecha, alojamiento, alimentación, transporte, actividades, seguro y extras
- Gestión de viajeros por reserva, confirmación en pantalla y **descarga de la reserva en PDF**
- Panel de administración: paquetes, destinos, niveles de gamificación, encuestas, reportes y reservas
- Perfil de usuario con nivel de gamificación e insignias
- Historial de búsqueda reutilizable
- **Encuestas de satisfacción** post-viaje
- Roles de guía turístico y proveedor (contratos y solicitudes)

---

## 7. Tecnologías Utilizadas

| Capa | Tecnología |
|---|---|
| **Frontend** | HTML5 · CSS3 · JavaScript (Jinja2) |
| **Backend** | Python 3 · Flask 3 |
| **Base de Datos** | PostgreSQL (psycopg 3) |
| **PDF** | ReportLab |
| **Patrón Backend** | Arquitectura N-Capas (Presentación → Negocio → Datos) |
| **Patrón OOP** | Abstract Base Class + Factory Method (clases `Playa`, `Aventura`, `Ecoturismo`, `Cultural`, `Ciudad`) |
| **Control de versiones** | Git / GitHub |
| **Gestión del proyecto** | GitHub Projects (Scrum) |

---

## 8. Arquitectura — N-Capas

El sistema está dividido en **6 capas**, agrupadas en FrontEnd y BackEnd:

```
╔══════════════════════════════════════════════════════╗
║  FRONTEND                                            ║
║  ┌───────────────────────────────────────────────┐  ║
║  │  Capa de Presentación  │  HTML5 · CSS3 · JS   │  ║
║  └───────────────────────────────────────────────┘  ║
╠══════════════════════════════════════════════════════╣
║  BACKEND                                             ║
║  ┌───────────────────────────────────────────────┐  ║
║  │  Capa de Aplicación    │  Flask (routes +     │  ║
║  │                        │  controllers)        │  ║
║  ├───────────────────────────────────────────────┤  ║
║  │  Capa de Negocio       │  Python · Flask      │  ║
║  │  (Services)            │                      │  ║
║  ├───────────────────────────────────────────────┤  ║
║  │  Capa de Datos         │  Python · POO        │  ║
║  │  (Models)              │                      │  ║
║  ├───────────────────────────────────────────────┤  ║
║  │  Capa de Persistencia  │  PostgreSQL          │  ║
║  │  (Repositories)        │                      │  ║
║  └───────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════╝
```

### Descripción de cada capa

| Capa | Ubicación | Responsabilidad |
|---|---|---|
| **Presentación** | `frontend/` (HTML · CSS · JS) | Muestra la interfaz y gestiona la interacción visual |
| **Aplicación** | `backend/routes/` y `backend/controllers/` | Define las URLs y recibe las solicitudes HTTP |
| **Negocio (Services)** | `backend/services/` | Reglas de negocio: validaciones, cálculos y procesamiento |
| **Datos (Models)** | `backend/models/` | Entidades POO del dominio (paquetes, clientes) |
| **Persistencia (Repositories)** | `backend/repositories/` | Comunicación directa con PostgreSQL |
| **Servicios Externos** | APIs de terceros | Conectores con el mundo exterior (en esta versión, proveedores y guías viven en la BD) |

### ¿Por qué elegimos Arquitectura N-Capas?

El equipo optó por esta arquitectura por dos razones fundamentales:

**1. Modificabilidad sin efecto cascada**
Al separar cada responsabilidad en su propia capa, cualquier cambio queda contenido sin propagarse al resto del sistema. Si se cambia PostgreSQL por otro motor de base de datos, solo se toca la capa de Persistencia. Si se rediseña la interfaz, la lógica de negocio y los repositorios permanecen intactos. Esto fue clave para un equipo de 5 personas trabajando en paralelo: cada integrante podía modificar su módulo sin romper el trabajo de los demás.

**2. Optimización y rendimiento del sistema**
La separación de responsabilidades permite identificar y optimizar cada capa de forma independiente. Si hay lentitud en las consultas, se interviene únicamente en los repositorios sin tocar los servicios ni las rutas. Esto hace que el sistema sea más fácil de auditar, depurar y escalar.

Esto garantiza:
- **Separación de responsabilidades** — los cambios en la BD no afectan la vista ni los servicios
- **Mantenibilidad** — cada módulo puede actualizarse de forma independiente
- **Escalabilidad** — nuevas funciones se agregan en la capa correcta sin romper las demás
- **Trabajo en equipo eficiente** — cada integrante trabaja sobre su capa sin generar conflictos

---

## 9. Base de Datos — Módulos

La base de datos final en PostgreSQL tiene **13 módulos** y más de **35 tablas**:

| # | Módulo | Tablas principales |
|---|---|---|
| 1 | **Gamificación** | `nivel`, `insignia`, `cliente_insignia` |
| 2 | **Clientes** | `cliente`, `referido` |
| 3 | **Destinos** | `destino` |
| 4 | **Proveedores** | `proveedor`, `metodo_pago_proveedor` |
| 5 | **Guías Turísticos** | `guia_turistico` |
| 6 | **Seguros** | `tipo_seguro`, `seguro`, `seguro_servicio` |
| 7 | **Servicios** | `alojamiento`, `alimentacion`, `transporte`, `actividad_turistica` |
| 8 | **Paquetes Turísticos** | `paquete_turistico`, `paquete_*` (4 tablas N:M), `servicio_extra` |
| 9 | **Promociones** | `promocion`, `promocion_insignia`, `promocion_nivel` |
| 10 | **Reservas** | `reserva`, `reserva_seguro`, `reserva_servicio_extra`, `viajero_reserva`, `itinerario_viaje`, `itinerario_actividad` |
| 11 | **Funcionalidades Cliente** | `favoritos`, `lista_suenos`, `historial_busqueda`, `notificacion` |
| 12 | **Encuestas** | `encuesta_pregunta`, `encuesta_respuesta` |
| 13 | **Auditoría** | `auditoria_admin` |

**Datos iniciales cargados:**
- 4 niveles de gamificación: Explorador → Aventurero → Viajero Elite → Embajador
- 5 insignias: Primera Aventura, Playero, Montañista, Viajero Frecuente, Referidor Estrella
- 20 destinos colombianos
- 20 paquetes turísticos
- 5 administradores + 1 cliente de prueba (`yadira@test.co`)
- Proveedores, guías turísticos, promociones y encuestas base

---

## 10. Patrón POO en el Backend

`backend/models/paquete.py` implementa **Abstract Base Class + Factory Method**:

```python
class PaqueteBase(ABC):
    @abstractmethod
    def calcular_precio_final(self): pass

class Playa(PaqueteBase):
    def calcular_precio_final(self): return self._data["precio"] * 1.10

class Aventura(PaqueteBase):
    def calcular_precio_final(self): return self._data["precio"] * 1.15

class Ecoturismo(PaqueteBase):
    def calcular_precio_final(self): return self._data["precio"] * 1.08

class Cultural(PaqueteBase):
    def calcular_precio_final(self): return self._data["precio"] * 0.95

def factory_paquete(paquete_dict):
    # retorna la subclase correcta según categoría
```

Cada categoría aplica un ajuste de precio diferente, y la factory decide qué clase instanciar sin que el resto del código lo sepa.

---

## 11. Rutas Flask Implementadas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Página principal (destacados, destinos, promociones) |
| GET | `/paquetes` | Catálogo con búsqueda, filtros y ordenamiento |
| GET | `/paquetes/<slug>` | Detalle de un paquete |
| GET | `/comparar` | Comparador de paquetes |
| GET/POST | `/login` | Inicio de sesión |
| GET/POST | `/registro` | Registro de nuevo usuario |
| GET | `/logout` | Cierra sesión |
| GET | `/favoritos` | Lista de paquetes favoritos |
| POST | `/favoritos/<id_paquete>/alternar` | Agrega/quita un favorito (AJAX) |
| GET | `/destinos` | Listado de destinos |
| GET | `/destinos/<id_destino>` | Detalle de un destino |
| GET | `/reserva/<slug>` | Formulario de reserva (requiere login) |
| POST | `/reserva/preparar/<slug>` | Prepara y valida la selección de la reserva |
| POST | `/reserva/guardar/<slug>` | Guarda la reserva |
| GET | `/reserva/confirmacion` | Confirmación de reserva |
| GET | `/reserva/confirmacion/pdf` | Descarga la reserva en PDF |
| GET | `/perfil` | Perfil del usuario logueado (reservas, historial, niveles) |
| GET | `/admin/dashboard` | Panel del administrador |
| POST | `/admin/paquetes/suspender` | Suspende/activa paquetes |
| POST | `/admin/reservas/<id_reserva>/reembolso` | Marca reembolso de una reserva |
| GET | `/admin/encuestas/reporte` | Reporte de encuestas |

---

## 12. Metodología de Desarrollo

**Scrum**

---

## 13. Integrantes

| Nombre | Rol |
|---|---|
| Nicoll Valeria Sabogal | Lider del proyecto |
| Sofía Munevar | Tester |
| Laura Rubiano | Análisis de requisitos |
| César Uzcátegui | Diseñadora UX/UI |
| Andrés Aroca | Desarrollador |

---

## 14. Estado Actual del Proyecto

✅ Requisitos funcionales y no funcionales  
✅ Historias de usuario  
✅ Modelo Entidad-Relación (MER) y modelo lógico  
✅ Script SQL final PostgreSQL (13 módulos, 35+ tablas, datos iniciales)  
✅ Aplicación Flask conectada a PostgreSQL  
✅ Sistema de autenticación con hash de contraseñas y bloqueo por intentos fallidos  
✅ Catálogo de paquetes con Factory Method  
✅ Flujo completo de reservas con persistencia en BD y PDF  
✅ Favoritos, comparador, historial y perfil de cliente  
✅ Paneles de administración, guía y proveedor  
✅ Encuestas post-viaje y reportes  
✅ Repositorio colaborativo en GitHub

---

## 15. Bootcamp

**SENA — Arquitectura de Software**  
Inicio: 25 de abril de 2026