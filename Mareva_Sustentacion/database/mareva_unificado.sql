BEGIN;


-- MÓDULO 1: GAMIFICACIÓN — NIVELES ---

CREATE TABLE nivel (
    id_nivel             SERIAL PRIMARY KEY,
    nombre               VARCHAR(50)   NOT NULL,
    min_monto            NUMERIC(12,2) NOT NULL DEFAULT 0,
    min_reservas         INT           NOT NULL DEFAULT 0,
    descripcion          TEXT,
    porcentaje_descuento NUMERIC(5,2)  DEFAULT 0
);

-- MÓDULO 2: CLIENTES---

CREATE TABLE cliente (
    id_cliente        SERIAL PRIMARY KEY,
    nombre            VARCHAR(50)  NOT NULL,
    apellido          VARCHAR(50)  NOT NULL,
    tipo_documento    VARCHAR(30)  NOT NULL,
    numero_documento  VARCHAR(30)  NOT NULL UNIQUE,
    telefono          VARCHAR(20),
    correo            VARCHAR(100) NOT NULL UNIQUE,
    contrasena        VARCHAR(255) NOT NULL,
    rol               VARCHAR(20)  NOT NULL DEFAULT 'cliente',
    codigo_referido   VARCHAR(20)  UNIQUE,
    fecha_registro    DATE         NOT NULL DEFAULT CURRENT_DATE,
    estado            BOOLEAN      NOT NULL DEFAULT TRUE,
    intentos_fallidos INT          NOT NULL DEFAULT 0,
    bloqueado_hasta   TIMESTAMP,
    acepta_politica_no_reembolso BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_aceptacion_politica TIMESTAMP,
    version_politica  VARCHAR(20) NOT NULL DEFAULT '1.0',
    id_nivel          INT REFERENCES nivel(id_nivel),
    CONSTRAINT chk_cliente_rol CHECK (rol IN ('admin', 'cliente', 'guia'))
);

--- Referidos entre clientes---
CREATE TABLE referido (
    id_referido         SERIAL PRIMARY KEY,
    fecha_referido      DATE        NOT NULL DEFAULT CURRENT_DATE,
    puntos_ganados      INT         NOT NULL DEFAULT 0,
    estado              VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    id_referidor        INT NOT NULL REFERENCES cliente(id_cliente),
    id_referido_cliente INT NOT NULL REFERENCES cliente(id_cliente),
    UNIQUE (id_referidor, id_referido_cliente),
    CONSTRAINT chk_referido_estado    CHECK (estado IN ('pendiente','completado','cancelado')),
    CONSTRAINT chk_no_autoreferido    CHECK (id_referidor <> id_referido_cliente)
);

-- MÓDULO 3: DESTINOS---

CREATE TABLE destino (
    id_destino       SERIAL PRIMARY KEY,
    nombre_destino   VARCHAR(100) NOT NULL,
    departamento     VARCHAR(100),
    ciudad           VARCHAR(100),
    categoria        VARCHAR(50),
    descripcion      TEXT,
    atracciones      TEXT,
docs_requeridos  TEXT,
    imagen_principal VARCHAR(255),
    video_url        VARCHAR(255),
    estado           BOOLEAN NOT NULL DEFAULT TRUE
);


---MÓDULO 4: PROVEEDORES---

