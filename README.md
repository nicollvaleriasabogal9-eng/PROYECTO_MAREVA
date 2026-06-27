# 🌊 MAREVA — Agencia de Viajes Digital

> Plataforma web para la organización de planes vacacionales personalizados en Colombia.

---

## 1. ¿Qué Problema Resuelve?

Hoy organizar unas vacaciones obliga a abrir decenas de pestañas: una para el tiquete, otra para el hotel, otra para las actividades. El resultado es desorden, tiempo perdido y gastos innecesarios.

**MAREVA** centraliza todo en un solo lugar: el usuario elige un destino, selecciona el paquete turístico, agrega servicios extra (buceo, kayak, senderismo nocturno…), aplica su seguro de viaje y confirma su reserva, sin salir de la plataforma. El administrador gestiona el catálogo desde el mismo sistema.

---

## 2. Usuarios del Sistema

| Rol | Descripción |
|---|---|
| **Cliente / Viajero** | Navega destinos, reserva paquetes, gestiona su perfil y acumula insignias |
| **Administrador** | Gestiona paquetes, proveedores, guías, promociones y audita el sistema |

---

## 3. Funcionalidades Principales

- Registro e inicio de sesión (con bloqueo por intentos fallidos)
- Catálogo de **20 paquetes turísticos** con filtro por categoría y búsqueda
- Detalle del paquete con servicios incluidos y extras opcionales
- Flujo de reserva con selección de viajeros, seguro y observaciones
- Perfil de usuario con nivel de gamificación e insignias
- Sistema de **referidos** entre clientes
- **Lista de sueños** (ahorro programado hacia un paquete)
- Favoritos, historial de búsqueda, notificaciones
- **Encuestas de satisfacción** post-viaje
- Auditoría de acciones del administrador

---

## 4. Tecnologías Utilizadas

| Capa | Tecnología |
|---|---|
| **Frontend** | HTML5 · CSS3 · JavaScript |
| **Backend** | Python 3 · Flask |
| **Base de Datos** | PostgreSQL |
| **Patrón Backend** | Arquitectura N-Capas (Presentación → Negocio → Datos) |
| **Patrón OOP** | Abstract Base Class + Factory Method (clases `Playa`, `Aventura`, `Ecoturismo`, `Cultural`) |
| **Control de versiones** | Git / GitHub |
| **Gestión del proyecto** | GitHub Projects (Scrum) |

---