CREATE TABLE proveedor (
    id_proveedor      SERIAL PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    nit               VARCHAR(30) UNIQUE,
    tipo_empresa      VARCHAR(50),
    descripcion       TEXT,
    ciudad            VARCHAR(100),
    telefono          VARCHAR(20),
    correo            VARCHAR(100) UNIQUE,
    contrasena        VARCHAR(255) NOT NULL,
    nombre_contacto   VARCHAR(100),
    telefono_contacto VARCHAR(20),
    correo_contacto   VARCHAR(100),
    estado            BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE metodo_pago_proveedor (
    id_metodo_proveedor SERIAL PRIMARY KEY,
    id_proveedor        INT NOT NULL REFERENCES proveedor(id_proveedor) ON DELETE CASCADE,
    tipo_metodo         VARCHAR(50)  NOT NULL,
    entidad             VARCHAR(100),
    titular             VARCHAR(150),
    numero_referencia   VARCHAR(100),
    instrucciones       TEXT,
    CONSTRAINT chk_tipo_metodo CHECK (
        tipo_metodo IN ('cuenta_bancaria','nequi','daviplata','efectivo','tarjeta','otro')
    )
);


--- MÓDULO 5: GUÍAS TURÍSTICOS---


CREATE TABLE guia_turistico (
    id_guia      SERIAL PRIMARY KEY,
    nombre       VARCHAR(50)  NOT NULL,
    apellido     VARCHAR(50)  NOT NULL,
    idiomas      VARCHAR(200),
    especialidad VARCHAR(200),
    telefono     VARCHAR(20),
    correo       VARCHAR(100),
    contrasena        VARCHAR(255) NOT NULL,
    estado       BOOLEAN NOT NULL DEFAULT TRUE
);

--- MÓDULO 6: SEGUROS---

CREATE TABLE tipo_seguro (
    id_tipo_seguro   SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    descripcion      TEXT,
    cobertura_general TEXT
);

CREATE TABLE seguro (
    id_seguro      SERIAL PRIMARY KEY,
    id_tipo_seguro INT NOT NULL REFERENCES tipo_seguro(id_tipo_seguro),
    nombre         VARCHAR(100)  NOT NULL,
    cobertura      TEXT          NOT NULL,
    precio         NUMERIC(10,2) NOT NULL DEFAULT 0,
    es_obligatorio BOOLEAN       NOT NULL DEFAULT FALSE,
    descripcion    TEXT,
    estado         BOOLEAN       NOT NULL DEFAULT TRUE
);

--- MÓDULO 7: SERVICIOS (Alojamiento, Alimentación, Transporte, Actividad)---

CREATE TABLE alojamiento (
    id_alojamiento   SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    tipo_alojamiento VARCHAR(50),
    ciudad           VARCHAR(100),
    servicios        TEXT,
    id_proveedor     INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE alimentacion (
    id_alimentacion SERIAL PRIMARY KEY,
    restaurante     VARCHAR(100),
    tipo_comida     VARCHAR(100),
    tipo_servicio   VARCHAR(50),
    incluye_bebidas BOOLEAN       NOT NULL DEFAULT FALSE,
    precio          NUMERIC(10,2),
    id_proveedor    INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE transporte (
    id_transporte SERIAL PRIMARY KEY,
    tipo          VARCHAR(50),
    empresa       VARCHAR(100),
    ruta          VARCHAR(200),
    capacidad     INT,
    hora_salida   TIME,
    hora_regreso  TIME,
    fecha_inicio  DATE,
    fecha_fin     DATE,
    id_proveedor  INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE actividad_turistica (
    id_actividad   SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    tipo           VARCHAR(100),
    duracion_horas NUMERIC(4,1),
    costo          NUMERIC(10,2),
    id_destino     INT REFERENCES destino(id_destino),
    id_guia        INT REFERENCES guia_turistico(id_guia),
    id_proveedor   INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE seguro_servicio (
    id_seguro_servicio SERIAL PRIMARY KEY,
    id_seguro          INT NOT NULL REFERENCES seguro(id_seguro) ON DELETE CASCADE,
    id_alojamiento     INT REFERENCES alojamiento(id_alojamiento)     ON DELETE CASCADE,
    id_alimentacion    INT REFERENCES alimentacion(id_alimentacion)   ON DELETE CASCADE,
    id_transporte      INT REFERENCES transporte(id_transporte)       ON DELETE CASCADE,
    id_actividad       INT REFERENCES actividad_turistica(id_actividad) ON DELETE CASCADE,
    CONSTRAINT chk_solo_un_servicio CHECK (
        (id_alojamiento  IS NOT NULL)::INT +
        (id_alimentacion IS NOT NULL)::INT +
        (id_transporte   IS NOT NULL)::INT +
        (id_actividad    IS NOT NULL)::INT = 1
    ),
    UNIQUE (id_seguro, id_alojamiento),
    UNIQUE (id_seguro, id_alimentacion),
    UNIQUE (id_seguro, id_transporte),
    UNIQUE (id_seguro, id_actividad)
);


--- MÓDULO 8: PAQUETES TURÍSTICOS---


CREATE TABLE paquete_turistico (
    id_paquete        SERIAL PRIMARY KEY,
    nombre            VARCHAR(100)  NOT NULL,
    slug              VARCHAR(100)  NOT NULL UNIQUE,
    imagen_url        VARCHAR(255),
    descripcion       TEXT,
    precio            NUMERIC(10,2) NOT NULL,
    duracion_dias     INT,
    duracion_noches   INT,
    cupos_totales     INT           NOT NULL DEFAULT 0,
    cupos_disponibles INT           NOT NULL DEFAULT 0,
    fecha_inicio      DATE,
    fecha_fin         DATE,
    imagen_principal  VARCHAR(255),
    personalizable    BOOLEAN       NOT NULL DEFAULT FALSE,
    estado            VARCHAR(20)   NOT NULL DEFAULT 'activo',
    id_destino        INT REFERENCES destino(id_destino),
id_guia           INT REFERENCES guia_turistico(id_guia),
    emoji             VARCHAR(10) DEFAULT '🧳',
    video_url         VARCHAR(255),

    CONSTRAINT chk_paquete_estado
        CHECK (estado IN ('activo','suspendido')),

    CONSTRAINT chk_cupos
        CHECK (cupos_disponibles <= cupos_totales)
);

-- Servicios que componen el paquete (tablas N:M)---
CREATE TABLE paquete_transporte (
    id_paquete    INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_transporte INT NOT NULL REFERENCES transporte(id_transporte),
    PRIMARY KEY (id_paquete, id_transporte)
);

CREATE TABLE paquete_alojamiento (
    id_paquete     INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_alojamiento INT NOT NULL REFERENCES alojamiento(id_alojamiento),
    PRIMARY KEY (id_paquete, id_alojamiento)
);

CREATE TABLE paquete_alimentacion (
    id_paquete      INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_alimentacion INT NOT NULL REFERENCES alimentacion(id_alimentacion),
    PRIMARY KEY (id_paquete, id_alimentacion)
);

CREATE TABLE paquete_actividad (
    id_paquete   INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_actividad INT NOT NULL REFERENCES actividad_turistica(id_actividad),
    PRIMARY KEY (id_paquete, id_actividad)
);

--- Servicios extras opcionales dentro del paquete---
CREATE TABLE servicio_extra (
    id_servicio_extra SERIAL PRIMARY KEY,
    nombre            VARCHAR(100)  NOT NULL,
    precio            NUMERIC(10,2) NOT NULL,
    descripcion       TEXT,
    estado            BOOLEAN       NOT NULL DEFAULT TRUE,
    id_paquete        INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE
);

CREATE TABLE contrato
(
    id_contrato              SERIAL PRIMARY KEY,
    id_proveedor             INTEGER NOT NULL,
    id_paquete               INTEGER NOT NULL,
    descripcion_terminos     TEXT NOT NULL,
    fecha_inicio             DATE,
    fecha_fin                DATE,
    condiciones_comerciales  TEXT,
    estado_contrato          VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_creacion           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    respuesta_proveedor      VARCHAR(20),
    fecha_respuesta          TIMESTAMP,
    firma_proveedor          BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_firma              TIMESTAMP,
    metodo_firma             VARCHAR(50),

    CONSTRAINT contrato_proveedor_fkey
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor)
        ON DELETE CASCADE,

    CONSTRAINT contrato_paquete_fkey
        FOREIGN KEY (id_paquete)
        REFERENCES paquete_turistico(id_paquete)
        ON DELETE CASCADE,

    CONSTRAINT contrato_estado_check
        CHECK (
            estado_contrato IN (
                'pendiente',
                'aceptado',
                'rechazado',
                'vigente',
                'vencido'
            )
        ),

    CONSTRAINT contrato_respuesta_check
        CHECK (
            respuesta_proveedor IS NULL
            OR respuesta_proveedor IN ('aceptado', 'rechazado')
        ),

    CONSTRAINT contrato_fechas_check
        CHECK (
            fecha_fin IS NULL
            OR fecha_inicio IS NULL
            OR fecha_fin >= fecha_inicio
        )
);

CREATE TABLE documento
(
    id_documento       SERIAL PRIMARY KEY,
    id_contrato        INTEGER,
    id_proveedor       INTEGER NOT NULL,
    nombre_documento   VARCHAR(150) NOT NULL,
    tipo_documento     VARCHAR(50),
    url_documento      VARCHAR(500),
    fecha_carga        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado_documento   VARCHAR(20) NOT NULL DEFAULT 'pendiente',

    CONSTRAINT documento_contrato_fkey
        FOREIGN KEY (id_contrato)
        REFERENCES contrato(id_contrato)
        ON DELETE CASCADE,

    CONSTRAINT documento_proveedor_fkey
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor)
        ON DELETE CASCADE,

    CONSTRAINT documento_estado_check
        CHECK (
            estado_documento IN (
                'pendiente',
                'aprobado',
                'rechazado'
            )
        )
);


--- MÓDULO 9: PROMOCIONES---


CREATE TABLE promocion (
    id_promocion   SERIAL PRIMARY KEY,
    codigo         VARCHAR(30)   NOT NULL UNIQUE,
    descuento      NUMERIC(5,2)  NOT NULL,
    descripcion    TEXT,
    fecha_inicio   DATE,
    fecha_fin      DATE,
    tipo_promocion VARCHAR(30),
    id_paquete     INT REFERENCES paquete_turistico(id_paquete),
    CONSTRAINT chk_descuento CHECK (descuento > 0 AND descuento <= 100)
);

--- Promoción disponible según nivel del cliente (N:M)---
CREATE TABLE promocion_nivel (
    id_promocion INT NOT NULL REFERENCES promocion(id_promocion) ON DELETE CASCADE,
    id_nivel     INT NOT NULL REFERENCES nivel(id_nivel)         ON DELETE CASCADE,
    PRIMARY KEY (id_promocion, id_nivel)
);

-- ============================================================
-- NUEVA ARQUITECTURA DE SALIDAS
-- ============================================================
-- paquete_turistico = qué se vende
-- salida_paquete   = cuándo sale + guía asignado
-- Los cupos permanecen en BD por compatibilidad, pero NO se
-- muestran en la interfaz del cliente.

CREATE TABLE salida_paquete (
    id_salida SERIAL PRIMARY KEY,
    id_paquete INT NOT NULL
        REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    fecha_salida DATE NOT NULL,
    fecha_regreso DATE NOT NULL,
    cupos_totales INT NOT NULL DEFAULT 0,
    cupos_disponibles INT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'programada',
    id_guia INT REFERENCES guia_turistico(id_guia),
    observaciones TEXT,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_salida_fechas CHECK (
        fecha_regreso >= fecha_salida
    ),
    CONSTRAINT chk_salida_cupos CHECK (
        cupos_totales >= 0
        AND cupos_disponibles >= 0
        AND cupos_disponibles <= cupos_totales
    ),
    CONSTRAINT chk_salida_estado CHECK (
        estado IN (
            'programada','disponible','agotada',
            'cerrada','cancelada'
        )
    ),
    CONSTRAINT uq_salida_paquete_fecha
        UNIQUE (id_paquete, fecha_salida)
);

CREATE INDEX idx_salida_paquete ON salida_paquete(id_paquete);
CREATE INDEX idx_salida_fecha ON salida_paquete(fecha_salida);
CREATE INDEX idx_salida_estado ON salida_paquete(estado);
CREATE INDEX idx_salida_guia ON salida_paquete(id_guia);


-- MÓDULO 10: RESERVAS---


CREATE TABLE reserva (
    id_reserva          SERIAL PRIMARY KEY,
    codigo_unico        VARCHAR(30)   NOT NULL UNIQUE,
    fecha_reserva       DATE          NOT NULL DEFAULT CURRENT_DATE,
    fecha_viaje         DATE,
    estado              VARCHAR(30)   NOT NULL DEFAULT 'solicitada',
    valor_referencial   NUMERIC(12,2),
    precio_total        NUMERIC(12,2),
    cant_adultos        INT           NOT NULL DEFAULT 1,
    cant_menores        INT           NOT NULL DEFAULT 0,
    observaciones       TEXT,
    acepta_no_reembolso BOOLEAN       NOT NULL DEFAULT FALSE,
    plan                 TEXT,
    alergias             TEXT,
    mascotas             BOOLEAN      NOT NULL DEFAULT FALSE,
    metodo_contacto     VARCHAR(30),
    guia_pdf             VARCHAR(255),
    id_cliente          INT NOT NULL
        REFERENCES cliente(id_cliente),
    id_paquete          INT NOT NULL
        REFERENCES paquete_turistico(id_paquete),
    id_salida           INT REFERENCES salida_paquete(id_salida),
    CONSTRAINT chk_reserva_estado
        CHECK (
            estado IN ('solicitada', 'confirmada', 'en_proceso', 'completada', 'cancelada')
        ),
    CONSTRAINT chk_cant_adultos
        CHECK (cant_adultos >= 1),
    CONSTRAINT chk_cant_menores
        CHECK (cant_menores >= 0)
);

--- Seguro adicional opcional que el cliente agrega a su reserva---
CREATE TABLE reserva_seguro (
    id_reserva_seguro  SERIAL PRIMARY KEY,
    id_reserva         INT NOT NULL REFERENCES reserva(id_reserva)  ON DELETE CASCADE,
    id_seguro          INT NOT NULL REFERENCES seguro(id_seguro)     ON DELETE CASCADE,
    precio_aplicado    NUMERIC(10,2) NOT NULL,
    fecha_contratacion DATE          NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (id_reserva, id_seguro)
);

--- Servicios extra opcionales que el cliente agrega a su reserva---
CREATE TABLE reserva_servicio_extra (
    id_reserva        INT NOT NULL REFERENCES reserva(id_reserva)             ON DELETE CASCADE,
    id_servicio_extra INT NOT NULL REFERENCES servicio_extra(id_servicio_extra),
    PRIMARY KEY (id_reserva, id_servicio_extra)
);

--- Viajeros registrados en la reserva---
CREATE TABLE viajero_reserva (
    id_viajero       SERIAL PRIMARY KEY,
    nombre           VARCHAR(50) NOT NULL,
    apellido         VARCHAR(50) NOT NULL,
    tipo_documento   VARCHAR(30) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    id_reserva       INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

--- Itinerario de traslados de la reserva---
CREATE TABLE itinerario_viaje (
    id_itinerario    SERIAL PRIMARY KEY,
    origen           VARCHAR(100),
    destino          VARCHAR(100),
    fecha_salida     DATE,
    fecha_regreso    DATE,
    hora_salida      TIME,
    hora_regreso     TIME,
    medio_transporte VARCHAR(50),
    id_reserva       INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

--- Actividades diarias del itinerario de la reserva---
CREATE TABLE itinerario_actividad (
    id_itin_actividad  SERIAL PRIMARY KEY,
    dia                INT,
    hora_inicio        TIME,
    lugar              VARCHAR(200),
    descripcion        TEXT,
    costos_adicionales NUMERIC(10,2) DEFAULT 0,
    id_actividad       INT REFERENCES actividad_turistica(id_actividad),
    id_reserva         INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

--- MÓDULO 11: FUNCIONALIDADES DEL CLIENTE---


CREATE TABLE favoritos (
    id_favorito    SERIAL PRIMARY KEY,
    fecha_agregado DATE NOT NULL DEFAULT CURRENT_DATE,
    id_cliente     INT NOT NULL REFERENCES cliente(id_cliente)         ON DELETE CASCADE,
    id_paquete     INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    UNIQUE (id_cliente, id_paquete)
);

CREATE TABLE lista_suenos (
    id_sueno            SERIAL PRIMARY KEY,
    fecha_inicio_ahorro DATE,
    meta_semanal        NUMERIC(10,2),
    meta_mensual        NUMERIC(10,2),
    id_cliente          INT NOT NULL REFERENCES cliente(id_cliente)         ON DELETE CASCADE,
    id_paquete          INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    UNIQUE (id_cliente, id_paquete)
);

CREATE TABLE historial_busqueda (
    id_busqueda     SERIAL PRIMARY KEY,
    destino_buscado VARCHAR(100),
    filtros         JSONB,
    fecha_busqueda  TIMESTAMP NOT NULL DEFAULT NOW(),
    id_cliente      INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE notificacion (
    id_notificacion SERIAL PRIMARY KEY,
    tipo            VARCHAR(50),
    mensaje         TEXT,
    fecha           TIMESTAMP NOT NULL DEFAULT NOW(),
    leida           BOOLEAN   NOT NULL DEFAULT FALSE,
    id_cliente      INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE
);


--- MÓDULO 12: ENCUESTAS DE SATISFACCIÓN ---

CREATE TABLE encuesta_pregunta (
    id_pregunta    SERIAL PRIMARY KEY,
    texto          TEXT        NOT NULL,
    tipo_respuesta VARCHAR(50) NOT NULL,
    orden          INT         NOT NULL,
    estado         BOOLEAN     NOT NULL DEFAULT TRUE
);

--- Una fila por respuesta (pregunta + reserva + cliente)---
CREATE TABLE encuesta_respuesta (
    id_respuesta      SERIAL PRIMARY KEY,
    id_pregunta       INT NOT NULL REFERENCES encuesta_pregunta(id_pregunta) ON DELETE CASCADE,
    id_reserva        INT NOT NULL REFERENCES reserva(id_reserva)            ON DELETE CASCADE,
    id_cliente        INT NOT NULL REFERENCES cliente(id_cliente)            ON DELETE CASCADE,
    respuesta_texto   TEXT,
    respuesta_numero  INT,
    fecha             TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_pregunta, id_reserva, id_cliente)
);


--- MÓDULO 13: ADMINISTRACIÓN Y AUDITORÍA---


CREATE TABLE auditoria_admin (
    id_auditoria SERIAL PRIMARY KEY,
    accion       VARCHAR(100) NOT NULL,
    descripcion  TEXT,
    fecha        TIMESTAMP NOT NULL DEFAULT NOW(),
    id_admin     INT NOT NULL REFERENCES cliente(id_cliente)
);

--- ÍNDICES---


--- Cliente---
CREATE INDEX idx_cliente_correo      ON cliente(correo);
CREATE INDEX idx_cliente_documento   ON cliente(numero_documento);
CREATE INDEX idx_cliente_nivel       ON cliente(id_nivel);

--- Reserva---
CREATE INDEX idx_reserva_cliente     ON reserva(id_cliente);
CREATE INDEX idx_reserva_paquete     ON reserva(id_paquete);
CREATE INDEX idx_reserva_estado      ON reserva(estado);
CREATE INDEX idx_reserva_fecha_viaje ON reserva(fecha_viaje);

--- Paquete ---
CREATE INDEX idx_paquete_destino     ON paquete_turistico(id_destino);
CREATE INDEX idx_paquete_estado      ON paquete_turistico(estado);
CREATE INDEX idx_paquete_fecha       ON paquete_turistico(fecha_inicio);

--- Seguro ---
CREATE INDEX idx_seguro_servicio     ON seguro_servicio(id_seguro);
CREATE INDEX idx_reserva_seguro      ON reserva_seguro(id_reserva);

--- Proveedor ---
CREATE INDEX idx_metodo_proveedor    ON metodo_pago_proveedor(id_proveedor);

--- Funcionalidades cliente ---
CREATE INDEX idx_historial_cliente   ON historial_busqueda(id_cliente);
CREATE INDEX idx_notif_cliente       ON notificacion(id_cliente);
CREATE INDEX idx_favoritos_cliente   ON favoritos(id_cliente);

--- Promoción ---
CREATE INDEX idx_promocion_codigo    ON promocion(codigo);

--- Auditoría ---
CREATE INDEX idx_auditoria_admin     ON auditoria_admin(id_admin);


--- DATOS INICIALES ---

--- Niveles ---
INSERT INTO nivel (nombre, min_monto, min_reservas, descripcion, porcentaje_descuento) VALUES
('Explorador',    0,        0,  'Nivel inicial para nuevos viajeros',   0.00),
('Aventurero',    2000000,  2,  'Viajeros con experiencia',             5.00),
('Viajero Elite', 6000000,  5,  'Acceso a promociones exclusivas',     10.00),
('Embajador',     15000000, 10, 'El nivel más alto de MAREVA',         15.00);

--- Admins y cliente de prueba ---
-- NOTA: las contraseñas se guardan con hash (werkzeug scrypt), tal como las verifica
-- services/auth_services.py. Contraseña real para iniciar sesión con cualquier admin: Admin_mareva01
-- Contraseña real de Yadira (cliente de prueba): cliente_prueba
INSERT INTO cliente (nombre, apellido, tipo_documento, numero_documento, telefono, correo, contrasena, rol, codigo_referido, acepta_politica_no_reembolso, fecha_aceptacion_politica, version_politica) VALUES
('Cesar',  'Uzcategui', 'CC', '1000000001', '3100000001', 'cesar@mareva.co',  'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin',   NULL, TRUE, CURRENT_TIMESTAMP, '1.0'),
('Andres', 'Aroca',     'CC', '1000000002', '3100000002', 'andres@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin',   NULL, TRUE, CURRENT_TIMESTAMP, '1.0'),
('Laura',  'Rubiano',   'CC', '1000000003', '3100000003', 'laura@mareva.co',  'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin',   NULL, TRUE, CURRENT_TIMESTAMP, '1.0'),
('Sofia',  'Munevar',   'CC', '1000000004', '3100000004', 'sofia@mareva.co',  'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin',   NULL, TRUE, CURRENT_TIMESTAMP, '1.0'),
('Nicoll', 'Sabogal',   'CC', '1000000005', '3100000005', 'nicoll@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin',   NULL, TRUE, CURRENT_TIMESTAMP, '1.0'),
('Yadira', 'Narvaez',   'CC', '2000000001', '3200000001', 'yadira@test.co',   'scrypt:32768:8:1$OsPW9JDKU8BF6uy1$c12dc8e295c68587bcc6ff01fcfd1357c394d46c95a19957ec6c2f84b771ef91b9a2191af9a552289ff05fc3301822519acf4c3c1a536efc88f71ee52886e235', 'cliente', 'YN20261', TRUE, CURRENT_TIMESTAMP, '1.0');

--- Destinos (20 destinos para los 20 paquetes) ---
INSERT INTO destino (nombre_destino, departamento, ciudad, categoria, descripcion, atracciones, imagen_principal, estado) VALUES
('Cartagena de Indias', 'Bolívar',    'Cartagena',    'playa',    'Ciudad amurallada Patrimonio de la Humanidad con playas caribeñas.',    'Ciudad Amurallada, Islas del Rosario, Castillo de San Felipe, Bocagrande',  'img/destinos/cartagena_indias.jpeg',        TRUE),
('Medellín',            'Antioquia',  'Medellín',     'ciudad',   'La ciudad de la eterna primavera, innovadora y cultural.',             'El Poblado, Metro Cable, Pueblito Paisa, Museo de Antioquia',              'img/destinos/medellin.jpeg',         TRUE),
('Guatapé',             'Antioquia',  'Guatapé',      'aventura', 'Pueblo colorido con la imponente Piedra del Peñol.',                   'La Piedra del Peñol, Embalse de Guatapé, Zócalos pintados',                'img/destinos/guatape.jpeg',          TRUE),
('San Andrés',          'San Andrés', 'San Andrés',   'playa',    'El mar de los siete colores en el Caribe colombiano.',                 'Hoyo Soplador, Johnny Cay, La Piscinita, El Acuario',                      'img/destinos/san_andres.jpeg',       TRUE),
('Parque Tayrona',      'Magdalena',  'Santa Marta',  'playa',    'Naturaleza salvaje: selva tropical y playas vírgenes.',                'Cabo San Juan, Playa Cristal, Arrecifes, Pueblito',                        'img/destinos/tayrona.jpeg',          TRUE),
('Valle del Cocora',    'Quindío',    'Salento',      'montaña',  'Hogar de las palmas de cera, árbol nacional de Colombia.',             'Palmas de Cera, Salento, Finca El Ocaso, Mirador',                         'img/destinos/cocora.jpeg',    TRUE),
('Barichara',           'Santander',  'Barichara',    'cultural', 'El pueblo más bonito de Colombia, arquitectura colonial.',             'Catedral de la Inmaculada, Camino Real, Capilla de Santa Bárbara',         'img/destinos/barichara.jpg',        TRUE),
('Leticia',             'Amazonas',   'Leticia',      'aventura', 'Puerta de entrada a la Amazonía colombiana.',                          'Parque Amacayacu, Isla de los Micos, Reserva Tanimboca',                   'img/destinos/leticia.jpeg',          TRUE),
('Caño Cristales',      'Meta',       'La Macarena',  'aventura', 'El río más hermoso del mundo, famoso por sus colores únicos.',         'Río Caño Cristales, Pozos naturales, Senderismo, Miradores',               'img/destinos/caño_cristales.jpeg',   TRUE),
('Eje Cafetero',        'Quindío',    'Armenia',      'cultural', 'Paisaje Cultural Cafetero, Patrimonio de la Humanidad.',               'Fincas cafeteras, Parque del Café, Pueblos patrimonio, Jeep willys',       'img/destinos/eje_cafetero.jpeg',     TRUE),
('Nuquí',               'Chocó',      'Nuquí',        'playa',    'Paraíso del Pacífico colombiano, avistamiento de ballenas jorobadas.', 'Playas vírgenes, Avistamiento ballenas, Manglares, Termas',                'img/destinos/nuqui.jpeg',            TRUE),
('Barichara Colonial',  'Santander',  'Barichara',    'cultural', 'Arquitectura colonial de piedra y el Camino Real hacia Guane.',        'Catedral Inmaculada, Capilla de Jesús, Camino Real, Guane',                'img/destinos/barichara_colonial.jpg',TRUE),
('Las Lajas',           'Nariño',     'Ipiales',      'cultural', 'Basílica neogótica construida sobre un cañón, ícono religioso.',       'Basílica Las Lajas, Puente, Cascadas, Laguna La Cocha',                    'img/destinos/lajas.jpeg',        TRUE),
('Villa de Leyva',      'Boyacá',     'Villa de Leyva','cultural','Plaza empedrada más grande de Colombia, arquitectura colonial.',        'Plaza Mayor, Museo del Desierto, Pozos Azules, Ráquira',                   'img/destinos/leyva.jpeg',   TRUE),
('Cañón del Chicamocha','Santander',  'San Gil',      'aventura', 'Capital colombiana de los deportes extremos y paisajes épicos.',       'Teleférico, Rafting, Parapente, Parque Chicamocha',                        'img/destinos/cañon_chicamocha.jpeg',       TRUE),
('Mompox',              'Bolívar',    'Mompox',       'cultural', 'Ciudad Patrimonio de la Humanidad a orillas del río Magdalena.',       'Calle Real, Iglesias coloniales, Orfebrería, Festival de Jazz',             'img/destinos/mompox.jpeg',           TRUE),
('Sierra Nevada',       'Magdalena',  'Santa Marta',  'aventura', 'La montaña costera más alta del mundo y territorios indígenas.',       'Ciudad Perdida, Comunidades Kogi, Caminatas, Biodiversidad',               'img/destinos/sierra_nevada.jpeg',    TRUE),
('Tolú y Coveñas',      'Sucre',      'Tolú',         'playa',    'Playas tranquilas del Caribe colombiano, ideal para el descanso.',     'Playas Tolú, Islas de San Bernardo, Motonáutica, Manglar',                 'img/destinos/tolu.jpeg',     TRUE),
('Isla Gorgona',        'Cauca',      'Guapi',        'aventura', 'Parque Nacional Natural, antigua prisión y reserva marina única.',     'Buceo, Avistamiento ballenas, Senderismo, Biodiversidad marina',            'img/destinos/gorgona.jpeg',          TRUE),
('Capurganá',           'Chocó',      'Acandí',       'playa',    'Pueblo caribeño sin carreteras, paraíso de buceadores.',              'Playa La Caleta, Sapzurro, Arrecifes de coral, Senderismo',                'img/destinos/capurgana.jpeg',        TRUE);

--- Proveedores---
-- Contraseña real para iniciar sesión como cualquier proveedor: Proveedor_mareva01
INSERT INTO proveedor (nombre, nit, tipo_empresa, descripcion, ciudad, telefono, correo, contrasena, nombre_contacto, telefono_contacto) 
VALUES
('Hotel Las Américas', '800100200-1', 'Hotel', 'Hotel 5 estrellas en Cartagena', 'Cartagena', '6056543210', 'reservas@lasamericas.co', 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0', 'María Torres', '3001234567'),
('Avianca', '860002964-4', 'Aerolínea', 'Aerolínea nacional', 'Bogotá', '018000953434', 'grupos@avianca.com', 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0', 'Carlos Reyes', '3009876543'),
('CocoraTours', '900567890-3', 'Operador', 'Tours en el Quindío', 'Salento', '3145678901', 'info@cocoratours.co', 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0', 'Juliana Ríos', '3145678901');

--- Métodos de pago de proveedores ---
INSERT INTO metodo_pago_proveedor (id_proveedor, tipo_metodo, entidad, titular, numero_referencia, instrucciones) VALUES
(1, 'cuenta_bancaria', 'Bancolombia', 'Hotel Las Americas SAS', '12345678901', 'Transferir y enviar comprobante al correo del proveedor'),
(2, 'nequi',           'Nequi',       'CocoraTours',            '3001234567',  NULL),
(3, 'daviplata',       'Daviplata',   'CocoraTours',            '3209876543',  NULL);

--- Guías turísticos ---
-- Contraseña real de Andrés: Guia123 · Valentina: GuiaTuristica123 · Miguel: (ya venía hasheada en el original)
INSERT INTO guia_turistico (nombre, apellido, idiomas, especialidad, telefono, correo, contrasena, estado) VALUES
('Andrés',    'Herrera',  'Español, Inglés',           'Cartagena histórica y playas',  '3100001111', 'andres.guia@mareva.co', 'scrypt:32768:8:1$DyUDJeiqrqIuCpOb$c8e99c7e7eae986e4f6d2a06188601687d96ef43f38ed10b1b20d509281d86ecc902d75b7e08e9e3fa89ba25a5488612376dd97555c73a42c92a5a40967a8576',    TRUE),
('Valentina', 'López',    'Español, Inglés, Francés',  'Ecoturismo y naturaleza',       '3100002222', 'valentina.guia@mareva.co', 'scrypt:32768:8:1$BmwNjfSVYTonnYPl$05a81a5f442d6ef99062a3bab28179e8759d28727f20d5639d0c0da82319c4de3dab02c1075708d912f3bbb36f0030e287088a39228453a5bda98cd01ffe92c3', TRUE),
('Miguel',    'Castillo', 'Español',                   'Aventura y deportes extremos',  '3100003333', 'miguel.guia@mareva.co', 'scrypt:32768:8:1$AELZ8i2lbW4gWGaS$c93d8a0d0ce87f2c85e74f63337cb6d60ead433feddece2e6a1311fdb52d633596f8d755fb690f34d34a2b7e1344066ea5a3978567b5d0509b827ca2905d387b',   TRUE);

--- Tipos de seguro ---
INSERT INTO tipo_seguro (nombre, descripcion, cobertura_general) VALUES
('Responsabilidad Civil', 'Seguro obligatorio por ley para prestadores de servicios turísticos',   'Cubre daños a terceros dentro de las instalaciones o durante el servicio'),
('Asistencia Médica',     'Seguro opcional de salud para el viajero',                             'Cubre emergencias médicas, hospitalización y asistencia en viaje'),
('Cancelación y Equipaje','Seguro opcional contra imprevistos del viaje',                          'Cubre cancelaciones, pérdida o daño de equipaje');

--- Seguros específicos ---
INSERT INTO seguro (id_tipo_seguro, nombre, cobertura, precio, es_obligatorio, descripcion, estado) VALUES
(1, 'RC Alojamiento',     'Accidentes dentro del alojamiento hasta $50.000.000',  0,      TRUE,  'Obligatorio — incluido en el costo del alojamiento',  TRUE),
(1, 'RC Transporte',      'Accidentes durante el traslado hasta $50.000.000',     0,      TRUE,  'Obligatorio — incluido en el costo del transporte',   TRUE),
(1, 'RC Actividad',       'Accidentes durante la actividad hasta $30.000.000',    0,      TRUE,  'Obligatorio — incluido en el costo de la actividad',  TRUE),
(2, 'Seguro Médico Básico','Emergencias médicas y hospitalización hasta $80.000.000', 120000, FALSE, 'Recomendado para viajes nacionales',                TRUE),
(2, 'Seguro Médico Completo','Médico, dental y evacuación hasta $200.000.000',    280000, FALSE, 'Cobertura amplia recomendada',                        TRUE),
(3, 'Seguro Premium',     'Cancelación, equipaje y médico hasta $500.000.000',    520000, FALSE, 'Máxima protección para tu viaje',                     TRUE);

--- Paquetes turísticos (20 paquetes)---
INSERT INTO paquete_turistico (nombre,slug,imagen_url,descripcion,precio,duracion_dias,duracion_noches,cupos_totales,cupos_disponibles,fecha_inicio,fecha_fin,imagen_principal,personalizable,estado,id_destino,id_guia) 
VALUES
('Cartagena Mágica','cartagena-magica','img/paquetes/Cartagena.jpeg','Descubre la ciudad amurallada con playas privadas e historia colonial.', 1850000, 5, 4, 20, 14,'2026-07-01', '2026-07-05','img/paquetes/Cartagena.jpeg',TRUE, 'activo', 1, 1),
('Medellín Innovadora','medellin-innovadora','img/paquetes/Medellin.jpeg','Conoce la ciudad más transformadora de América Latina.',1200000, 4, 3, 25, 20,'2026-07-10', '2026-07-13','img/paquetes/Medellin.jpeg',FALSE, 'activo', 2, 2),
('Guatapé Extremo','guatape-extremo','img/paquetes/Guatape.jpeg','Adrenalina pura: sube la Piedra del Peñol y navega el embalse.',890000, 3, 2, 15, 12,'2026-07-15', '2026-07-17','img/paquetes/Guatape.jpeg',TRUE, 'activo', 3, 3),
('San Andrés Todo Incluido','san-andres-todo-incluido','img/paquetes/SanAndres.jpeg','El mar de los siete colores con todo incluido en resort 5 estrellas.',3200000, 7, 6, 30, 18,'2026-08-01', '2026-08-07','img/paquetes/SanAndres.jpeg',FALSE, 'activo', 4, 1),
('Tayrona Salvaje','tayrona-salvaje','img/paquetes/Tayrona.jpeg','Selva, playas vírgenes y ecosistemas únicos en el Parque Tayrona.',1450000, 5, 4, 12, 8,'2026-08-10', '2026-08-14','img/paquetes/Tayrona.jpeg',TRUE, 'activo', 5, 2),
('Valle del Cocora Místico','valle-del-cocora-mistico','img/paquetes/Cocora.jpeg','Caminata entre palmas de cera y fincas cafeteras del Quindío.',980000, 3, 2, 20, 15,'2026-09-01', '2026-09-03','img/paquetes/Cocora.jpeg',FALSE, 'activo', 6, 3),
('Amazonas Aventura','amazonas-aventura','img/paquetes/Amazonas.jpeg','Explora la selva amazónica y conoce comunidades indígenas.',2750000, 6, 5, 18, 14,'2026-09-10', '2026-09-15','img/paquetes/Amazonas.jpeg',TRUE, 'activo', 8, 1),
('Desierto de la Tatacoa','desierto-de-la-tatacoa','img/paquetes/Desierto.jpeg','Observación astronómica y recorridos por paisajes únicos.',750000, 3, 2, 20, 16,'2026-09-20', '2026-09-22','img/paquetes/Desierto.jpeg',FALSE, 'activo', 8, 2),
('Caño Cristales Premium','cano-cristales-premium','img/paquetes/Caño.jpeg','Visita el río más hermoso del mundo con guía especializado.',2950000, 5, 4, 15, 10,'2026-10-01', '2026-10-05','img/paquetes/Caño.jpeg',TRUE, 'activo', 9, 3),
('Eje Cafetero Tradicional','eje-cafetero-tradicional','img/paquetes/EjeCafetero.jpeg','Recorrido por fincas cafeteras y pueblos patrimonio.',1350000, 4, 3, 25, 18,'2026-10-10', '2026-10-13','img/paquetes/EjeCafetero.jpeg',FALSE, 'activo', 10, 1),
('Nuquí Ecoturismo','nuqui-ecoturismo','img/paquetes/Nuqui.jpeg','Avistamiento de ballenas y playas vírgenes del Pacífico.',2400000, 5, 4, 16, 12,'2026-10-20', '2026-10-24','img/paquetes/Nuqui.jpeg',TRUE, 'activo', 11, 2),
('Barichara Colonial','barichara-colonial','img/paquetes/Barichara.jpg','Conoce uno de los pueblos más bellos de Colombia.',890000, 3, 2, 20, 17,'2026-11-01', '2026-11-03','img/paquetes/Barichara.jpg',FALSE, 'activo', 12, 3),
('Santuario Las Lajas','santuario-las-lajas','img/paquetes/Santuario.jpeg','Recorrido religioso y cultural por Nariño.',680000, 3, 2, 22, 19,'2026-11-08', '2026-11-10','img/paquetes/Santuario.jpeg',FALSE, 'activo', 13, 1),
('Boyacá Histórica','boyaca-historica','img/paquetes/BOYaca.jpeg','Villa de Leyva, Ráquira y monumentos históricos.',980000, 4, 3, 24, 20,'2026-11-15', '2026-11-18','img/paquetes/BOYaca.jpeg',TRUE, 'activo', 14, 2),
('Cañón del Chicamocha','canon-del-chicamocha','img/paquetes/CañonChica.jpeg','Deportes extremos y paisajes espectaculares.',1150000, 4, 3, 18, 13,'2026-11-25', '2026-11-28','img/paquetes/CañonChica.jpeg',TRUE, 'activo', 15, 3),
('Mompox Patrimonial','mompox-patrimonial','img/paquetes/Mompox.jpg','Historia, arquitectura colonial y cultura ribereña.',1250000, 4, 3, 20, 16,'2026-12-01', '2026-12-04','img/paquetes/Mompox.jpg',FALSE, 'activo', 16, 1),
('Sierra Nevada Ancestral','sierra-nevada-ancestral','img/paquetes/CierraNevada.jpeg','Conexión con comunidades indígenas y naturaleza.',2100000, 5, 4, 14, 10,'2026-12-10', '2026-12-14','img/paquetes/CierraNevada.jpeg',TRUE, 'activo', 17, 2),
('Tolú y Coveñas Relax','tolu-y-covenas-relax','img/paquetes/Tolu.jpeg','Playas tranquilas y actividades acuáticas.',1100000, 4, 3, 26, 21,'2026-12-18', '2026-12-21','img/paquetes/Tolu.jpeg',FALSE, 'activo', 18, 3),
('Isla Gorgona Explorer','isla-gorgona-explorer','img/paquetes/Isla.jpeg','Naturaleza, senderismo y biodiversidad marina.',2800000, 5, 4, 12, 8,'2027-01-10', '2027-01-14','img/paquetes/Isla.jpeg',TRUE, 'activo', 19, 1),
('Capurganá Paraíso','capurgana-paraiso','img/paquetes/Capurgana.jpeg','Playas cristalinas y ecoturismo en el Caribe colombiano.',1900000, 5, 4, 18, 13,'2027-01-20', '2027-01-24','img/paquetes/Capurgana.jpeg',TRUE, 'activo', 20, 2);

--- Servicios extra por paquete---
INSERT INTO servicio_extra (nombre, precio, descripcion, estado, id_paquete) VALUES
('Snorkel en Islas del Rosario',   180000, 'Equipo incluido, 3 horas',            TRUE, 1),
('Foto profesional en la Muralla', 120000, 'Sesión de 1 hora con fotógrafo',      TRUE, 1),
('Kayak en el embalse',             95000, 'Kayak doble 2 horas',                 TRUE, 3),
('Rappel en La Piedra',            140000, 'Equipo y seguro de escalada',          TRUE, 3),
('Buceo certificado',              350000, 'Bautismo de buceo 2 inmersiones',      TRUE, 5),
('Senderismo nocturno',            120000, 'Guía nocturno 4 horas',               TRUE, 5);

--- Promociones ---
INSERT INTO promocion (codigo, descuento, descripcion, fecha_inicio, fecha_fin, tipo_promocion, id_paquete) VALUES
('VERANO10',  10.00, '10% de descuento temporada de verano', '2026-06-01', '2026-07-31', 'temporal', 1),
('PAREJA20',  20.00, '20% para parejas en San Andrés',       '2026-07-01', '2026-08-31', 'especial', 4),
('MOCHILA15', 15.00, '15% para viajeros aventureros',        '2026-07-01', '2026-09-30', 'temporal', 5);

--- Preguntas de encuesta ---
INSERT INTO encuesta_pregunta (texto, tipo_respuesta, orden, estado) VALUES
('¿Cómo calificarías la calidad general del paquete?',       'calificacion', 1, TRUE),
('¿Qué tan satisfecho estás con el servicio del proveedor?', 'calificacion', 2, TRUE),
('¿El proceso de reserva en MAREVA fue fácil y claro?',      'calificacion', 3, TRUE),
('¿Recomendarías MAREVA a un amigo o familiar?',             'calificacion', 4, TRUE),
('Cuéntanos qué fue lo mejor de tu experiencia:',            'texto',        5, TRUE),
('¿Qué podríamos mejorar?',                                  'texto',        6, TRUE);


-- ============================================================
-- SALIDAS INICIALES: una por cada paquete existente
-- ============================================================

INSERT INTO salida_paquete
(
    id_paquete,
    fecha_salida,
    fecha_regreso,
    cupos_totales,
    cupos_disponibles,
    estado,
    id_guia,
    observaciones
)
SELECT
    id_paquete,
    fecha_inicio,
    fecha_fin,
    cupos_totales,
    cupos_disponibles,
    CASE
        WHEN fecha_inicio >= CURRENT_DATE THEN 'disponible'
        ELSE 'cerrada'
    END,
    id_guia,
    'Salida inicial generada desde la programación original del paquete.'
FROM paquete_turistico
WHERE fecha_inicio IS NOT NULL
  AND fecha_fin IS NOT NULL;

-- ============================================================
-- SALIDAS ADICIONALES PROGRAMADAS: varias por mes y por paquete
-- Genera 4 salidas mensuales (los días 5, 12, 19 y 26) durante
-- 6 meses para cada paquete, de modo que el cliente tenga un
-- calendario real con varias fechas para elegir.
-- ============================================================

INSERT INTO salida_paquete
(
    id_paquete,
    fecha_salida,
    fecha_regreso,
    cupos_totales,
    cupos_disponibles,
    estado,
    id_guia,
    observaciones
)
SELECT
    p.id_paquete,
    fechas.salida,
    (fechas.salida + (p.duracion_dias - 1) * INTERVAL '1 day')::date AS fecha_regreso,
    p.cupos_totales,
    p.cupos_disponibles,
    'programada',
    p.id_guia,
    'Salida programada automáticamente para dar varias opciones de fecha.'
FROM paquete_turistico p
CROSS JOIN LATERAL (
    SELECT
        (date_trunc('month', CURRENT_DATE)
         + (m - 1) * INTERVAL '1 month'
         + (dia - 1) * INTERVAL '1 day')::date AS salida
    FROM generate_series(1, 6) m,
         generate_series(5, 26, 7) dia
) fechas
WHERE p.estado = 'activo'
  AND NOT EXISTS (
      SELECT 1
      FROM salida_paquete sp
      WHERE sp.id_paquete = p.id_paquete
        AND sp.fecha_salida = fechas.salida
  );

COMMIT;

-- ============================================================
-- HOTELES / ALOJAMIENTOS
-- ============================================================

INSERT INTO alojamiento
(nombre, tipo_alojamiento, ciudad, servicios, id_proveedor)
SELECT
    v.nombre,
    v.tipo,
    v.ciudad,
    v.servicios,
    p.id_proveedor
FROM (
    VALUES
    ('Hotel Caribe Plaza','Hotel','Cartagena',
     'Piscina, WiFi, desayuno, aire acondicionado, recepción 24 horas','Hotel Las Américas'),

    ('Hotel Colonial Cartagena','Hotel Boutique','Cartagena',
     'Desayuno, WiFi, piscina, restaurante, servicio de habitaciones','Hotel Las Américas'),

    ('Hotel Poblado Central','Hotel','Medellín',
     'WiFi, desayuno, gimnasio, restaurante, aire acondicionado','Hotel Las Américas'),

    ('Hotel Primavera Medellín','Hotel','Medellín',
     'Desayuno, WiFi, restaurante, recepción 24 horas','Hotel Las Américas'),

    ('Hotel Guatapé Lago','Hotel','Guatapé',
     'Vista al embalse, desayuno, WiFi, restaurante, parqueadero','Hotel Las Américas'),

    ('Hostería Piedra del Peñol','Hostería','Guatapé',
     'Desayuno, WiFi, terraza, restaurante, actividades acuáticas','Hotel Las Américas'),

    ('Decameron San Andrés','Resort','San Andrés',
     'Todo incluido, piscina, playa privada, restaurantes, bar','Hotel Las Américas'),

    ('Hotel Coral Caribe','Hotel','San Andrés',
     'Piscina, desayuno, WiFi, restaurante, acceso a playa','Hotel Las Américas'),

    ('Ecohotel Tayrona','Ecohotel','Santa Marta',
     'Desayuno, senderismo, restaurante, zonas verdes, WiFi','Hotel Las Américas'),

    ('Cabañas Cabo San Juan','Cabaña','Santa Marta',
     'Alojamiento ecológico, restaurante, acceso a playa, senderos','Hotel Las Américas'),

    ('Hotel Salento Real','Hotel','Salento',
     'Desayuno, WiFi, restaurante, parqueadero, jardín','Hotel Las Américas'),

    ('Finca Cafetera Cocora','Finca','Salento',
     'Desayuno, tour cafetero, zonas verdes, WiFi, parqueadero','Hotel Las Américas'),

    ('Hotel Amazonas','Hotel','Leticia',
     'Piscina, restaurante, desayuno, WiFi, excursiones','Hotel Las Américas'),

    ('Eco Lodge Selva Amazónica','Eco Lodge','Leticia',
     'Alojamiento ecológico, alimentación, excursiones, senderismo','Hotel Las Américas'),

    ('Hotel Desierto Tatacoa','Hotel','Villavieja',
     'Piscina, restaurante, desayuno, observación astronómica','Hotel Las Américas'),

    ('Ecohostal La Tatacoa','Hostal','Villavieja',
     'Zona de camping, restaurante, terraza, observatorio astronómico','Hotel Las Américas'),

    ('Hotel Caño Cristales','Hotel','La Macarena',
     'Desayuno, restaurante, WiFi, excursiones, guía local','Hotel Las Américas'),

    ('Ecohotel Río Guayabero','Ecohotel','La Macarena',
     'Alojamiento ecológico, alimentación, senderismo, zonas verdes','Hotel Las Américas'),

    ('Hotel Eje Cafetero','Hotel','Armenia',
     'Piscina, desayuno, WiFi, gimnasio, restaurante','Hotel Las Américas'),

    ('Finca Cafetera Armenia','Finca','Armenia',
     'Desayuno, tour cafetero, jardín, restaurante, parqueadero','Hotel Las Américas'),

    ('Hotel Nuquí Pacífico','Hotel','Nuquí',
     'Desayuno, restaurante, acceso a playa, WiFi, excursiones','Hotel Las Américas'),

    ('Eco Lodge Nuquí','Eco Lodge','Nuquí',
     'Alojamiento ecológico, alimentación, playa, senderismo','Hotel Las Américas'),

    ('Hotel Barichara Colonial','Hotel','Barichara',
     'Desayuno, WiFi, piscina, restaurante, terraza','Hotel Las Américas'),

    ('Casa Colonial Barichara','Casa Hotel','Barichara',
     'Desayuno, jardín, WiFi, terraza, restaurante','Hotel Las Américas'),

    ('Hotel Las Lajas','Hotel','Ipiales',
     'Desayuno, WiFi, restaurante, parqueadero, recepción 24 horas','Hotel Las Américas'),

    ('Hotel Santuario Nariño','Hotel','Ipiales',
     'Desayuno, restaurante, WiFi, parqueadero, servicio de habitaciones','Hotel Las Américas'),

    ('Hotel Villa de Leyva','Hotel','Villa de Leyva',
     'Desayuno, WiFi, restaurante, jardín, parqueadero','Hotel Las Américas'),

    ('Posada Colonial Boyacá','Posada','Villa de Leyva',
     'Desayuno, chimenea, jardín, WiFi, restaurante','Hotel Las Américas'),

    ('Hotel Chicamocha','Hotel','San Gil',
     'Piscina, desayuno, WiFi, restaurante, actividades extremas','Hotel Las Américas'),

    ('Hotel Aventura Santander','Hotel','San Gil',
     'Desayuno, restaurante, WiFi, parqueadero, deportes extremos','Hotel Las Américas'),

    ('Hotel Mompox Real','Hotel','Mompox',
     'Desayuno, WiFi, restaurante, piscina, terraza','Hotel Las Américas'),

    ('Casa Colonial Mompox','Casa Hotel','Mompox',
     'Desayuno, jardín, WiFi, restaurante, terraza','Hotel Las Américas'),

    ('Hotel Sierra Nevada','Hotel','Santa Marta',
     'Desayuno, WiFi, restaurante, piscina, excursiones','Hotel Las Américas'),

    ('Eco Lodge Sierra Nevada','Eco Lodge','Santa Marta',
     'Alojamiento ecológico, alimentación, senderismo, guía local','Hotel Las Américas'),

    ('Hotel Tolú Caribe','Hotel','Tolú',
     'Piscina, desayuno, restaurante, acceso a playa, WiFi','Hotel Las Américas'),

    ('Hotel Coveñas Beach','Resort','Coveñas',
     'Piscina, playa, desayuno, restaurante, actividades acuáticas','Hotel Las Américas'),

    ('Ecohotel Gorgona','Ecohotel','Guapi',
     'Alojamiento ecológico, alimentación, senderismo, excursiones','Hotel Las Américas'),

    ('Cabañas Isla Gorgona','Cabaña','Guapi',
     'Alimentación, acceso a playa, senderismo, zonas naturales','Hotel Las Américas'),

    ('Hotel Capurganá Caribe','Hotel','Acandí',
     'Desayuno, restaurante, WiFi, acceso a playa, excursiones','Hotel Las Américas'),

    ('Eco Lodge Capurganá','Eco Lodge','Acandí',
     'Alojamiento ecológico, alimentación, playa, buceo, senderismo','Hotel Las Américas')
) AS v(nombre,tipo,ciudad,servicios,proveedor)
JOIN proveedor p
    ON p.nombre = v.proveedor
WHERE NOT EXISTS (
    SELECT 1
    FROM alojamiento a
    WHERE a.nombre = v.nombre
);


-- ============================================================
-- RESTAURANTES / ALIMENTACIÓN
-- ============================================================

INSERT INTO alimentacion
(
    restaurante,
    tipo_comida,
    tipo_servicio,
    incluye_bebidas,
    precio,
    id_proveedor
)
SELECT
    v.restaurante,
    v.tipo_comida,
    v.tipo_servicio,
    v.bebidas,
    v.precio,
    p.id_proveedor
FROM (
    VALUES

    ('Restaurante Caribe Plaza','Comida Caribeña','Desayuno',TRUE,35000,'Hotel Las Américas'),
    ('Sabor Cartagenero','Comida Típica','Almuerzo',TRUE,55000,'Hotel Las Américas'),
    ('Mar y Sol Cartagena','Mariscos','Cena',TRUE,70000,'Hotel Las Américas'),

    ('Sabor Paisa Medellín','Comida Paisa','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Paisa Gourmet','Comida Colombiana','Cena',TRUE,60000,'Hotel Las Américas'),
    ('Primavera Restaurante','Internacional','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Sabores de Guatapé','Comida Típica','Almuerzo',TRUE,40000,'Hotel Las Américas'),
    ('Lago Restaurante','Internacional','Cena',TRUE,55000,'Hotel Las Américas'),
    ('Piedra del Peñol Café','Comida Rápida','Refrigerio',TRUE,25000,'Hotel Las Américas'),

    ('Caribbean Taste San Andrés','Comida Caribeña','Almuerzo',TRUE,60000,'Hotel Las Américas'),
    ('Island Gourmet','Mariscos','Cena',TRUE,85000,'Hotel Las Américas'),
    ('Johnny Cay Restaurant','Comida Típica','Almuerzo',TRUE,50000,'Hotel Las Américas'),

    ('Tayrona Natural','Comida Caribeña','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Cabo San Juan Food','Comida Típica','Cena',TRUE,50000,'Hotel Las Américas'),
    ('Selva Restaurante','Comida Colombiana','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Cocora Gourmet','Comida Colombiana','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Salento Café','Cafetería','Refrigerio',TRUE,20000,'Hotel Las Américas'),
    ('Finca El Ocaso Restaurante','Comida Típica','Cena',TRUE,55000,'Hotel Las Américas'),

    ('Amazonas Sabores','Comida Amazónica','Almuerzo',TRUE,55000,'Hotel Las Américas'),
    ('Selva Gourmet','Comida Colombiana','Cena',TRUE,65000,'Hotel Las Américas'),
    ('Río Amazonas Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Tatacoa Restaurante','Comida Colombiana','Almuerzo',TRUE,40000,'Hotel Las Américas'),
    ('Desierto Gourmet','Comida Típica','Cena',TRUE,50000,'Hotel Las Américas'),
    ('Observatorio Café','Cafetería','Refrigerio',TRUE,25000,'Hotel Las Américas'),

    ('Caño Cristales Gourmet','Comida Colombiana','Almuerzo',TRUE,50000,'Hotel Las Américas'),
    ('Macarena Sabores','Comida Típica','Cena',TRUE,55000,'Hotel Las Américas'),
    ('Río Guayabero Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Eje Cafetero Gourmet','Comida Colombiana','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Café Armenia','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),
    ('Finca Cafetera Restaurante','Comida Típica','Cena',TRUE,55000,'Hotel Las Américas'),

    ('Pacífico Nuquí','Comida del Pacífico','Almuerzo',TRUE,60000,'Hotel Las Américas'),
    ('Nuquí Mariscos','Mariscos','Cena',TRUE,75000,'Hotel Las Américas'),
    ('Playa Olímpica Café','Comida Típica','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Barichara Sabores','Comida Santandereana','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Camino Real Restaurante','Comida Típica','Cena',TRUE,55000,'Hotel Las Américas'),
    ('Colonial Café','Cafetería','Desayuno',TRUE,28000,'Hotel Las Américas'),

    ('Las Lajas Restaurante','Comida Nariñense','Almuerzo',TRUE,40000,'Hotel Las Américas'),
    ('Sabores de Nariño','Comida Típica','Cena',TRUE,50000,'Hotel Las Américas'),
    ('Ipiales Café','Cafetería','Desayuno',TRUE,28000,'Hotel Las Américas'),

    ('Villa de Leyva Gourmet','Comida Colombiana','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Sabores Boyacenses','Comida Boyacense','Cena',TRUE,55000,'Hotel Las Américas'),
    ('Plaza Mayor Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Chicamocha Restaurante','Comida Santandereana','Almuerzo',TRUE,50000,'Hotel Las Américas'),
    ('Aventura Gourmet','Comida Colombiana','Cena',TRUE,60000,'Hotel Las Américas'),
    ('San Gil Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Mompox Sabores','Comida Caribeña','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Río Magdalena Restaurante','Comida Típica','Cena',TRUE,55000,'Hotel Las Américas'),
    ('Mompox Café Colonial','Cafetería','Desayuno',TRUE,28000,'Hotel Las Américas'),

    ('Sierra Nevada Restaurante','Comida Caribeña','Almuerzo',TRUE,50000,'Hotel Las Américas'),
    ('Sabores Ancestrales','Comida Típica','Cena',TRUE,60000,'Hotel Las Américas'),
    ('Sierra Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Tolú Caribe Restaurante','Comida Caribeña','Almuerzo',TRUE,45000,'Hotel Las Américas'),
    ('Coveñas Mariscos','Mariscos','Cena',TRUE,70000,'Hotel Las Américas'),
    ('Playa Tolú Café','Comida Típica','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Gorgona Natural','Comida del Pacífico','Almuerzo',TRUE,55000,'Hotel Las Américas'),
    ('Isla Gorgona Restaurante','Mariscos','Cena',TRUE,70000,'Hotel Las Américas'),
    ('Gorgona Café','Cafetería','Desayuno',TRUE,30000,'Hotel Las Américas'),

    ('Capurganá Caribe','Comida Caribeña','Almuerzo',TRUE,50000,'Hotel Las Américas'),
    ('Capurganá Mariscos','Mariscos','Cena',TRUE,70000,'Hotel Las Américas'),
    ('Playa La Caleta Café','Comida Típica','Desayuno',TRUE,30000,'Hotel Las Américas')

) AS v(
    restaurante,
    tipo_comida,
    tipo_servicio,
    bebidas,
    precio,
    proveedor
)
JOIN proveedor p
    ON p.nombre = v.proveedor
WHERE NOT EXISTS (
    SELECT 1
    FROM alimentacion a
    WHERE a.restaurante = v.restaurante
      AND a.tipo_comida = v.tipo_comida
);


-- ============================================================
-- TRANSPORTE
-- ============================================================

INSERT INTO transporte
(
    tipo,
    empresa,
    ruta,
    capacidad,
    hora_salida,
    hora_regreso,
    fecha_inicio,
    fecha_fin,
    id_proveedor
)
SELECT
    v.tipo,
    v.empresa,
    v.ruta,
    v.capacidad,
    v.salida::TIME,
    v.regreso::TIME,
    DATE '2026-01-01',
    DATE '2027-12-31',
    p.id_proveedor
FROM (
    VALUES

    ('Aéreo','Avianca','Bogotá → Cartagena',150,'08:00','18:00','Avianca'),
    ('Terrestre','CocoraTours','Cartagena → Barú → Cartagena',19,'08:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Medellín',150,'07:00','19:00','Avianca'),
    ('Terrestre','CocoraTours','Medellín → Guatapé → Medellín',19,'07:00','18:00','CocoraTours'),

    ('Terrestre','CocoraTours','Guatapé → Piedra del Peñol → Guatapé',19,'08:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → San Andrés',150,'06:30','17:30','Avianca'),
    ('Terrestre','CocoraTours','San Andrés → Playa de San Luis → San Andrés',19,'09:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Santa Marta',150,'07:30','18:30','Avianca'),
    ('Terrestre','CocoraTours','Santa Marta → Tayrona → Santa Marta',19,'06:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Armenia',150,'08:30','18:00','Avianca'),
    ('Terrestre','CocoraTours','Armenia → Salento → Armenia',19,'07:00','18:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Leticia',150,'09:00','17:00','Avianca'),
    ('Terrestre','CocoraTours','Leticia → Reserva Amazónica → Leticia',19,'07:00','17:00','CocoraTours'),

    ('Terrestre','CocoraTours','Neiva → Villavieja → Tatacoa',19,'06:00','18:00','CocoraTours'),
    ('Terrestre','CocoraTours','Villavieja → Observatorio → Villavieja',19,'18:00','23:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Villavicencio',150,'07:00','18:00','Avianca'),
    ('Terrestre','CocoraTours','La Macarena → Caño Cristales → La Macarena',19,'06:00','17:00','CocoraTours'),

    ('Terrestre','CocoraTours','Armenia → Finca Cafetera → Armenia',19,'07:00','18:00','CocoraTours'),

    ('Aéreo','Avianca','Medellín → Nuquí',100,'08:00','17:00','Avianca'),
    ('Terrestre','CocoraTours','Nuquí → Playa Olímpica → Nuquí',19,'08:00','17:00','CocoraTours'),

    ('Terrestre','CocoraTours','Bucaramanga → Barichara → Bucaramanga',19,'07:00','18:00','CocoraTours'),
    ('Terrestre','CocoraTours','Barichara → Camino Real → Barichara',19,'08:00','16:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Pasto',150,'07:30','18:00','Avianca'),
    ('Terrestre','CocoraTours','Pasto → Las Lajas → Pasto',19,'07:00','17:00','CocoraTours'),

    ('Terrestre','CocoraTours','Bogotá → Villa de Leyva → Bogotá',19,'06:00','19:00','CocoraTours'),
    ('Terrestre','CocoraTours','Villa de Leyva → Ráquira → Villa de Leyva',19,'08:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Bucaramanga',150,'07:00','18:00','Avianca'),
    ('Terrestre','CocoraTours','Bucaramanga → Chicamocha → Bucaramanga',19,'06:30','18:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Mompox',100,'08:00','17:00','Avianca'),
    ('Terrestre','CocoraTours','Mompox → Santa Cruz de Mompox → Mompox',19,'08:00','17:00','CocoraTours'),

    ('Terrestre','CocoraTours','Santa Marta → Sierra Nevada → Santa Marta',19,'05:30','18:00','CocoraTours'),

    ('Aéreo','Avianca','Bogotá → Sincelejo',150,'07:00','18:00','Avianca'),
    ('Terrestre','CocoraTours','Sincelejo → Tolú → Coveñas',19,'07:00','18:00','CocoraTours'),

    ('Aéreo','Avianca','Cali → Buenaventura',100,'08:00','17:00','Avianca'),
    ('Terrestre','CocoraTours','Buenaventura → Gorgona',19,'07:00','17:00','CocoraTours'),

    ('Aéreo','Avianca','Medellín → Apartadó',100,'07:00','17:00','Avianca'),
    ('Terrestre','CocoraTours','Necoclí → Capurganá',19,'08:00','17:00','CocoraTours')

) AS v(
    tipo,
    empresa,
    ruta,
    capacidad,
    salida,
    regreso,
    proveedor
)
JOIN proveedor p
    ON p.nombre = v.proveedor
WHERE NOT EXISTS (
    SELECT 1
    FROM transporte t
    WHERE t.empresa = v.empresa
      AND t.ruta = v.ruta
);

-- ============================================================

-- ============================================================

-- ============================================================

-- ============================================================

-- ============================================================
-- SIEMBRA DE SERVICIOS POR PAQUETE (demo del nuevo flujo)
-- Enlaza alojamientos, restaurantes, transportes y actividades
-- a cada paquete y crea los enlaces de seguro_servicio.
-- seguros: RC obligatorios + opcionales para todos los paquetes
-- ============================================================

BEGIN;

INSERT INTO actividad_turistica (nombre, tipo, duracion_horas, costo, id_destino)
SELECT a.nombre, a.tipo, a.duracion_horas::numeric, a.costo::numeric, d.id_destino
FROM (VALUES
    ('Tour Gastronómico Caribeño', 'Aventura', '3', '200000', 'Cartagena de Indias'),
    ('Islas del Rosario', 'Playa', '3', '120000', 'Cartagena de Indias'),
    ('City Tour Cartagena Histórica', 'Cultural', '3', '120000', 'Cartagena de Indias'),
    ('Tour Pueblito Paisa', 'Cultural', '3', '120000', 'Medellín'),
    ('Recorrido Comuna 13', 'Cultural', '3', '120000', 'Medellín'),
    ('City Tour Medellín', 'Cultural', '3', '120000', 'Medellín'),
    ('Pueblo de los Zócalos', 'Cultural', '3', '120000', 'Guatapé'),
    ('Tour Embalse de Guatapé', 'Naturaleza', '3', '120000', 'Guatapé'),
    ('Piedra del Peñol', 'Aventura', '3', '200000', 'Guatapé'),
    ('Tour Vuelta a la Isla', 'Naturaleza', '3', '120000', 'San Andrés'),
    ('Tour Johnny Cay', 'Playa', '3', '120000', 'San Andrés'),
    ('Snorkel Caribeño', 'Aventura', '3', '200000', 'San Andrés'),
    ('Senderismo Parque Tayrona', 'Naturaleza', '3', '120000', 'Parque Tayrona'),
    ('Avistamiento de Fauna', 'Naturaleza', '3', '120000', 'Parque Tayrona'),
    ('Playa Cabo San Juan', 'Playa', '3', '120000', 'Parque Tayrona'),
    ('Avistamiento de Aves', 'Naturaleza', '3', '120000', 'Valle del Cocora'),
    ('Tour Finca Cafetera', 'Cultural', '3', '120000', 'Valle del Cocora'),
    ('Caminata Valle del Cocora', 'Naturaleza', '3', '120000', 'Valle del Cocora'),
    ('Tour Arquitectura Colonial', 'Cultural', '3', '120000', 'Barichara'),
    ('Taller de Papel Artesanal', 'Cultural', '3', '120000', 'Barichara'),
    ('Camino Real de Barichara', 'Cultural', '3', '120000', 'Barichara'),
    ('Canotaje por el Río Amazonas', 'Aventura', '3', '200000', 'Leticia'),
    ('Senderismo Selva Amazónica', 'Naturaleza', '3', '120000', 'Leticia'),
    ('Avistamiento de Delfines Rosados', 'Naturaleza', '3', '120000', 'Leticia'),
    ('Visita a Caño Cristales', 'Naturaleza', '3', '120000', 'Caño Cristales'),
    ('Navegación Río Guayabero', 'Naturaleza', '3', '120000', 'Caño Cristales'),
    ('Senderismo Sierra de La Macarena', 'Aventura', '3', '200000', 'Caño Cristales'),
    ('Tour Finca Cafetera', 'Cultural', '3', '120000', 'Eje Cafetero'),
    ('Cata de Café Colombiano', 'Gastronomía', '3', '120000', 'Eje Cafetero'),
    ('Jardín Botánico y Mariposario', 'Naturaleza', '3', '120000', 'Eje Cafetero'),
    ('Avistamiento de Ballenas', 'Naturaleza', '3', '180000', 'Nuquí'),
    ('Playa y Snorkel Pacífico', 'Playa', '3', '120000', 'Nuquí'),
    ('Senderismo Selva Pacífica', 'Aventura', '3', '200000', 'Nuquí'),
    ('Tour Arquitectura Colonial', 'Cultural', '3', '120000', 'Barichara Colonial'),
    ('Taller de Papel Artesanal', 'Cultural', '3', '120000', 'Barichara Colonial'),
    ('Camino Real de Barichara', 'Cultural', '3', '120000', 'Barichara Colonial'),
    ('Tour Cultural de Ipiales', 'Cultural', '3', '120000', 'Las Lajas'),
    ('Santuario de Las Lajas', 'Cultural', '3', '120000', 'Las Lajas'),
    ('Miradores del Cañón', 'Naturaleza', '3', '120000', 'Las Lajas'),
    ('Plaza Mayor y Villa de Leyva', 'Cultural', '3', '120000', 'Villa de Leyva'),
    ('Museo Paleontológico del Desierto', 'Cultural', '3', '120000', 'Villa de Leyva'),
    ('Cerámica artesanal en Ráquira', 'Cultural', '3', '120000', 'Villa de Leyva'),
    ('Tour de San Gil', 'Aventura', '3', '200000', 'Cañón del Chicamocha'),
    ('Cañón del Chicamocha', 'Naturaleza', '3', '120000', 'Cañón del Chicamocha'),
    ('Parapente en Chicamocha', 'Aventura', '3', '200000', 'Cañón del Chicamocha'),
    ('Tour Colonial de Mompox', 'Cultural', '3', '120000', 'Mompox'),
    ('Taller de Filigrana', 'Cultural', '3', '120000', 'Mompox'),
    ('Navegación por el Río Magdalena', 'Naturaleza', '3', '120000', 'Mompox'),
    ('Experiencia Cultural Indígena', 'Cultural', '3', '120000', 'Sierra Nevada'),
    ('Caminata por Bosque Tropical', 'Naturaleza', '3', '120000', 'Sierra Nevada'),
    ('Senderismo Sierra Nevada', 'Naturaleza', '3', '120000', 'Sierra Nevada'),
    ('Tour Costero Tolú - Coveñas', 'Playa', '3', '120000', 'Tolú y Coveñas'),
    ('Snorkel Golfo de Morrosquillo', 'Aventura', '3', '200000', 'Tolú y Coveñas'),
    ('Tour Islas de San Bernardo', 'Playa', '3', '120000', 'Tolú y Coveñas'),
    ('Senderismo Parque Gorgona', 'Naturaleza', '3', '180000', 'Isla Gorgona'),
    ('Avistamiento de Fauna', 'Naturaleza', '3', '120000', 'Isla Gorgona'),
    ('Buceo y Vida Marina', 'Aventura', '3', '200000', 'Isla Gorgona'),
    ('Tour Bahía El Aguacate', 'Playa', '3', '120000', 'Capurganá'),
    ('Senderismo La Coquerita', 'Naturaleza', '3', '120000', 'Capurganá'),
    ('Snorkel Caribeño Capurganá', 'Aventura', '3', '200000', 'Capurganá')
) AS a(nombre, tipo, duracion_horas, costo, destino)
JOIN destino d ON d.nombre_destino = a.destino
WHERE NOT EXISTS (
    SELECT 1 FROM actividad_turistica at
    WHERE at.nombre = a.nombre AND at.id_destino = d.id_destino
);

-- alojamientos
CREATE TEMP TABLE paquete_alojamiento_l (slug TEXT, servicio TEXT) ON COMMIT DROP;
INSERT INTO paquete_alojamiento_l VALUES ('cartagena-magica', 'Hotel Caribe Plaza');
INSERT INTO paquete_alojamiento_l VALUES ('cartagena-magica', 'Hotel Colonial Cartagena');
INSERT INTO paquete_alojamiento_l VALUES ('medellin-innovadora', 'Hotel Poblado Central');
INSERT INTO paquete_alojamiento_l VALUES ('medellin-innovadora', 'Hotel Primavera Medellín');
INSERT INTO paquete_alojamiento_l VALUES ('guatape-extremo', 'Hotel Guatapé Lago');
INSERT INTO paquete_alojamiento_l VALUES ('guatape-extremo', 'Hostería Piedra del Peñol');
INSERT INTO paquete_alojamiento_l VALUES ('san-andres-todo-incluido', 'Decameron San Andrés');
INSERT INTO paquete_alojamiento_l VALUES ('san-andres-todo-incluido', 'Hotel Coral Caribe');
INSERT INTO paquete_alojamiento_l VALUES ('tayrona-salvaje', 'Ecohotel Tayrona');
INSERT INTO paquete_alojamiento_l VALUES ('tayrona-salvaje', 'Cabañas Cabo San Juan');
INSERT INTO paquete_alojamiento_l VALUES ('valle-del-cocora-mistico', 'Hotel Salento Real');
INSERT INTO paquete_alojamiento_l VALUES ('valle-del-cocora-mistico', 'Finca Cafetera Cocora');
INSERT INTO paquete_alojamiento_l VALUES ('amazonas-aventura', 'Hotel Amazonas');
INSERT INTO paquete_alojamiento_l VALUES ('amazonas-aventura', 'Eco Lodge Selva Amazónica');
INSERT INTO paquete_alojamiento_l VALUES ('desierto-de-la-tatacoa', 'Hotel Desierto Tatacoa');
INSERT INTO paquete_alojamiento_l VALUES ('desierto-de-la-tatacoa', 'Ecohostal La Tatacoa');
INSERT INTO paquete_alojamiento_l VALUES ('cano-cristales-premium', 'Hotel Caño Cristales');
INSERT INTO paquete_alojamiento_l VALUES ('cano-cristales-premium', 'Ecohotel Río Guayabero');
INSERT INTO paquete_alojamiento_l VALUES ('eje-cafetero-tradicional', 'Hotel Eje Cafetero');
INSERT INTO paquete_alojamiento_l VALUES ('eje-cafetero-tradicional', 'Finca Cafetera Armenia');
INSERT INTO paquete_alojamiento_l VALUES ('nuqui-ecoturismo', 'Hotel Nuquí Pacífico');
INSERT INTO paquete_alojamiento_l VALUES ('nuqui-ecoturismo', 'Eco Lodge Nuquí');
INSERT INTO paquete_alojamiento_l VALUES ('barichara-colonial', 'Hotel Barichara Colonial');
INSERT INTO paquete_alojamiento_l VALUES ('barichara-colonial', 'Casa Colonial Barichara');
INSERT INTO paquete_alojamiento_l VALUES ('santuario-las-lajas', 'Hotel Las Lajas');
INSERT INTO paquete_alojamiento_l VALUES ('santuario-las-lajas', 'Hotel Santuario Nariño');
INSERT INTO paquete_alojamiento_l VALUES ('boyaca-historica', 'Hotel Villa de Leyva');
INSERT INTO paquete_alojamiento_l VALUES ('boyaca-historica', 'Posada Colonial Boyacá');
INSERT INTO paquete_alojamiento_l VALUES ('canon-del-chicamocha', 'Hotel Chicamocha');
INSERT INTO paquete_alojamiento_l VALUES ('canon-del-chicamocha', 'Hotel Aventura Santander');
INSERT INTO paquete_alojamiento_l VALUES ('mompox-patrimonial', 'Hotel Mompox Real');
INSERT INTO paquete_alojamiento_l VALUES ('mompox-patrimonial', 'Casa Colonial Mompox');
INSERT INTO paquete_alojamiento_l VALUES ('sierra-nevada-ancestral', 'Hotel Sierra Nevada');
INSERT INTO paquete_alojamiento_l VALUES ('sierra-nevada-ancestral', 'Eco Lodge Sierra Nevada');
INSERT INTO paquete_alojamiento_l VALUES ('tolu-y-covenas-relax', 'Hotel Tolú Caribe');
INSERT INTO paquete_alojamiento_l VALUES ('tolu-y-covenas-relax', 'Hotel Coveñas Beach');
INSERT INTO paquete_alojamiento_l VALUES ('isla-gorgona-explorer', 'Ecohotel Gorgona');
INSERT INTO paquete_alojamiento_l VALUES ('isla-gorgona-explorer', 'Cabañas Isla Gorgona');
INSERT INTO paquete_alojamiento_l VALUES ('capurgana-paraiso', 'Hotel Capurganá Caribe');
INSERT INTO paquete_alojamiento_l VALUES ('capurgana-paraiso', 'Eco Lodge Capurganá');
INSERT INTO paquete_alojamiento (id_paquete, id_alojamiento)
SELECT p.id_paquete, s.id_alojamiento
FROM (paquete_alojamiento_l l JOIN paquete_turistico p ON p.slug = l.slug)
JOIN alojamiento s ON l.servicio = s.nombre
WHERE NOT EXISTS (
    SELECT 1 FROM paquete_alojamiento x
    WHERE x.id_paquete = p.id_paquete AND x.id_alojamiento = s.id_alojamiento
);

-- alimentación
CREATE TEMP TABLE paquete_alimentacion_l (slug TEXT, servicio TEXT) ON COMMIT DROP;
INSERT INTO paquete_alimentacion_l VALUES ('cartagena-magica', 'Restaurante Caribe Plaza');
INSERT INTO paquete_alimentacion_l VALUES ('cartagena-magica', 'Sabor Cartagenero');
INSERT INTO paquete_alimentacion_l VALUES ('cartagena-magica', 'Mar y Sol Cartagena');
INSERT INTO paquete_alimentacion_l VALUES ('medellin-innovadora', 'Sabor Paisa Medellín');
INSERT INTO paquete_alimentacion_l VALUES ('medellin-innovadora', 'Paisa Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('medellin-innovadora', 'Primavera Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('guatape-extremo', 'Sabores de Guatapé');
INSERT INTO paquete_alimentacion_l VALUES ('guatape-extremo', 'Lago Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('guatape-extremo', 'Piedra del Peñol Café');
INSERT INTO paquete_alimentacion_l VALUES ('san-andres-todo-incluido', 'Caribbean Taste San Andrés');
INSERT INTO paquete_alimentacion_l VALUES ('san-andres-todo-incluido', 'Island Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('san-andres-todo-incluido', 'Johnny Cay Restaurant');
INSERT INTO paquete_alimentacion_l VALUES ('tayrona-salvaje', 'Tayrona Natural');
INSERT INTO paquete_alimentacion_l VALUES ('tayrona-salvaje', 'Cabo San Juan Food');
INSERT INTO paquete_alimentacion_l VALUES ('tayrona-salvaje', 'Selva Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('valle-del-cocora-mistico', 'Cocora Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('valle-del-cocora-mistico', 'Salento Café');
INSERT INTO paquete_alimentacion_l VALUES ('valle-del-cocora-mistico', 'Finca El Ocaso Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('amazonas-aventura', 'Amazonas Sabores');
INSERT INTO paquete_alimentacion_l VALUES ('amazonas-aventura', 'Selva Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('amazonas-aventura', 'Río Amazonas Café');
INSERT INTO paquete_alimentacion_l VALUES ('desierto-de-la-tatacoa', 'Tatacoa Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('desierto-de-la-tatacoa', 'Desierto Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('desierto-de-la-tatacoa', 'Observatorio Café');
INSERT INTO paquete_alimentacion_l VALUES ('cano-cristales-premium', 'Caño Cristales Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('cano-cristales-premium', 'Macarena Sabores');
INSERT INTO paquete_alimentacion_l VALUES ('cano-cristales-premium', 'Río Guayabero Café');
INSERT INTO paquete_alimentacion_l VALUES ('eje-cafetero-tradicional', 'Eje Cafetero Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('eje-cafetero-tradicional', 'Café Armenia');
INSERT INTO paquete_alimentacion_l VALUES ('eje-cafetero-tradicional', 'Finca Cafetera Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('nuqui-ecoturismo', 'Pacífico Nuquí');
INSERT INTO paquete_alimentacion_l VALUES ('nuqui-ecoturismo', 'Nuquí Mariscos');
INSERT INTO paquete_alimentacion_l VALUES ('nuqui-ecoturismo', 'Playa Olímpica Café');
INSERT INTO paquete_alimentacion_l VALUES ('barichara-colonial', 'Barichara Sabores');
INSERT INTO paquete_alimentacion_l VALUES ('barichara-colonial', 'Camino Real Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('barichara-colonial', 'Colonial Café');
INSERT INTO paquete_alimentacion_l VALUES ('santuario-las-lajas', 'Las Lajas Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('santuario-las-lajas', 'Sabores de Nariño');
INSERT INTO paquete_alimentacion_l VALUES ('santuario-las-lajas', 'Ipiales Café');
INSERT INTO paquete_alimentacion_l VALUES ('boyaca-historica', 'Villa de Leyva Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('boyaca-historica', 'Sabores Boyacenses');
INSERT INTO paquete_alimentacion_l VALUES ('boyaca-historica', 'Plaza Mayor Café');
INSERT INTO paquete_alimentacion_l VALUES ('canon-del-chicamocha', 'Chicamocha Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('canon-del-chicamocha', 'Aventura Gourmet');
INSERT INTO paquete_alimentacion_l VALUES ('canon-del-chicamocha', 'San Gil Café');
INSERT INTO paquete_alimentacion_l VALUES ('mompox-patrimonial', 'Mompox Sabores');
INSERT INTO paquete_alimentacion_l VALUES ('mompox-patrimonial', 'Río Magdalena Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('mompox-patrimonial', 'Mompox Café Colonial');
INSERT INTO paquete_alimentacion_l VALUES ('sierra-nevada-ancestral', 'Sierra Nevada Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('sierra-nevada-ancestral', 'Sabores Ancestrales');
INSERT INTO paquete_alimentacion_l VALUES ('sierra-nevada-ancestral', 'Sierra Café');
INSERT INTO paquete_alimentacion_l VALUES ('tolu-y-covenas-relax', 'Tolú Caribe Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('tolu-y-covenas-relax', 'Coveñas Mariscos');
INSERT INTO paquete_alimentacion_l VALUES ('tolu-y-covenas-relax', 'Playa Tolú Café');
INSERT INTO paquete_alimentacion_l VALUES ('isla-gorgona-explorer', 'Gorgona Natural');
INSERT INTO paquete_alimentacion_l VALUES ('isla-gorgona-explorer', 'Isla Gorgona Restaurante');
INSERT INTO paquete_alimentacion_l VALUES ('isla-gorgona-explorer', 'Gorgona Café');
INSERT INTO paquete_alimentacion_l VALUES ('capurgana-paraiso', 'Capurganá Caribe');
INSERT INTO paquete_alimentacion_l VALUES ('capurgana-paraiso', 'Capurganá Mariscos');
INSERT INTO paquete_alimentacion_l VALUES ('capurgana-paraiso', 'Playa La Caleta Café');
INSERT INTO paquete_alimentacion (id_paquete, id_alimentacion)
SELECT p.id_paquete, s.id_alimentacion
FROM (paquete_alimentacion_l l JOIN paquete_turistico p ON p.slug = l.slug)
JOIN alimentacion s ON l.servicio = s.restaurante
WHERE NOT EXISTS (
    SELECT 1 FROM paquete_alimentacion x
    WHERE x.id_paquete = p.id_paquete AND x.id_alimentacion = s.id_alimentacion
);

-- transporte
CREATE TEMP TABLE paquete_transporte_l (slug TEXT, servicio TEXT) ON COMMIT DROP;
INSERT INTO paquete_transporte_l VALUES ('cartagena-magica', 'Bogotá → Cartagena');
INSERT INTO paquete_transporte_l VALUES ('cartagena-magica', 'Cartagena → Barú → Cartagena');
INSERT INTO paquete_transporte_l VALUES ('medellin-innovadora', 'Bogotá → Medellín');
INSERT INTO paquete_transporte_l VALUES ('medellin-innovadora', 'Medellín → Guatapé → Medellín');
INSERT INTO paquete_transporte_l VALUES ('guatape-extremo', 'Guatapé → Piedra del Peñol → Guatapé');
INSERT INTO paquete_transporte_l VALUES ('guatape-extremo', 'Medellín → Guatapé → Medellín');
INSERT INTO paquete_transporte_l VALUES ('san-andres-todo-incluido', 'Bogotá → San Andrés');
INSERT INTO paquete_transporte_l VALUES ('san-andres-todo-incluido', 'San Andrés → Playa de San Luis → San Andrés');
INSERT INTO paquete_transporte_l VALUES ('tayrona-salvaje', 'Bogotá → Santa Marta');
INSERT INTO paquete_transporte_l VALUES ('tayrona-salvaje', 'Santa Marta → Tayrona → Santa Marta');
INSERT INTO paquete_transporte_l VALUES ('valle-del-cocora-mistico', 'Bogotá → Armenia');
INSERT INTO paquete_transporte_l VALUES ('valle-del-cocora-mistico', 'Armenia → Salento → Armenia');
INSERT INTO paquete_transporte_l VALUES ('amazonas-aventura', 'Bogotá → Leticia');
INSERT INTO paquete_transporte_l VALUES ('amazonas-aventura', 'Leticia → Reserva Amazónica → Leticia');
INSERT INTO paquete_transporte_l VALUES ('desierto-de-la-tatacoa', 'Neiva → Villavieja → Tatacoa');
INSERT INTO paquete_transporte_l VALUES ('desierto-de-la-tatacoa', 'Villavieja → Observatorio → Villavieja');
INSERT INTO paquete_transporte_l VALUES ('cano-cristales-premium', 'Bogotá → Villavicencio');
INSERT INTO paquete_transporte_l VALUES ('cano-cristales-premium', 'La Macarena → Caño Cristales → La Macarena');
INSERT INTO paquete_transporte_l VALUES ('eje-cafetero-tradicional', 'Bogotá → Armenia');
INSERT INTO paquete_transporte_l VALUES ('eje-cafetero-tradicional', 'Armenia → Finca Cafetera → Armenia');
INSERT INTO paquete_transporte_l VALUES ('nuqui-ecoturismo', 'Medellín → Nuquí');
INSERT INTO paquete_transporte_l VALUES ('nuqui-ecoturismo', 'Nuquí → Playa Olímpica → Nuquí');
INSERT INTO paquete_transporte_l VALUES ('barichara-colonial', 'Bucaramanga → Barichara → Bucaramanga');
INSERT INTO paquete_transporte_l VALUES ('barichara-colonial', 'Barichara → Camino Real → Barichara');
INSERT INTO paquete_transporte_l VALUES ('santuario-las-lajas', 'Bogotá → Pasto');
INSERT INTO paquete_transporte_l VALUES ('santuario-las-lajas', 'Pasto → Las Lajas → Pasto');
INSERT INTO paquete_transporte_l VALUES ('boyaca-historica', 'Bogotá → Villa de Leyva → Bogotá');
INSERT INTO paquete_transporte_l VALUES ('boyaca-historica', 'Villa de Leyva → Ráquira → Villa de Leyva');
INSERT INTO paquete_transporte_l VALUES ('canon-del-chicamocha', 'Bogotá → Bucaramanga');
INSERT INTO paquete_transporte_l VALUES ('canon-del-chicamocha', 'Bucaramanga → Chicamocha → Bucaramanga');
INSERT INTO paquete_transporte_l VALUES ('mompox-patrimonial', 'Bogotá → Mompox');
INSERT INTO paquete_transporte_l VALUES ('mompox-patrimonial', 'Mompox → Santa Cruz de Mompox → Mompox');
INSERT INTO paquete_transporte_l VALUES ('sierra-nevada-ancestral', 'Bogotá → Santa Marta');
INSERT INTO paquete_transporte_l VALUES ('sierra-nevada-ancestral', 'Santa Marta → Sierra Nevada → Santa Marta');
INSERT INTO paquete_transporte_l VALUES ('tolu-y-covenas-relax', 'Bogotá → Sincelejo');
INSERT INTO paquete_transporte_l VALUES ('tolu-y-covenas-relax', 'Sincelejo → Tolú → Coveñas');
INSERT INTO paquete_transporte_l VALUES ('isla-gorgona-explorer', 'Cali → Buenaventura');
INSERT INTO paquete_transporte_l VALUES ('isla-gorgona-explorer', 'Buenaventura → Gorgona');
INSERT INTO paquete_transporte_l VALUES ('capurgana-paraiso', 'Medellín → Apartadó');
INSERT INTO paquete_transporte_l VALUES ('capurgana-paraiso', 'Necoclí → Capurganá');
INSERT INTO paquete_transporte (id_paquete, id_transporte)
SELECT p.id_paquete, s.id_transporte
FROM (paquete_transporte_l l JOIN paquete_turistico p ON p.slug = l.slug)
JOIN transporte s ON l.servicio = s.ruta
WHERE NOT EXISTS (
    SELECT 1 FROM paquete_transporte x
    WHERE x.id_paquete = p.id_paquete AND x.id_transporte = s.id_transporte
);

-- actividades
CREATE TEMP TABLE paquete_actividad_l (slug TEXT, servicio TEXT) ON COMMIT DROP;
INSERT INTO paquete_actividad_l VALUES ('cartagena-magica', 'Tour Gastronómico Caribeño');
INSERT INTO paquete_actividad_l VALUES ('cartagena-magica', 'Islas del Rosario');
INSERT INTO paquete_actividad_l VALUES ('cartagena-magica', 'City Tour Cartagena Histórica');
INSERT INTO paquete_actividad_l VALUES ('medellin-innovadora', 'Tour Pueblito Paisa');
INSERT INTO paquete_actividad_l VALUES ('medellin-innovadora', 'Recorrido Comuna 13');
INSERT INTO paquete_actividad_l VALUES ('medellin-innovadora', 'City Tour Medellín');
INSERT INTO paquete_actividad_l VALUES ('guatape-extremo', 'Pueblo de los Zócalos');
INSERT INTO paquete_actividad_l VALUES ('guatape-extremo', 'Tour Embalse de Guatapé');
INSERT INTO paquete_actividad_l VALUES ('guatape-extremo', 'Piedra del Peñol');
INSERT INTO paquete_actividad_l VALUES ('san-andres-todo-incluido', 'Tour Vuelta a la Isla');
INSERT INTO paquete_actividad_l VALUES ('san-andres-todo-incluido', 'Tour Johnny Cay');
INSERT INTO paquete_actividad_l VALUES ('san-andres-todo-incluido', 'Snorkel Caribeño');
INSERT INTO paquete_actividad_l VALUES ('tayrona-salvaje', 'Senderismo Parque Tayrona');
INSERT INTO paquete_actividad_l VALUES ('tayrona-salvaje', 'Avistamiento de Fauna');
INSERT INTO paquete_actividad_l VALUES ('tayrona-salvaje', 'Playa Cabo San Juan');
INSERT INTO paquete_actividad_l VALUES ('valle-del-cocora-mistico', 'Avistamiento de Aves');
INSERT INTO paquete_actividad_l VALUES ('valle-del-cocora-mistico', 'Tour Finca Cafetera');
INSERT INTO paquete_actividad_l VALUES ('valle-del-cocora-mistico', 'Caminata Valle del Cocora');
INSERT INTO paquete_actividad_l VALUES ('amazonas-aventura', 'Canotaje por el Río Amazonas');
INSERT INTO paquete_actividad_l VALUES ('amazonas-aventura', 'Senderismo Selva Amazónica');
INSERT INTO paquete_actividad_l VALUES ('amazonas-aventura', 'Avistamiento de Delfines Rosados');
INSERT INTO paquete_actividad_l VALUES ('cano-cristales-premium', 'Visita a Caño Cristales');
INSERT INTO paquete_actividad_l VALUES ('cano-cristales-premium', 'Navegación Río Guayabero');
INSERT INTO paquete_actividad_l VALUES ('cano-cristales-premium', 'Senderismo Sierra de La Macarena');
INSERT INTO paquete_actividad_l VALUES ('eje-cafetero-tradicional', 'Tour Finca Cafetera');
INSERT INTO paquete_actividad_l VALUES ('eje-cafetero-tradicional', 'Cata de Café Colombiano');
INSERT INTO paquete_actividad_l VALUES ('eje-cafetero-tradicional', 'Jardín Botánico y Mariposario');
INSERT INTO paquete_actividad_l VALUES ('nuqui-ecoturismo', 'Avistamiento de Ballenas');
INSERT INTO paquete_actividad_l VALUES ('nuqui-ecoturismo', 'Playa y Snorkel Pacífico');
INSERT INTO paquete_actividad_l VALUES ('nuqui-ecoturismo', 'Senderismo Selva Pacífica');
INSERT INTO paquete_actividad_l VALUES ('barichara-colonial', 'Tour Arquitectura Colonial');
INSERT INTO paquete_actividad_l VALUES ('barichara-colonial', 'Taller de Papel Artesanal');
INSERT INTO paquete_actividad_l VALUES ('barichara-colonial', 'Camino Real de Barichara');
INSERT INTO paquete_actividad_l VALUES ('santuario-las-lajas', 'Tour Cultural de Ipiales');
INSERT INTO paquete_actividad_l VALUES ('santuario-las-lajas', 'Santuario de Las Lajas');
INSERT INTO paquete_actividad_l VALUES ('santuario-las-lajas', 'Miradores del Cañón');
INSERT INTO paquete_actividad_l VALUES ('boyaca-historica', 'Plaza Mayor y Villa de Leyva');
INSERT INTO paquete_actividad_l VALUES ('boyaca-historica', 'Museo Paleontológico del Desierto');
INSERT INTO paquete_actividad_l VALUES ('boyaca-historica', 'Cerámica artesanal en Ráquira');
INSERT INTO paquete_actividad_l VALUES ('canon-del-chicamocha', 'Tour de San Gil');
INSERT INTO paquete_actividad_l VALUES ('canon-del-chicamocha', 'Cañón del Chicamocha');
INSERT INTO paquete_actividad_l VALUES ('canon-del-chicamocha', 'Parapente en Chicamocha');
INSERT INTO paquete_actividad_l VALUES ('mompox-patrimonial', 'Tour Colonial de Mompox');
INSERT INTO paquete_actividad_l VALUES ('mompox-patrimonial', 'Taller de Filigrana');
INSERT INTO paquete_actividad_l VALUES ('mompox-patrimonial', 'Navegación por el Río Magdalena');
INSERT INTO paquete_actividad_l VALUES ('sierra-nevada-ancestral', 'Experiencia Cultural Indígena');
INSERT INTO paquete_actividad_l VALUES ('sierra-nevada-ancestral', 'Caminata por Bosque Tropical');
INSERT INTO paquete_actividad_l VALUES ('sierra-nevada-ancestral', 'Senderismo Sierra Nevada');
INSERT INTO paquete_actividad_l VALUES ('tolu-y-covenas-relax', 'Tour Costero Tolú - Coveñas');
INSERT INTO paquete_actividad_l VALUES ('tolu-y-covenas-relax', 'Snorkel Golfo de Morrosquillo');
INSERT INTO paquete_actividad_l VALUES ('tolu-y-covenas-relax', 'Tour Islas de San Bernardo');
INSERT INTO paquete_actividad_l VALUES ('isla-gorgona-explorer', 'Senderismo Parque Gorgona');
INSERT INTO paquete_actividad_l VALUES ('isla-gorgona-explorer', 'Avistamiento de Fauna');
INSERT INTO paquete_actividad_l VALUES ('isla-gorgona-explorer', 'Buceo y Vida Marina');
INSERT INTO paquete_actividad_l VALUES ('capurgana-paraiso', 'Tour Bahía El Aguacate');
INSERT INTO paquete_actividad_l VALUES ('capurgana-paraiso', 'Senderismo La Coquerita');
INSERT INTO paquete_actividad_l VALUES ('capurgana-paraiso', 'Snorkel Caribeño Capurganá');
INSERT INTO paquete_actividad (id_paquete, id_actividad)
SELECT p.id_paquete, a.id_actividad
FROM paquete_actividad_l l JOIN paquete_turistico p ON p.slug = l.slug
JOIN actividad_turistica a ON a.nombre = l.servicio AND a.id_destino = p.id_destino
WHERE NOT EXISTS (
    SELECT 1 FROM paquete_actividad x
    WHERE x.id_paquete = p.id_paquete AND x.id_actividad = a.id_actividad
);

-- seguros obligatorios ligados a sus servicios
INSERT INTO seguro_servicio (id_seguro, id_alojamiento)
SELECT s.id_seguro, a.id_alojamiento FROM seguro s CROSS JOIN alojamiento a
WHERE s.nombre = 'RC Alojamiento'
  AND NOT EXISTS (SELECT 1 FROM seguro_servicio ss WHERE ss.id_seguro = s.id_seguro AND ss.id_alojamiento = a.id_alojamiento);
INSERT INTO seguro_servicio (id_seguro, id_transporte)
SELECT s.id_seguro, t.id_transporte FROM seguro s CROSS JOIN transporte t
WHERE s.nombre = 'RC Transporte'
  AND NOT EXISTS (SELECT 1 FROM seguro_servicio ss WHERE ss.id_seguro = s.id_seguro AND ss.id_transporte = t.id_transporte);
INSERT INTO seguro_servicio (id_seguro, id_actividad)
SELECT s.id_seguro, a.id_actividad FROM seguro s CROSS JOIN actividad_turistica a
WHERE s.nombre = 'RC Actividad'
  AND NOT EXISTS (SELECT 1 FROM seguro_servicio ss WHERE ss.id_seguro = s.id_seguro AND ss.id_actividad = a.id_actividad);

-- seguros opcionales ofrecidos en todos los paquetes
INSERT INTO seguro_servicio (id_seguro, id_actividad)
SELECT s.id_seguro, pa.id_actividad
FROM seguro s
CROSS JOIN (SELECT id_paquete, MIN(id_actividad) AS id_actividad FROM paquete_actividad GROUP BY id_paquete) pa
WHERE s.nombre IN ('Seguro Médico Básico', 'Seguro Médico Completo', 'Seguro Premium')
  AND NOT EXISTS (
    SELECT 1 FROM seguro_servicio ss
    WHERE ss.id_seguro = s.id_seguro AND ss.id_actividad = pa.id_actividad
  );


COMMIT;