## 5. Arquitectura — N-Capas

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
║  ├───────────────────────────────────────────────┤  ║
║  │  Servicios Externos    │  APIs de terceros    │  ║
║  │  (Adapters)            │                      │  ║
║  └───────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════╝
```

### Descripción de cada capa

| Capa | Tecnología | Responsabilidad |
|---|---|---|
| **Presentación** | HTML5 · CSS3 · JavaScript | Muestra la interfaz al usuario y gestiona la interacción visual |
| **Aplicación** | Flask (routes · controllers) | Actúa como intermediaria entre el FrontEnd y la lógica de negocio. Define las URLs y recibe las solicitudes HTTP |
| **Negocio (Services)** | Python · Flask | Contiene las reglas de negocio del sistema: validaciones, cálculos y procesamiento de información |
| **Datos (Models)** | Python · POO | Representa las entidades de la base de datos, define atributos y relaciones entre tablas |
| **Persistencia (Repositories)** | PostgreSQL | Se encarga de la comunicación directa con la base de datos: consultas, inserciones y actualizaciones |
| **Servicios Externos (Adapters)** | APIs de terceros | Conectores con servicios externos. Actúan como intermediarios entre la aplicación y el mundo exterior |

### ¿Por qué elegimos Arquitectura N-Capas?

El equipo optó por esta arquitectura por dos razones fundamentales:

**1. Modificabilidad sin efecto cascada**
Al separar cada responsabilidad en su propia capa, cualquier cambio queda contenido sin propagarse al resto del sistema. Si se cambia PostgreSQL por otro motor de base de datos, solo se toca la capa de Persistencia. Si se rediseña la interfaz, la lógica de negocio y los repositorios permanecen intactos. Si se agrega un nuevo servicio externo, basta con crear un nuevo adapter sin modificar nada más. Esto fue clave para un equipo de 5 personas trabajando en paralelo: cada integrante podía modificar su módulo sin romper el trabajo de los demás.

**2. Optimización y rendimiento del sistema**
La separación de responsabilidades permite identificar y optimizar cada capa de forma independiente. Si hay lentitud en las consultas, se interviene únicamente en los repositorios sin tocar los servicios ni las rutas. Si hay un cuello de botella en la lógica de negocio, se refactoriza esa capa sin afectar la vista. Esto hace que el sistema sea más fácil de auditar, depurar y escalar a medida que crezca el catálogo de paquetes o la base de clientes.

Esto garantiza:
- **Separación de responsabilidades** — los cambios en la BD no afectan la vista ni los servicios
- **Mantenibilidad** — cada módulo puede actualizarse de forma independiente
- **Escalabilidad** — nuevas funciones se agregan en la capa correcta sin romper las demás
- **Trabajo en equipo eficiente** — cada integrante trabaja sobre su capa sin generar conflictos

---

## 6. Base de Datos — Módulos

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
- 5 proveedores, 3 guías, 3 promociones, 6 encuestas base

---

## 7. Diagrama de Componentes

El sistema sigue una arquitectura cliente-servidor donde:

- El **navegador** consume las rutas Flask (`/`, `/paquetes`, `/login`, `/reserva/<slug>`, etc.)
- El **backend Flask** contiene los controladores, servicios (POO con factory) y adaptadores
- Los **repositorios** se conectan a **PostgreSQL** para persistir clientes, reservas y paquetes
- Los **proveedores externos** (seguros, guías) son entidades de la BD, no servicios externos en esta versión

---

## 8. Patrón POO en el Backend

`app.py` implementa **Abstract Base Class + Factory Method**:

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

## 9. Rutas Flask Implementadas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Página principal con 6 destacados |
| GET | `/paquetes` | Catálogo completo con búsqueda |
| GET | `/destinos` | Listado de los 20 destinos |
| GET | `/detalle/<slug>` | Detalle de un paquete |
| GET/POST | `/login` | Inicio de sesión |
| GET/POST | `/registro` | Registro de nuevo usuario |
| GET | `/reserva/<slug>` | Formulario de reserva (requiere login) |
| POST | `/confirmar-reserva` | Procesa la reserva |
| GET | `/perfil` | Perfil del usuario logueado |
| GET | `/logout` | Cierra sesión |

---

## 10. Metodología de Desarrollo

**Scrum**

---

## 11. Integrantes

| Nombre | Rol |
|---|---|
| Nicoll Valeria Sabogal | Lider del proyecto |
| Sofía Munevar | Tester |
| Laura Rubiano | Análisis de requisitos |
| César Uzcátegui | Diseñadora UX/UI |
| Andrés Aroca | Desarrollador |

---

## 12. Estado Actual del Proyecto

✅ Requisitos funcionales y no funcionales  
✅ Historias de usuario  
✅ Modelo Entidad-Relación (MER) y modelo lógico  
✅ Script SQL final PostgreSQL (13 módulos, 35+ tablas, datos iniciales)  
✅ Prototipos HTML/CSS/JS funcionales  
✅ Backend Flask con rutas y POO implementadas  
✅ Sistema de sesiones (login/registro/logout)  
✅ Catálogo de paquetes con Factory Method  
✅ Repositorio colaborativo en GitHub  

🚧 En desarrollo:  
- Conexión real Flask ↔ PostgreSQL  
- Sistema de autenticación con hash de contraseña  
- Panel de administración  
- Integración completa de reservas en BD  

---

## 13. Bootcamp

**SENA — Arquitectura de Software**  
Inicio: 25 de abril de 2026
