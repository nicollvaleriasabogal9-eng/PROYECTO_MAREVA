BEGIN;

CREATE TABLE IF NOT EXISTS nivel (
    id_nivel SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    min_monto NUMERIC(12,2) NOT NULL DEFAULT 0,
    min_reservas INT NOT NULL DEFAULT 0,
    descripcion TEXT,
    porcentaje_descuento NUMERIC(5,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS insignia (
    id_insignia SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    criterio TEXT,
    imagen_url VARCHAR(255),
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    tipo_documento VARCHAR(30) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'cliente',
    codigo_referido VARCHAR(20) UNIQUE,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta TIMESTAMP,
    id_nivel INT REFERENCES nivel(id_nivel),
    acepta_politica_no_reembolso BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_aceptacion_politica TIMESTAMP,
    version_politica VARCHAR(20) NOT NULL DEFAULT '1.0',
    CONSTRAINT chk_cliente_rol CHECK (rol IN ('admin','cliente'))
);

CREATE TABLE IF NOT EXISTS cliente_insignia (
    id_cliente_insignia SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_insignia INT NOT NULL REFERENCES insignia(id_insignia),
    fecha_obtenida DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (id_cliente, id_insignia)
);

CREATE TABLE IF NOT EXISTS referido (
    id_referido SERIAL PRIMARY KEY,
    fecha_referido DATE NOT NULL DEFAULT CURRENT_DATE,
    puntos_ganados INT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    id_referidor INT NOT NULL REFERENCES cliente(id_cliente),
    id_referido_cliente INT NOT NULL REFERENCES cliente(id_cliente),
    UNIQUE (id_referidor, id_referido_cliente),
    CONSTRAINT chk_referido_estado CHECK (estado IN ('pendiente','completado','cancelado')),
    CONSTRAINT chk_no_autoreferido CHECK (id_referidor <> id_referido_cliente)
);

CREATE TABLE IF NOT EXISTS destino (
    id_destino SERIAL PRIMARY KEY,
    nombre_destino VARCHAR(100) NOT NULL,
    departamento VARCHAR(100),
    ciudad VARCHAR(100),
    categoria VARCHAR(50),
    descripcion TEXT,
    atracciones TEXT,
    docs_requeridos TEXT,
    imagen_principal VARCHAR(255),
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    video_url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nit VARCHAR(30),
    tipo_empresa VARCHAR(50),
    descripcion TEXT,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    nombre_contacto VARCHAR(100),
    telefono_contacto VARCHAR(20),
    correo_contacto VARCHAR(100),
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    contrasena VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS metodo_pago_proveedor (
    id_metodo_proveedor SERIAL PRIMARY KEY,
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor) ON DELETE CASCADE,
    tipo_metodo VARCHAR(50) NOT NULL,
    entidad VARCHAR(100),
    titular VARCHAR(150),
    numero_referencia VARCHAR(100),
    instrucciones TEXT,
    CONSTRAINT chk_tipo_metodo CHECK (tipo_metodo IN ('cuenta_bancaria','nequi','daviplata','efectivo','tarjeta','otro'))
);

CREATE TABLE IF NOT EXISTS guia_turistico (
    id_guia SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    idiomas VARCHAR(200),
    especialidad VARCHAR(200),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    contrasena VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tipo_seguro (
    id_tipo_seguro SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    cobertura_general TEXT
);

CREATE TABLE IF NOT EXISTS seguro (
    id_seguro SERIAL PRIMARY KEY,
    id_tipo_seguro INT NOT NULL REFERENCES tipo_seguro(id_tipo_seguro),
    nombre VARCHAR(100) NOT NULL,
    cobertura TEXT NOT NULL,
    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
    es_obligatorio BOOLEAN NOT NULL DEFAULT FALSE,
    descripcion TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS alojamiento (
    id_alojamiento SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo_alojamiento VARCHAR(50),
    ciudad VARCHAR(100),
    direccion VARCHAR(200),
    servicios TEXT,
    id_proveedor INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE IF NOT EXISTS alimentacion (
    id_alimentacion SERIAL PRIMARY KEY,
    restaurante VARCHAR(100),
    tipo_comida VARCHAR(100),
    tipo_servicio VARCHAR(50),
    incluye_bebidas BOOLEAN NOT NULL DEFAULT FALSE,
    precio NUMERIC(10,2),
    id_proveedor INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE IF NOT EXISTS transporte (
    id_transporte SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    empresa VARCHAR(100),
    ruta VARCHAR(200),
    capacidad INT,
    hora_salida TIME,
    hora_regreso TIME,
    fecha_inicio DATE,
    fecha_fin DATE,
    id_proveedor INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE IF NOT EXISTS actividad_turistica (
    id_actividad SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(100),
    duracion_horas NUMERIC(4,1),
    costo NUMERIC(10,2),
    id_destino INT REFERENCES destino(id_destino),
    id_guia INT REFERENCES guia_turistico(id_guia),
    id_proveedor INT REFERENCES proveedor(id_proveedor)
);

CREATE TABLE IF NOT EXISTS seguro_servicio (
    id_seguro_servicio SERIAL PRIMARY KEY,
    id_seguro INT NOT NULL REFERENCES seguro(id_seguro) ON DELETE CASCADE,
    id_alojamiento INT REFERENCES alojamiento(id_alojamiento) ON DELETE CASCADE,
    id_alimentacion INT REFERENCES alimentacion(id_alimentacion) ON DELETE CASCADE,
    id_transporte INT REFERENCES transporte(id_transporte) ON DELETE CASCADE,
    id_actividad INT REFERENCES actividad_turistica(id_actividad) ON DELETE CASCADE,
    CONSTRAINT chk_solo_un_servicio CHECK (
        (id_alojamiento IS NOT NULL)::INT +
        (id_alimentacion IS NOT NULL)::INT +
        (id_transporte IS NOT NULL)::INT +
        (id_actividad IS NOT NULL)::INT = 1
    ),
    UNIQUE (id_seguro, id_alojamiento),
    UNIQUE (id_seguro, id_alimentacion),
    UNIQUE (id_seguro, id_transporte),
    UNIQUE (id_seguro, id_actividad)
);

CREATE TABLE IF NOT EXISTS paquete_turistico (
    id_paquete SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    imagen_url VARCHAR(255),
    descripcion TEXT,
    precio NUMERIC(10,2) NOT NULL,
    duracion_dias INT,
    duracion_noches INT,
    cupos_totales INT NOT NULL DEFAULT 0,
    cupos_disponibles INT NOT NULL DEFAULT 0,
    fecha_inicio DATE,
    fecha_fin DATE,
    imagen_principal VARCHAR(255),
    personalizable BOOLEAN NOT NULL DEFAULT FALSE,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    id_destino INT REFERENCES destino(id_destino),
    id_guia INT REFERENCES guia_turistico(id_guia),
    emoji VARCHAR(10) DEFAULT '🧳',
    video_url VARCHAR(255),
    CONSTRAINT chk_paquete_estado CHECK (estado IN ('activo','suspendido')),
    CONSTRAINT chk_cupos CHECK (cupos_disponibles <= cupos_totales)
);

CREATE TABLE IF NOT EXISTS paquete_transporte (
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_transporte INT NOT NULL REFERENCES transporte(id_transporte),
    PRIMARY KEY (id_paquete, id_transporte)
);

CREATE TABLE IF NOT EXISTS paquete_alojamiento (
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_alojamiento INT NOT NULL REFERENCES alojamiento(id_alojamiento),
    PRIMARY KEY (id_paquete, id_alojamiento)
);

CREATE TABLE IF NOT EXISTS paquete_alimentacion (
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_alimentacion INT NOT NULL REFERENCES alimentacion(id_alimentacion),
    PRIMARY KEY (id_paquete, id_alimentacion)
);

CREATE TABLE IF NOT EXISTS paquete_actividad (
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_actividad INT NOT NULL REFERENCES actividad_turistica(id_actividad),
    PRIMARY KEY (id_paquete, id_actividad)
);

CREATE TABLE IF NOT EXISTS servicio_extra (
    id_servicio_extra SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    descripcion TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS promocion (
    id_promocion SERIAL PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    descuento NUMERIC(5,2) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    tipo_promocion VARCHAR(30),
    id_paquete INT REFERENCES paquete_turistico(id_paquete),
    CONSTRAINT chk_descuento CHECK (descuento > 0 AND descuento <= 100)
);

CREATE TABLE IF NOT EXISTS promocion_insignia (
    id_promocion INT NOT NULL REFERENCES promocion(id_promocion) ON DELETE CASCADE,
    id_insignia INT NOT NULL REFERENCES insignia(id_insignia) ON DELETE CASCADE,
    PRIMARY KEY (id_promocion, id_insignia)
);

CREATE TABLE IF NOT EXISTS promocion_nivel (
    id_promocion INT NOT NULL REFERENCES promocion(id_promocion) ON DELETE CASCADE,
    id_nivel INT NOT NULL REFERENCES nivel(id_nivel) ON DELETE CASCADE,
    PRIMARY KEY (id_promocion, id_nivel)
);

CREATE TABLE IF NOT EXISTS contrato (
    id_contrato SERIAL PRIMARY KEY,
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor) ON DELETE CASCADE,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    descripcion_terminos TEXT NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    condiciones_comerciales TEXT,
    estado_contrato VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    respuesta_proveedor VARCHAR(20),
    fecha_respuesta TIMESTAMP,
    firma_proveedor BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_firma TIMESTAMP,
    metodo_firma VARCHAR(50),
    CONSTRAINT contrato_check CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT contrato_estado_contrato_check CHECK (estado_contrato IN ('pendiente','aceptado','rechazado','vigente','vencido')),
    CONSTRAINT contrato_respuesta_proveedor_check CHECK (respuesta_proveedor IS NULL OR respuesta_proveedor IN ('aceptado','rechazado'))
);

CREATE TABLE IF NOT EXISTS documento (
    id_documento SERIAL PRIMARY KEY,
    id_contrato INT REFERENCES contrato(id_contrato) ON DELETE CASCADE,
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor) ON DELETE CASCADE,
    nombre_documento VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    url_documento VARCHAR(500) NOT NULL,
    estado_documento VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT documento_estado_documento_check CHECK (estado_documento IN ('pendiente','aprobado','rechazado'))
);

CREATE TABLE IF NOT EXISTS salida_paquete (
    id_salida SERIAL PRIMARY KEY,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    fecha_salida DATE NOT NULL,
    fecha_regreso DATE NOT NULL,
    cupos_totales INT NOT NULL DEFAULT 0,
    cupos_disponibles INT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'programada',
    id_guia INT REFERENCES guia_turistico(id_guia),
    observaciones TEXT,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_paquete, fecha_salida),
    CONSTRAINT salida_paquete_check CHECK (cupos_totales >= 0 AND cupos_disponibles >= 0 AND cupos_disponibles <= cupos_totales),
    CONSTRAINT salida_paquete_check1 CHECK (fecha_regreso >= fecha_salida),
    CONSTRAINT salida_paquete_estado_check CHECK (estado IN ('programada','disponible','agotada','cerrada','cancelada'))
);

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva SERIAL PRIMARY KEY,
    codigo_unico VARCHAR(30) NOT NULL UNIQUE,
    fecha_reserva DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_viaje DATE,
    estado VARCHAR(30) NOT NULL DEFAULT 'solicitada',
    valor_referencial NUMERIC(12,2),
    cant_adultos INT NOT NULL DEFAULT 1,
    cant_menores INT NOT NULL DEFAULT 0,
    observaciones TEXT,
    acepta_no_reembolso BOOLEAN NOT NULL DEFAULT FALSE,
    metodo_contacto VARCHAR(30),
    guia_pdf VARCHAR(255),
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente),
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete),
    precio_total NUMERIC(12,2),
    plan TEXT,
    alergias TEXT,
    mascotas BOOLEAN NOT NULL DEFAULT FALSE,
    id_salida INT REFERENCES salida_paquete(id_salida),
    reembolso_estado VARCHAR(20),
    motivo_cancelacion TEXT,
    reembolso_fecha TIMESTAMP,
    encuesta_enviada BOOLEAN NOT NULL DEFAULT FALSE,
    encuesta_enviada_fecha TIMESTAMP,
    CONSTRAINT chk_reserva_estado CHECK (estado IN ('solicitada','pendiente a pago','confirmada','pagada','en_proceso','completada','cancelada')),
    CONSTRAINT chk_cant_adultos CHECK (cant_adultos >= 1),
    CONSTRAINT chk_cant_menores CHECK (cant_menores >= 0)
);

CREATE TABLE IF NOT EXISTS reserva_seguro (
    id_reserva_seguro SERIAL PRIMARY KEY,
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    id_seguro INT NOT NULL REFERENCES seguro(id_seguro) ON DELETE CASCADE,
    precio_aplicado NUMERIC(10,2) NOT NULL,
    fecha_contratacion DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (id_reserva, id_seguro)
);

CREATE TABLE IF NOT EXISTS reserva_servicio_extra (
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    id_servicio_extra INT NOT NULL REFERENCES servicio_extra(id_servicio_extra),
    PRIMARY KEY (id_reserva, id_servicio_extra)
);

CREATE TABLE IF NOT EXISTS viajero_reserva (
    id_viajero SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    tipo_documento VARCHAR(30) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    idioma VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS itinerario_viaje (
    id_itinerario SERIAL PRIMARY KEY,
    origen VARCHAR(100),
    destino VARCHAR(100),
    fecha_salida DATE,
    fecha_regreso DATE,
    hora_salida TIME,
    hora_regreso TIME,
    medio_transporte VARCHAR(50),
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS itinerario_actividad (
    id_itin_actividad SERIAL PRIMARY KEY,
    dia INT,
    hora_inicio TIME,
    lugar VARCHAR(200),
    descripcion TEXT,
    costos_adicionales NUMERIC(10,2) DEFAULT 0,
    id_actividad INT REFERENCES actividad_turistica(id_actividad),
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favoritos (
    id_favorito SERIAL PRIMARY KEY,
    fecha_agregado DATE NOT NULL DEFAULT CURRENT_DATE,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    UNIQUE (id_cliente, id_paquete)
);

CREATE TABLE IF NOT EXISTS lista_suenos (
    id_sueno SERIAL PRIMARY KEY,
    fecha_inicio_ahorro DATE,
    meta_semanal NUMERIC(10,2),
    meta_mensual NUMERIC(10,2),
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    UNIQUE (id_cliente, id_paquete)
);

CREATE TABLE IF NOT EXISTS historial_busqueda (
    id_busqueda SERIAL PRIMARY KEY,
    destino_buscado VARCHAR(100),
    filtros JSONB,
    fecha_busqueda TIMESTAMP NOT NULL DEFAULT NOW(),
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notificacion (
    id_notificacion SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    mensaje TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS encuesta_pregunta (
    id_pregunta SERIAL PRIMARY KEY,
    texto TEXT NOT NULL,
    tipo_respuesta VARCHAR(50) NOT NULL,
    orden INT NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS encuesta_respuesta (
    id_respuesta SERIAL PRIMARY KEY,
    id_pregunta INT NOT NULL REFERENCES encuesta_pregunta(id_pregunta) ON DELETE CASCADE,
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    respuesta_texto TEXT,
    respuesta_numero INT,
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_pregunta, id_reserva, id_cliente)
);

CREATE TABLE IF NOT EXISTS auditoria_admin (
    id_auditoria SERIAL PRIMARY KEY,
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    id_admin INT NOT NULL REFERENCES cliente(id_cliente)
);

CREATE TABLE IF NOT EXISTS resena_paquete (
    id_resena SERIAL PRIMARY KEY,
    id_paquete INT NOT NULL REFERENCES paquete_turistico(id_paquete) ON DELETE CASCADE,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_reserva INT REFERENCES reserva(id_reserva) ON DELETE SET NULL,
    calificacion SMALLINT,
    calificacion_servicio SMALLINT,
    titulo VARCHAR(120),
    comentario TEXT,
    fecha_resena TIMESTAMP NOT NULL DEFAULT NOW(),
    estado VARCHAR(20) NOT NULL DEFAULT 'visible',
    origen VARCHAR(20) NOT NULL DEFAULT 'real',
    CONSTRAINT chk_resena_calificacion CHECK (calificacion BETWEEN 1 AND 5),
    CONSTRAINT chk_resena_servicio CHECK (calificacion_servicio IS NULL OR calificacion_servicio BETWEEN 1 AND 5),
    CONSTRAINT chk_resena_estado CHECK (estado IN ('visible','oculta','pendiente')),
    CONSTRAINT chk_resena_origen CHECK (origen IN ('real','semilla'))
);

ALTER TABLE cliente ADD COLUMN IF NOT EXISTS acepta_politica_no_reembolso BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE cliente ADD COLUMN IF NOT EXISTS fecha_aceptacion_politica TIMESTAMP;
ALTER TABLE cliente ADD COLUMN IF NOT EXISTS version_politica VARCHAR(20) NOT NULL DEFAULT '1.0';
ALTER TABLE destino ADD COLUMN IF NOT EXISTS video_url VARCHAR(255);
ALTER TABLE proveedor ADD COLUMN IF NOT EXISTS contrasena VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE guia_turistico ADD COLUMN IF NOT EXISTS contrasena VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE paquete_turistico ADD COLUMN IF NOT EXISTS emoji VARCHAR(10) DEFAULT '🧳';
ALTER TABLE paquete_turistico ADD COLUMN IF NOT EXISTS video_url VARCHAR(255);
ALTER TABLE viajero_reserva ADD COLUMN IF NOT EXISTS idioma VARCHAR(50);
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS precio_total NUMERIC(12,2);
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS plan TEXT;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS alergias TEXT;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS mascotas BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS id_salida INT REFERENCES salida_paquete(id_salida);
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS encuesta_enviada BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE reserva ADD COLUMN IF NOT EXISTS encuesta_enviada_fecha TIMESTAMP;
ALTER TABLE resena_paquete ADD COLUMN IF NOT EXISTS origen VARCHAR(20) NOT NULL DEFAULT 'real';
ALTER TABLE resena_paquete ALTER COLUMN calificacion DROP NOT NULL;

UPDATE resena_paquete SET origen = 'real' WHERE origen IS NULL;

ALTER TABLE resena_paquete ALTER COLUMN origen SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_resena_calificacion' AND conrelid = 'resena_paquete'::regclass) THEN
        ALTER TABLE resena_paquete ADD CONSTRAINT chk_resena_calificacion CHECK (calificacion BETWEEN 1 AND 5);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_resena_servicio' AND conrelid = 'resena_paquete'::regclass) THEN
        ALTER TABLE resena_paquete ADD CONSTRAINT chk_resena_servicio CHECK (calificacion_servicio IS NULL OR calificacion_servicio BETWEEN 1 AND 5);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_resena_estado' AND conrelid = 'resena_paquete'::regclass) THEN
        ALTER TABLE resena_paquete ADD CONSTRAINT chk_resena_estado CHECK (estado IN ('visible','oculta','pendiente'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_resena_origen' AND conrelid = 'resena_paquete'::regclass) THEN
        ALTER TABLE resena_paquete ADD CONSTRAINT chk_resena_origen CHECK (origen IN ('real','semilla'));
    END IF;
END $$;

ALTER TABLE resena_paquete DROP CONSTRAINT IF EXISTS uq_resena_paquete_cliente;
ALTER TABLE resena_paquete DROP CONSTRAINT IF EXISTS uq_resena_reserva;
DROP INDEX IF EXISTS uq_resena_real_cliente;

CREATE UNIQUE INDEX IF NOT EXISTS uq_resena_real_reserva ON resena_paquete (id_reserva) WHERE origen = 'real' AND id_reserva IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_resena_paquete_visible ON resena_paquete (id_paquete, estado);
CREATE INDEX IF NOT EXISTS idx_resena_paquete_origen ON resena_paquete (origen, id_paquete);
CREATE INDEX IF NOT EXISTS idx_reserva_encuesta_pendiente ON reserva (estado, encuesta_enviada, fecha_viaje);
CREATE INDEX IF NOT EXISTS idx_cliente_correo ON cliente (correo);
CREATE INDEX IF NOT EXISTS idx_cliente_documento ON cliente (numero_documento);
CREATE INDEX IF NOT EXISTS idx_cliente_nivel ON cliente (id_nivel);
CREATE INDEX IF NOT EXISTS idx_reserva_cliente ON reserva (id_cliente);
CREATE INDEX IF NOT EXISTS idx_reserva_paquete ON reserva (id_paquete);
CREATE INDEX IF NOT EXISTS idx_reserva_estado ON reserva (estado);
CREATE INDEX IF NOT EXISTS idx_reserva_fecha_viaje ON reserva (fecha_viaje);
CREATE INDEX IF NOT EXISTS idx_paquete_destino ON paquete_turistico (id_destino);
CREATE INDEX IF NOT EXISTS idx_paquete_estado ON paquete_turistico (estado);
CREATE INDEX IF NOT EXISTS idx_paquete_fecha ON paquete_turistico (fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_seguro_servicio ON seguro_servicio (id_seguro);
CREATE INDEX IF NOT EXISTS idx_reserva_seguro ON reserva_seguro (id_reserva);
CREATE INDEX IF NOT EXISTS idx_metodo_proveedor ON metodo_pago_proveedor (id_proveedor);
CREATE INDEX IF NOT EXISTS idx_historial_cliente ON historial_busqueda (id_cliente);
CREATE INDEX IF NOT EXISTS idx_notif_cliente ON notificacion (id_cliente);
CREATE INDEX IF NOT EXISTS idx_favoritos_cliente ON favoritos (id_cliente);
CREATE INDEX IF NOT EXISTS idx_promocion_codigo ON promocion (codigo);
CREATE INDEX IF NOT EXISTS idx_auditoria_admin ON auditoria_admin (id_admin);
CREATE INDEX IF NOT EXISTS idx_salida_estado ON salida_paquete (estado);
CREATE INDEX IF NOT EXISTS idx_salida_fecha ON salida_paquete (fecha_salida);
CREATE INDEX IF NOT EXISTS idx_salida_guia ON salida_paquete (id_guia);

INSERT INTO nivel (id_nivel, nombre, min_monto, min_reservas, descripcion, porcentaje_descuento) VALUES
(1, 'Explorador', 0.00, 0, 'Nivel inicial para nuevos viajeros', 0.00),
(2, 'Aventurero', 2000000.00, 2, 'Viajeros con experiencia', 5.00),
(3, 'Viajero Elite', 6000000.00, 5, 'Acceso a promociones exclusivas', 10.00),
(4, 'Embajador', 15000000.00, 10, 'El nivel más alto de MAREVA', 15.00)
ON CONFLICT DO NOTHING;

INSERT INTO insignia (id_insignia, nombre, criterio, imagen_url, estado) VALUES
(1, 'Primera Aventura', 'Completar su primera reserva', NULL, TRUE),
(2, 'Playero', 'Reservar un destino de playa', NULL, TRUE),
(3, 'Montañista', 'Reservar un destino de montaña', NULL, TRUE),
(4, 'Viajero Frecuente', 'Completar 5 reservas', NULL, TRUE),
(5, 'Referidor Estrella', 'Referir 3 amigos que hayan reservado', NULL, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO cliente (id_cliente, nombre, apellido, tipo_documento, numero_documento, telefono, correo, contrasena, rol, codigo_referido, fecha_registro, estado, intentos_fallidos, bloqueado_hasta, id_nivel, acepta_politica_no_reembolso, fecha_aceptacion_politica, version_politica) VALUES
(1, 'Cesar', 'Uzcategui', 'CC', '1000000001', '3100000001', 'cesar@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin', NULL, '2026-11-24', TRUE, 0, NULL, NULL, FALSE, NULL, '1.0'),
(2, 'Andres', 'Aroca', 'CC', '1000000002', '3100000002', 'andres@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin', NULL, '2026-11-24', TRUE, 0, NULL, NULL, FALSE, NULL, '1.0'),
(3, 'Laura', 'Rubiano', 'CC', '1000000003', '3100000003', 'laura@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin', NULL, '2026-11-24', TRUE, 0, NULL, NULL, FALSE, NULL, '1.0'),
(4, 'Sofia', 'Munevar', 'CC', '1000000004', '3100000004', 'sofia@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin', NULL, '2026-11-24', TRUE, 0, NULL, NULL, FALSE, NULL, '1.0'),
(5, 'Nicoll', 'Sabogal', 'CC', '1000000005', '3100000005', 'nicoll@mareva.co', 'scrypt:32768:8:1$OfezC5PlkEjHkACB$d216d80ef624d29146bbc75def4f94e7735245b886e198200cc8ea8503670ffc494d6f71faa458d3720ca6462b5af1cc1b9cc7b0668ee23e8d987a504b314a02', 'admin', NULL, '2026-11-24', TRUE, 0, NULL, NULL, FALSE, NULL, '1.0'),
(6, 'Yadira', 'Narvaez', 'CC', '2000000001', '3200000001', 'yadira@test.co', 'scrypt:32768:8:1$OsPW9JDKU8BF6uy1$c12dc8e295c68587bcc6ff01fcfd1357c394d46c95a19957ec6c2f84b771ef91b9a2191af9a552289ff05fc3301822519acf4c3c1a536efc88f71ee52886e235', 'cliente', 'YN20261', '2026-11-24', TRUE, 0, NULL, 1, FALSE, NULL, '1.0'),
(11, 'Nicoll Valeria', 'Sabogal Narvaez', 'GOOGLE', '1123808371', '+573009654523', 'nicollvaleria.sabogal.9@gmail.com', 'scrypt:32768:8:1$8wdalf8oiyCqbrfS$bc6a9bc74f0cf2e478098688ceab5b9c73856e826103948bf10a8bb25538e39143caa760f8c6dea04d9b72e183f2bc202c1697a33025d804aaaaa412af23239b', 'cliente', NULL, '2026-11-24', TRUE, 0, NULL, 2, FALSE, NULL, '1.0'),
(14, 'Nicoll Valeria', 'Sabogal Narvaez', 'CC', '40987654', '+573009654523', 'yanaca4@hotmail.com', 'scrypt:32768:8:1$DN3ySnGWp2LXlYjy$3a2c24d6a30d77b6f259bdb2d0e7d1041aa8550d82978972389766681004ff164df6e594025fd79b3e8f0cd5037d1eb537d4dc435b5112124d4b5517d4f78edf', 'cliente', NULL, '2026-11-24', TRUE, 0, NULL, NULL, TRUE, '2026-11-24 21:43:17.342381', '1.0'),
(15, 'Nicoll', 'Sabogal', 'GOOGLE', '9043562', '+573009654523', 'fotosnicoll33@gmail.com', 'scrypt:32768:8:1$32mevwKvxN6je0wY$8752f35134943e32d74b734565e07a9efeb538f7f4d7721f283195ad8e04e99bf957e182145fd113ff830e53f2ae1b5662b3a6ba25478fb41281c4532c70ff63', 'cliente', NULL, '2026-11-25', TRUE, 0, NULL, 1, FALSE, NULL, '1.0')
ON CONFLICT DO NOTHING;

INSERT INTO destino (id_destino, nombre_destino, departamento, ciudad, categoria, descripcion, atracciones, docs_requeridos, imagen_principal, estado, video_url) VALUES
(1, 'Cartagena de Indias', 'Bolívar', 'Cartagena', 'playa', 'Ciudad amurallada Patrimonio de la Humanidad con playas caribeñas.', 'Ciudad Amurallada, Islas del Rosario, Castillo de San Felipe, Bocagrande', NULL, 'img/destinos/cartagena_indias.jpeg', TRUE, NULL),
(2, 'Medellín', 'Antioquia', 'Medellín', 'ciudad', 'La ciudad de la eterna primavera, innovadora y cultural.', 'El Poblado, Metro Cable, Pueblito Paisa, Museo de Antioquia', NULL, 'img/destinos/medellin.jpeg', TRUE, NULL),
(3, 'Guatapé', 'Antioquia', 'Guatapé', 'aventura', 'Pueblo colorido con la imponente Piedra del Peñol.', 'La Piedra del Peñol, Embalse de Guatapé, Zócalos pintados', NULL, 'img/destinos/guatape.jpeg', TRUE, NULL),
(4, 'San Andrés', 'San Andrés', 'San Andrés', 'playa', 'El mar de los siete colores en el Caribe colombiano.', 'Hoyo Soplador, Johnny Cay, La Piscinita, El Acuario', NULL, 'img/destinos/san_andres.jpeg', TRUE, NULL),
(5, 'Parque Tayrona', 'Magdalena', 'Santa Marta', 'playa', 'Naturaleza salvaje: selva tropical y playas vírgenes.', 'Cabo San Juan, Playa Cristal, Arrecifes, Pueblito', NULL, 'img/destinos/tayrona.jpeg', TRUE, NULL),
(6, 'Valle del Cocora', 'Quindío', 'Salento', 'montaña', 'Hogar de las palmas de cera, árbol nacional de Colombia.', 'Palmas de Cera, Salento, Finca El Ocaso, Mirador', NULL, 'img/destinos/cocora.jpeg', TRUE, NULL),
(7, 'Barichara', 'Santander', 'Barichara', 'cultural', 'El pueblo más bonito de Colombia, arquitectura colonial.', 'Catedral de la Inmaculada, Camino Real, Capilla de Santa Bárbara', NULL, 'img/destinos/barichara.jpg', TRUE, NULL),
(8, 'Leticia', 'Amazonas', 'Leticia', 'aventura', 'Puerta de entrada a la Amazonía colombiana.', 'Parque Amacayacu, Isla de los Micos, Reserva Tanimboca', NULL, 'img/destinos/leticia.jpeg', TRUE, NULL),
(9, 'Caño Cristales', 'Meta', 'La Macarena', 'aventura', 'El río más hermoso del mundo, famoso por sus colores únicos.', 'Río Caño Cristales, Pozos naturales, Senderismo, Miradores', NULL, 'img/destinos/caño_cristales.jpeg', TRUE, NULL),
(10, 'Eje Cafetero', 'Quindío', 'Armenia', 'cultural', 'Paisaje Cultural Cafetero, Patrimonio de la Humanidad.', 'Fincas cafeteras, Parque del Café, Pueblos patrimonio, Jeep willys', NULL, 'img/destinos/eje_cafetero.jpeg', TRUE, NULL),
(11, 'Nuquí', 'Chocó', 'Nuquí', 'playa', 'Paraíso del Pacífico colombiano, avistamiento de ballenas jorobadas.', 'Playas vírgenes, Avistamiento ballenas, Manglares, Termas', NULL, 'img/destinos/nuqui.jpeg', TRUE, NULL),
(12, 'Barichara Colonial', 'Santander', 'Barichara', 'cultural', 'Arquitectura colonial de piedra y el Camino Real hacia Guane.', 'Catedral Inmaculada, Capilla de Jesús, Camino Real, Guane', NULL, 'img/destinos/barichara_colonial.jpg', TRUE, NULL),
(13, 'Las Lajas', 'Nariño', 'Ipiales', 'cultural', 'Basílica neogótica construida sobre un cañón, ícono religioso.', 'Basílica Las Lajas, Puente, Cascadas, Laguna La Cocha', NULL, 'img/destinos/lajas.jpeg', TRUE, NULL),
(14, 'Villa de Leyva', 'Boyacá', 'Villa de Leyva', 'cultural', 'Plaza empedrada más grande de Colombia, arquitectura colonial.', 'Plaza Mayor, Museo del Desierto, Pozos Azules, Ráquira', NULL, 'img/destinos/leyva.jpeg', TRUE, NULL),
(15, 'Cañón del Chicamocha', 'Santander', 'San Gil', 'aventura', 'Capital colombiana de los deportes extremos y paisajes épicos.', 'Teleférico, Rafting, Parapente, Parque Chicamocha', NULL, 'img/destinos/cañon_chicamocha.jpeg', TRUE, NULL),
(16, 'Mompox', 'Bolívar', 'Mompox', 'cultural', 'Ciudad Patrimonio de la Humanidad a orillas del río Magdalena.', 'Calle Real, Iglesias coloniales, Orfebrería, Festival de Jazz', NULL, 'img/destinos/mompox.jpeg', TRUE, NULL),
(17, 'Sierra Nevada', 'Magdalena', 'Santa Marta', 'aventura', 'La montaña costera más alta del mundo y territorios indígenas.', 'Ciudad Perdida, Comunidades Kogi, Caminatas, Biodiversidad', NULL, 'img/destinos/sierra_nevada.jpeg', TRUE, NULL),
(18, 'Tolú y Coveñas', 'Sucre', 'Tolú', 'playa', 'Playas tranquilas del Caribe colombiano, ideal para el descanso.', 'Playas Tolú, Islas de San Bernardo, Motonáutica, Manglar', NULL, 'img/destinos/tolu.jpeg', TRUE, NULL),
(19, 'Isla Gorgona', 'Cauca', 'Guapi', 'aventura', 'Parque Nacional Natural, antigua prisión y reserva marina única.', 'Buceo, Avistamiento ballenas, Senderismo, Biodiversidad marina', NULL, 'img/destinos/gorgona.jpeg', TRUE, NULL),
(20, 'Capurganá', 'Chocó', 'Acandí', 'playa', 'Pueblo caribeño sin carreteras, paraíso de buceadores.', 'Playa La Caleta, Sapzurro, Arrecifes de coral, Senderismo', NULL, 'img/destinos/capurgana.jpeg', TRUE, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO proveedor (id_proveedor, nombre, nit, tipo_empresa, descripcion, direccion, ciudad, telefono, correo, nombre_contacto, telefono_contacto, correo_contacto, estado, contrasena) VALUES
(1, 'Hotel Las Américas', '800100200-1', 'Hotel', 'Hotel 5 estrellas en Cartagena', NULL, 'Cartagena', '6056543210', 'reservas@lasamericas.co', 'María Torres', '3001234567', NULL, TRUE, 'scrypt:32768:8:1$RYE8IIScR6B2VzdH$28ab79bc00e691b705a55e1d40099a5ba47a91f8c5a91969b0281dba8372e5d103c9e6461d69bf6577598fbe348cb9cff923907bf26449f04fcba6176faff8a2'),
(2, 'Avianca', '860002964-4', 'Aerolínea', 'Aerolínea nacional', NULL, 'Bogotá', '018000953434', 'grupos@avianca.com', 'Carlos Reyes', '3009876543', NULL, TRUE, 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0'),
(3, 'Decameron Colombia', '800112233-5', 'Todo incluido', 'Resorts todo incluido en Colombia', NULL, 'San Andrés', '6085121212', 'reservas@decameron.co', 'Ana Gómez', '3152345678', NULL, TRUE, 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0'),
(4, 'Ecoturismo Tayrona', '900345678-2', 'Operador', 'Operador turístico local Tayrona', NULL, 'Santa Marta', '3123456789', 'info@ecotayrona.co', 'Pedro Silva', '3123456789', NULL, TRUE, 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0'),
(5, 'CocoraTours', '900567890-3', 'Operador', 'Tours en el Quindío', NULL, 'Salento', '3145678901', 'info@cocoratours.co', 'Juliana Ríos', '3145678901', NULL, TRUE, 'scrypt:32768:8:1$Y48DfJ4449NTuVQY$5c2981bb49d79dc53471b4e38017e7d255024511e18f8e6ea9d6739e9d6076fc8da20d32cb9cc40dddcb67cc79aea84f5e944193c36e2252a3b649bf52500da0')
ON CONFLICT DO NOTHING;

INSERT INTO metodo_pago_proveedor (id_metodo_proveedor, id_proveedor, tipo_metodo, entidad, titular, numero_referencia, instrucciones) VALUES
(1, 1, 'cuenta_bancaria', 'Bancolombia', 'Hotel Las Americas SAS', '12345678901', 'Transferir y enviar comprobante al correo del proveedor'),
(2, 5, 'nequi', 'Nequi', 'CocoraTours', '3001234567', NULL),
(3, 5, 'daviplata', 'Daviplata', 'CocoraTours', '3209876543', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO guia_turistico (id_guia, nombre, apellido, idiomas, especialidad, telefono, correo, estado, contrasena) VALUES
(1, 'Andrés', 'Herrera', 'Español, Inglés', 'Cartagena histórica y playas', '3100001111', 'andres.guia@mareva.co', TRUE, 'scrypt:32768:8:1$DyUDJeiqrqIuCpOb$c8e99c7e7eae986e4f6d2a06188601687d96ef43f38ed10b1b20d509281d86ecc902d75b7e08e9e3fa89ba25a5488612376dd97555c73a42c92a5a40967a8576'),
(2, 'Valentina', 'López', 'Español, Inglés, Francés', 'Ecoturismo y naturaleza', '3100002222', 'valentina.guia@mareva.co', TRUE, 'scrypt:32768:8:1$BmwNjfSVYTonnYPl$05a81a5f442d6ef99062a3bab28179e8759d28727f20d5639d0c0da82319c4de3dab02c1075708d912f3bbb36f0030e287088a39228453a5bda98cd01ffe92c3'),
(3, 'Miguel', 'Castillo', 'Español', 'Aventura y deportes extremos', '3100003333', 'miguel.guia@mareva.co', TRUE, 'scrypt:32768:8:1$AELZ8i2lbW4gWGaS$c93d8a0d0ce87f2c85e74f63337cb6d60ead433feddece2e6a1311fdb52d633596f8d755fb690f34d34a2b7e1344066ea5a3978567b5d0509b827ca2905d387b')
ON CONFLICT DO NOTHING;

INSERT INTO tipo_seguro (id_tipo_seguro, nombre, descripcion, cobertura_general) VALUES
(1, 'Responsabilidad Civil', 'Seguro obligatorio por ley para prestadores de servicios turísticos', 'Cubre daños a terceros dentro de las instalaciones o durante el servicio'),
(2, 'Asistencia Médica', 'Seguro opcional de salud para el viajero', 'Cubre emergencias médicas, hospitalización y asistencia en viaje'),
(3, 'Cancelación y Equipaje', 'Seguro opcional contra imprevistos del viaje', 'Cubre cancelaciones, pérdida o daño de equipaje')
ON CONFLICT DO NOTHING;

INSERT INTO seguro (id_seguro, id_tipo_seguro, nombre, cobertura, precio, es_obligatorio, descripcion, estado) VALUES
(1, 1, 'RC Alojamiento', 'Accidentes dentro del alojamiento hasta $50.000.000', 0.00, TRUE, 'Obligatorio — incluido en el costo del alojamiento', TRUE),
(2, 1, 'RC Transporte', 'Accidentes durante el traslado hasta $50.000.000', 0.00, TRUE, 'Obligatorio — incluido en el costo del transporte', TRUE),
(3, 1, 'RC Actividad', 'Accidentes durante la actividad hasta $30.000.000', 0.00, TRUE, 'Obligatorio — incluido en el costo de la actividad', TRUE),
(4, 2, 'Seguro Médico Básico', 'Emergencias médicas y hospitalización hasta $80.000.000', 120000.00, FALSE, 'Recomendado para viajes nacionales', TRUE),
(5, 2, 'Seguro Médico Completo', 'Médico, dental y evacuación hasta $200.000.000', 280000.00, FALSE, 'Cobertura amplia recomendada', TRUE),
(6, 3, 'Seguro Premium', 'Cancelación, equipaje y médico hasta $500.000.000', 520000.00, FALSE, 'Máxima protección para tu viaje', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO alojamiento (id_alojamiento, nombre, tipo_alojamiento, ciudad, direccion, servicios, id_proveedor) VALUES
(1, 'Hotel Coral Caribe', 'Hotel', 'San Andrés', NULL, 'Piscina, desayuno, WiFi, restaurante, acceso a playa', 1),
(2, 'Cabañas Cabo San Juan', 'Cabaña', 'Santa Marta', NULL, 'Alojamiento ecológico, restaurante, acceso a playa, senderos', 1),
(3, 'Hotel Coveñas Beach', 'Resort', 'Coveñas', NULL, 'Piscina, playa, desayuno, restaurante, actividades acuáticas', 1),
(4, 'Hotel Guatapé Lago', 'Hotel', 'Guatapé', NULL, 'Vista al embalse, desayuno, WiFi, restaurante, parqueadero', 1),
(5, 'Casa Colonial Barichara', 'Casa Hotel', 'Barichara', NULL, 'Desayuno, jardín, WiFi, terraza, restaurante', 1),
(6, 'Ecohotel Gorgona', 'Ecohotel', 'Guapi', NULL, 'Alojamiento ecológico, alimentación, senderismo, excursiones', 1),
(7, 'Posada Colonial Boyacá', 'Posada', 'Villa de Leyva', NULL, 'Desayuno, chimenea, jardín, WiFi, restaurante', 1),
(8, 'Hotel Desierto Tatacoa', 'Hotel', 'Villavieja', NULL, 'Piscina, restaurante, desayuno, observación astronómica', 1),
(9, 'Hotel Santuario Nariño', 'Hotel', 'Ipiales', NULL, 'Desayuno, restaurante, WiFi, parqueadero, servicio de habitaciones', 1),
(10, 'Hotel Salento Real', 'Hotel', 'Salento', NULL, 'Desayuno, WiFi, restaurante, parqueadero, jardín', 1),
(11, 'Hostería Piedra del Peñol', 'Hostería', 'Guatapé', NULL, 'Desayuno, WiFi, terraza, restaurante, actividades acuáticas', 1),
(12, 'Ecohotel Tayrona', 'Ecohotel', 'Santa Marta', NULL, 'Desayuno, senderismo, restaurante, zonas verdes, WiFi', 1),
(13, 'Eco Lodge Sierra Nevada', 'Eco Lodge', 'Santa Marta', NULL, 'Alojamiento ecológico, alimentación, senderismo, guía local', 1),
(14, 'Cabañas Isla Gorgona', 'Cabaña', 'Guapi', NULL, 'Alimentación, acceso a playa, senderismo, zonas naturales', 1),
(15, 'Eco Lodge Selva Amazónica', 'Eco Lodge', 'Leticia', NULL, 'Alojamiento ecológico, alimentación, excursiones, senderismo', 1),
(16, 'Hotel Chicamocha', 'Hotel', 'San Gil', NULL, 'Piscina, desayuno, WiFi, restaurante, actividades extremas', 1),
(17, 'Hotel Nuquí Pacífico', 'Hotel', 'Nuquí', NULL, 'Desayuno, restaurante, acceso a playa, WiFi, excursiones', 1),
(18, 'Hotel Poblado Central', 'Hotel', 'Medellín', NULL, 'WiFi, desayuno, gimnasio, restaurante, aire acondicionado', 1),
(19, 'Ecohotel Río Guayabero', 'Ecohotel', 'La Macarena', NULL, 'Alojamiento ecológico, alimentación, senderismo, zonas verdes', 1),
(20, 'Hotel Primavera Medellín', 'Hotel', 'Medellín', NULL, 'Desayuno, WiFi, restaurante, recepción 24 horas', 1),
(21, 'Hotel Amazonas', 'Hotel', 'Leticia', NULL, 'Piscina, restaurante, desayuno, WiFi, excursiones', 1),
(22, 'Hotel Mompox Real', 'Hotel', 'Mompox', NULL, 'Desayuno, WiFi, restaurante, piscina, terraza', 1),
(23, 'Hotel Sierra Nevada', 'Hotel', 'Santa Marta', NULL, 'Desayuno, WiFi, restaurante, piscina, excursiones', 1),
(24, 'Hotel Caño Cristales', 'Hotel', 'La Macarena', NULL, 'Desayuno, restaurante, WiFi, excursiones, guía local', 1),
(25, 'Hotel Villa de Leyva', 'Hotel', 'Villa de Leyva', NULL, 'Desayuno, WiFi, restaurante, jardín, parqueadero', 1),
(26, 'Eco Lodge Nuquí', 'Eco Lodge', 'Nuquí', NULL, 'Alojamiento ecológico, alimentación, playa, senderismo', 1),
(27, 'Hotel Eje Cafetero', 'Hotel', 'Armenia', NULL, 'Piscina, desayuno, WiFi, gimnasio, restaurante', 1),
(28, 'Hotel Aventura Santander', 'Hotel', 'San Gil', NULL, 'Desayuno, restaurante, WiFi, parqueadero, deportes extremos', 1),
(29, 'Casa Colonial Mompox', 'Casa Hotel', 'Mompox', NULL, 'Desayuno, jardín, WiFi, restaurante, terraza', 1),
(30, 'Eco Lodge Capurganá', 'Eco Lodge', 'Acandí', NULL, 'Alojamiento ecológico, alimentación, playa, buceo, senderismo', 1),
(31, 'Decameron San Andrés', 'Resort', 'San Andrés', NULL, 'Todo incluido, piscina, playa privada, restaurantes, bar', 1),
(32, 'Ecohostal La Tatacoa', 'Hostal', 'Villavieja', NULL, 'Zona de camping, restaurante, terraza, observatorio astronómico', 1),
(33, 'Hotel Barichara Colonial', 'Hotel', 'Barichara', NULL, 'Desayuno, WiFi, piscina, restaurante, terraza', 1),
(34, 'Finca Cafetera Cocora', 'Finca', 'Salento', NULL, 'Desayuno, tour cafetero, zonas verdes, WiFi, parqueadero', 1),
(35, 'Finca Cafetera Armenia', 'Finca', 'Armenia', NULL, 'Desayuno, tour cafetero, jardín, restaurante, parqueadero', 1),
(36, 'Hotel Colonial Cartagena', 'Hotel Boutique', 'Cartagena', NULL, 'Desayuno, WiFi, piscina, restaurante, servicio de habitaciones', 1),
(37, 'Hotel Tolú Caribe', 'Hotel', 'Tolú', NULL, 'Piscina, desayuno, restaurante, acceso a playa, WiFi', 1),
(38, 'Hotel Capurganá Caribe', 'Hotel', 'Acandí', NULL, 'Desayuno, restaurante, WiFi, acceso a playa, excursiones', 1),
(39, 'Hotel Caribe Plaza', 'Hotel', 'Cartagena', NULL, 'Piscina, WiFi, desayuno, aire acondicionado, recepción 24 horas', 1),
(40, 'Hotel Las Lajas', 'Hotel', 'Ipiales', NULL, 'Desayuno, WiFi, restaurante, parqueadero, recepción 24 horas', 1)
ON CONFLICT DO NOTHING;

INSERT INTO alimentacion (id_alimentacion, restaurante, tipo_comida, tipo_servicio, incluye_bebidas, precio, id_proveedor) VALUES
(1, 'Playa Olímpica Café', 'Comida Típica', 'Desayuno', TRUE, 30000.00, 1),
(2, 'Playa Tolú Café', 'Comida Típica', 'Desayuno', TRUE, 30000.00, 1),
(3, 'Capurganá Mariscos', 'Mariscos', 'Cena', TRUE, 70000.00, 1),
(4, 'Camino Real Restaurante', 'Comida Típica', 'Cena', TRUE, 55000.00, 1),
(5, 'Sabor Cartagenero', 'Comida Típica', 'Almuerzo', TRUE, 55000.00, 1),
(6, 'Mompox Café Colonial', 'Cafetería', 'Desayuno', TRUE, 28000.00, 1),
(7, 'Finca Cafetera Restaurante', 'Comida Típica', 'Cena', TRUE, 55000.00, 1),
(8, 'Sabores Boyacenses', 'Comida Boyacense', 'Cena', TRUE, 55000.00, 1),
(9, 'Café Armenia', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(10, 'Pacífico Nuquí', 'Comida del Pacífico', 'Almuerzo', TRUE, 60000.00, 1),
(11, 'Tolú Caribe Restaurante', 'Comida Caribeña', 'Almuerzo', TRUE, 45000.00, 1),
(12, 'Las Lajas Restaurante', 'Comida Nariñense', 'Almuerzo', TRUE, 40000.00, 1),
(13, 'Piedra del Peñol Café', 'Comida Rápida', 'Refrigerio', TRUE, 25000.00, 1),
(14, 'Nuquí Mariscos', 'Mariscos', 'Cena', TRUE, 75000.00, 1),
(15, 'Mompox Sabores', 'Comida Caribeña', 'Almuerzo', TRUE, 45000.00, 1),
(16, 'Eje Cafetero Gourmet', 'Comida Colombiana', 'Almuerzo', TRUE, 45000.00, 1),
(17, 'Sabores de Nariño', 'Comida Típica', 'Cena', TRUE, 50000.00, 1),
(18, 'Cabo San Juan Food', 'Comida Típica', 'Cena', TRUE, 50000.00, 1),
(19, 'Plaza Mayor Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(20, 'Cocora Gourmet', 'Comida Colombiana', 'Almuerzo', TRUE, 45000.00, 1),
(21, 'Mar y Sol Cartagena', 'Mariscos', 'Cena', TRUE, 70000.00, 1),
(22, 'Sierra Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(23, 'Caño Cristales Gourmet', 'Comida Colombiana', 'Almuerzo', TRUE, 50000.00, 1),
(24, 'Río Guayabero Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(25, 'Sierra Nevada Restaurante', 'Comida Caribeña', 'Almuerzo', TRUE, 50000.00, 1),
(26, 'Primavera Restaurante', 'Internacional', 'Desayuno', TRUE, 30000.00, 1),
(27, 'Restaurante Caribe Plaza', 'Comida Caribeña', 'Desayuno', TRUE, 35000.00, 1),
(28, 'Colonial Café', 'Cafetería', 'Desayuno', TRUE, 28000.00, 1),
(29, 'Capurganá Caribe', 'Comida Caribeña', 'Almuerzo', TRUE, 50000.00, 1),
(30, 'Sabores Ancestrales', 'Comida Típica', 'Cena', TRUE, 60000.00, 1),
(31, 'Playa La Caleta Café', 'Comida Típica', 'Desayuno', TRUE, 30000.00, 1),
(32, 'Salento Café', 'Cafetería', 'Refrigerio', TRUE, 20000.00, 1),
(33, 'Río Magdalena Restaurante', 'Comida Típica', 'Cena', TRUE, 55000.00, 1),
(34, 'Isla Gorgona Restaurante', 'Mariscos', 'Cena', TRUE, 70000.00, 1),
(35, 'Aventura Gourmet', 'Comida Colombiana', 'Cena', TRUE, 60000.00, 1),
(36, 'Gorgona Natural', 'Comida del Pacífico', 'Almuerzo', TRUE, 55000.00, 1),
(37, 'Sabores de Guatapé', 'Comida Típica', 'Almuerzo', TRUE, 40000.00, 1),
(38, 'Amazonas Sabores', 'Comida Amazónica', 'Almuerzo', TRUE, 55000.00, 1),
(39, 'Tayrona Natural', 'Comida Caribeña', 'Almuerzo', TRUE, 45000.00, 1),
(40, 'Ipiales Café', 'Cafetería', 'Desayuno', TRUE, 28000.00, 1),
(41, 'Caribbean Taste San Andrés', 'Comida Caribeña', 'Almuerzo', TRUE, 60000.00, 1),
(42, 'Selva Gourmet', 'Comida Colombiana', 'Cena', TRUE, 65000.00, 1),
(43, 'Gorgona Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(44, 'Río Amazonas Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(45, 'Macarena Sabores', 'Comida Típica', 'Cena', TRUE, 55000.00, 1),
(46, 'Coveñas Mariscos', 'Mariscos', 'Cena', TRUE, 70000.00, 1),
(47, 'Finca El Ocaso Restaurante', 'Comida Típica', 'Cena', TRUE, 55000.00, 1),
(48, 'Sabor Paisa Medellín', 'Comida Paisa', 'Almuerzo', TRUE, 45000.00, 1),
(49, 'Villa de Leyva Gourmet', 'Comida Colombiana', 'Almuerzo', TRUE, 45000.00, 1),
(50, 'Chicamocha Restaurante', 'Comida Santandereana', 'Almuerzo', TRUE, 50000.00, 1),
(51, 'Desierto Gourmet', 'Comida Típica', 'Cena', TRUE, 50000.00, 1),
(52, 'Paisa Gourmet', 'Comida Colombiana', 'Cena', TRUE, 60000.00, 1),
(53, 'Johnny Cay Restaurant', 'Comida Típica', 'Almuerzo', TRUE, 50000.00, 1),
(54, 'Lago Restaurante', 'Internacional', 'Cena', TRUE, 55000.00, 1),
(55, 'Island Gourmet', 'Mariscos', 'Cena', TRUE, 85000.00, 1),
(56, 'Barichara Sabores', 'Comida Santandereana', 'Almuerzo', TRUE, 45000.00, 1),
(57, 'San Gil Café', 'Cafetería', 'Desayuno', TRUE, 30000.00, 1),
(58, 'Selva Restaurante', 'Comida Colombiana', 'Desayuno', TRUE, 30000.00, 1),
(59, 'Observatorio Café', 'Cafetería', 'Refrigerio', TRUE, 25000.00, 1),
(60, 'Tatacoa Restaurante', 'Comida Colombiana', 'Almuerzo', TRUE, 40000.00, 1)
ON CONFLICT DO NOTHING;

INSERT INTO transporte (id_transporte, tipo, empresa, ruta, capacidad, hora_salida, hora_regreso, fecha_inicio, fecha_fin, id_proveedor) VALUES
(1, 'Aéreo', 'Avianca', 'Cali → Buenaventura', 100, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 2),
(2, 'Aéreo', 'Avianca', 'Medellín → Apartadó', 100, '07:00:00', '17:00:00', '2026-01-01', '2027-12-31', 2),
(3, 'Aéreo', 'Avianca', 'Bogotá → Santa Marta', 150, '07:30:00', '18:30:00', '2026-01-01', '2027-12-31', 2),
(4, 'Aéreo', 'Avianca', 'Bogotá → Armenia', 150, '08:30:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(5, 'Aéreo', 'Avianca', 'Medellín → Nuquí', 100, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 2),
(6, 'Aéreo', 'Avianca', 'Bogotá → Sincelejo', 150, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(7, 'Aéreo', 'Avianca', 'Bogotá → San Andrés', 150, '06:30:00', '17:30:00', '2026-01-01', '2027-12-31', 2),
(8, 'Aéreo', 'Avianca', 'Bogotá → Pasto', 150, '07:30:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(9, 'Aéreo', 'Avianca', 'Bogotá → Leticia', 150, '09:00:00', '17:00:00', '2026-01-01', '2027-12-31', 2),
(10, 'Aéreo', 'Avianca', 'Bogotá → Cartagena', 150, '08:00:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(11, 'Aéreo', 'Avianca', 'Bogotá → Medellín', 150, '07:00:00', '19:00:00', '2026-01-01', '2027-12-31', 2),
(12, 'Aéreo', 'Avianca', 'Bogotá → Villavicencio', 150, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(13, 'Aéreo', 'Avianca', 'Bogotá → Bucaramanga', 150, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 2),
(14, 'Aéreo', 'Avianca', 'Bogotá → Mompox', 100, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 2),
(15, 'Terrestre', 'CocoraTours', 'Santa Marta → Sierra Nevada → Santa Marta', 19, '05:30:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(16, 'Terrestre', 'CocoraTours', 'Bucaramanga → Barichara → Bucaramanga', 19, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(17, 'Terrestre', 'CocoraTours', 'Leticia → Reserva Amazónica → Leticia', 19, '07:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(18, 'Terrestre', 'CocoraTours', 'San Andrés → Playa de San Luis → San Andrés', 19, '09:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(19, 'Terrestre', 'CocoraTours', 'Buenaventura → Gorgona', 19, '07:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(20, 'Terrestre', 'CocoraTours', 'Neiva → Villavieja → Tatacoa', 19, '06:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(21, 'Terrestre', 'CocoraTours', 'Necoclí → Capurganá', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(22, 'Terrestre', 'CocoraTours', 'Armenia → Salento → Armenia', 19, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(23, 'Terrestre', 'CocoraTours', 'Pasto → Las Lajas → Pasto', 19, '07:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(24, 'Terrestre', 'CocoraTours', 'Armenia → Finca Cafetera → Armenia', 19, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(25, 'Terrestre', 'CocoraTours', 'Mompox → Santa Cruz de Mompox → Mompox', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(26, 'Terrestre', 'CocoraTours', 'Bogotá → Villa de Leyva → Bogotá', 19, '06:00:00', '19:00:00', '2026-01-01', '2027-12-31', 3),
(27, 'Terrestre', 'CocoraTours', 'Villa de Leyva → Ráquira → Villa de Leyva', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(28, 'Terrestre', 'CocoraTours', 'Cartagena → Barú → Cartagena', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(29, 'Terrestre', 'CocoraTours', 'Villavieja → Observatorio → Villavieja', 19, '18:00:00', '23:00:00', '2026-01-01', '2027-12-31', 3),
(30, 'Terrestre', 'CocoraTours', 'Sincelejo → Tolú → Coveñas', 19, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(31, 'Terrestre', 'CocoraTours', 'Guatapé → Piedra del Peñol → Guatapé', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(32, 'Terrestre', 'CocoraTours', 'Barichara → Camino Real → Barichara', 19, '08:00:00', '16:00:00', '2026-01-01', '2027-12-31', 3),
(33, 'Terrestre', 'CocoraTours', 'Medellín → Guatapé → Medellín', 19, '07:00:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(34, 'Terrestre', 'CocoraTours', 'Bucaramanga → Chicamocha → Bucaramanga', 19, '06:30:00', '18:00:00', '2026-01-01', '2027-12-31', 3),
(35, 'Terrestre', 'CocoraTours', 'La Macarena → Caño Cristales → La Macarena', 19, '06:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(36, 'Terrestre', 'CocoraTours', 'Nuquí → Playa Olímpica → Nuquí', 19, '08:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3),
(37, 'Terrestre', 'CocoraTours', 'Santa Marta → Tayrona → Santa Marta', 19, '06:00:00', '17:00:00', '2026-01-01', '2027-12-31', 3)
ON CONFLICT DO NOTHING;

INSERT INTO actividad_turistica (id_actividad, nombre, tipo, duracion_horas, costo, id_destino, id_guia, id_proveedor) VALUES
(1, 'Jardín Botánico y Mariposario', 'Naturaleza', 3.0, 120000.00, 10, NULL, NULL),
(2, 'Tour Arquitectura Colonial', 'Cultural', 3.0, 120000.00, 7, NULL, NULL),
(3, 'Avistamiento de Delfines Rosados', 'Naturaleza', 3.0, 120000.00, 8, NULL, NULL),
(4, 'Tour Costero Tolú - Coveñas', 'Playa', 3.0, 120000.00, 18, NULL, NULL),
(5, 'Senderismo Parque Tayrona', 'Naturaleza', 3.0, 120000.00, 5, NULL, NULL),
(6, 'Pueblo de los Zócalos', 'Cultural', 3.0, 120000.00, 3, NULL, NULL),
(7, 'Miradores del Cañón', 'Naturaleza', 3.0, 120000.00, 13, NULL, NULL),
(8, 'Camino Real de Barichara', 'Cultural', 3.0, 120000.00, 7, NULL, NULL),
(9, 'Tour Finca Cafetera', 'Cultural', 3.0, 120000.00, 10, NULL, NULL),
(10, 'Islas del Rosario', 'Playa', 3.0, 120000.00, 1, NULL, NULL),
(11, 'Cañón del Chicamocha', 'Naturaleza', 3.0, 120000.00, 15, NULL, NULL),
(12, 'Senderismo Parque Gorgona', 'Naturaleza', 3.0, 180000.00, 19, NULL, NULL),
(13, 'Caminata Valle del Cocora', 'Naturaleza', 3.0, 120000.00, 6, NULL, NULL),
(14, 'Piedra del Peñol', 'Aventura', 3.0, 200000.00, 3, NULL, NULL),
(15, 'Taller de Filigrana', 'Cultural', 3.0, 120000.00, 16, NULL, NULL),
(16, 'Tour Johnny Cay', 'Playa', 3.0, 120000.00, 4, NULL, NULL),
(17, 'Taller de Papel Artesanal', 'Cultural', 3.0, 120000.00, 12, NULL, NULL),
(18, 'Tour Cultural de Ipiales', 'Cultural', 3.0, 120000.00, 13, NULL, NULL),
(19, 'Tour Bahía El Aguacate', 'Playa', 3.0, 120000.00, 20, NULL, NULL),
(20, 'Cata de Café Colombiano', 'Gastronomía', 3.0, 120000.00, 10, NULL, NULL),
(21, 'Tour Islas de San Bernardo', 'Playa', 3.0, 120000.00, 18, NULL, NULL),
(22, 'Navegación Río Guayabero', 'Naturaleza', 3.0, 120000.00, 9, NULL, NULL),
(23, 'Recorrido Comuna 13', 'Cultural', 3.0, 120000.00, 2, NULL, NULL),
(24, 'Santuario de Las Lajas', 'Cultural', 3.0, 120000.00, 13, NULL, NULL),
(25, 'Senderismo Sierra de La Macarena', 'Aventura', 3.0, 200000.00, 9, NULL, NULL),
(26, 'Navegación por el Río Magdalena', 'Naturaleza', 3.0, 120000.00, 16, NULL, NULL),
(27, 'Tour Embalse de Guatapé', 'Naturaleza', 3.0, 120000.00, 3, NULL, NULL),
(28, 'Visita a Caño Cristales', 'Naturaleza', 3.0, 120000.00, 9, NULL, NULL),
(29, 'Caminata por Bosque Tropical', 'Naturaleza', 3.0, 120000.00, 17, NULL, NULL),
(30, 'Senderismo Selva Pacífica', 'Aventura', 3.0, 200000.00, 11, NULL, NULL),
(31, 'Tour Pueblito Paisa', 'Cultural', 3.0, 120000.00, 2, NULL, NULL),
(32, 'Buceo y Vida Marina', 'Aventura', 3.0, 200000.00, 19, NULL, NULL),
(33, 'Snorkel Caribeño Capurganá', 'Aventura', 3.0, 200000.00, 20, NULL, NULL),
(34, 'Taller de Papel Artesanal', 'Cultural', 3.0, 120000.00, 7, NULL, NULL),
(35, 'Playa Cabo San Juan', 'Playa', 3.0, 120000.00, 5, NULL, NULL),
(36, 'Avistamiento de Ballenas', 'Naturaleza', 3.0, 180000.00, 11, NULL, NULL),
(37, 'Senderismo Sierra Nevada', 'Naturaleza', 3.0, 120000.00, 17, NULL, NULL),
(38, 'Tour Gastronómico Caribeño', 'Aventura', 3.0, 200000.00, 1, NULL, NULL),
(39, 'Tour Finca Cafetera', 'Cultural', 3.0, 120000.00, 6, NULL, NULL),
(40, 'Senderismo Selva Amazónica', 'Naturaleza', 3.0, 120000.00, 8, NULL, NULL),
(41, 'Avistamiento de Aves', 'Naturaleza', 3.0, 120000.00, 6, NULL, NULL),
(42, 'Parapente en Chicamocha', 'Aventura', 3.0, 200000.00, 15, NULL, NULL),
(43, 'Museo Paleontológico del Desierto', 'Cultural', 3.0, 120000.00, 14, NULL, NULL),
(44, 'Plaza Mayor y Villa de Leyva', 'Cultural', 3.0, 120000.00, 14, NULL, NULL),
(45, 'Avistamiento de Fauna', 'Naturaleza', 3.0, 120000.00, 5, NULL, NULL),
(46, 'Senderismo La Coquerita', 'Naturaleza', 3.0, 120000.00, 20, NULL, NULL),
(47, 'City Tour Medellín', 'Cultural', 3.0, 120000.00, 2, NULL, NULL),
(48, 'Snorkel Golfo de Morrosquillo', 'Aventura', 3.0, 200000.00, 18, NULL, NULL),
(49, 'Playa y Snorkel Pacífico', 'Playa', 3.0, 120000.00, 11, NULL, NULL),
(50, 'Tour Colonial de Mompox', 'Cultural', 3.0, 120000.00, 16, NULL, NULL),
(51, 'Tour de San Gil', 'Aventura', 3.0, 200000.00, 15, NULL, NULL),
(52, 'Tour Arquitectura Colonial', 'Cultural', 3.0, 120000.00, 12, NULL, NULL),
(53, 'Experiencia Cultural Indígena', 'Cultural', 3.0, 120000.00, 17, NULL, NULL),
(54, 'City Tour Cartagena Histórica', 'Cultural', 3.0, 120000.00, 1, NULL, NULL),
(55, 'Tour Vuelta a la Isla', 'Naturaleza', 3.0, 120000.00, 4, NULL, NULL),
(56, 'Camino Real de Barichara', 'Cultural', 3.0, 120000.00, 12, NULL, NULL),
(57, 'Snorkel Caribeño', 'Aventura', 3.0, 200000.00, 4, NULL, NULL),
(58, 'Canotaje por el Río Amazonas', 'Aventura', 3.0, 200000.00, 8, NULL, NULL),
(59, 'Cerámica artesanal en Ráquira', 'Cultural', 3.0, 120000.00, 14, NULL, NULL),
(60, 'Avistamiento de Fauna', 'Naturaleza', 3.0, 120000.00, 19, NULL, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO seguro_servicio (id_seguro_servicio, id_seguro, id_alojamiento, id_alimentacion, id_transporte, id_actividad) VALUES
(1, 1, 29, NULL, NULL, NULL),
(2, 1, 6, NULL, NULL, NULL),
(3, 1, 8, NULL, NULL, NULL),
(4, 1, 30, NULL, NULL, NULL),
(5, 1, 28, NULL, NULL, NULL),
(6, 1, 3, NULL, NULL, NULL),
(7, 1, 14, NULL, NULL, NULL),
(8, 1, 35, NULL, NULL, NULL),
(9, 1, 9, NULL, NULL, NULL),
(10, 1, 7, NULL, NULL, NULL),
(11, 1, 16, NULL, NULL, NULL),
(12, 1, 4, NULL, NULL, NULL),
(13, 1, 36, NULL, NULL, NULL),
(14, 1, 23, NULL, NULL, NULL),
(15, 1, 1, NULL, NULL, NULL),
(16, 1, 22, NULL, NULL, NULL),
(17, 1, 39, NULL, NULL, NULL),
(18, 1, 11, NULL, NULL, NULL),
(19, 1, 33, NULL, NULL, NULL),
(20, 1, 17, NULL, NULL, NULL),
(21, 1, 31, NULL, NULL, NULL),
(22, 1, 18, NULL, NULL, NULL),
(23, 1, 12, NULL, NULL, NULL),
(24, 1, 10, NULL, NULL, NULL),
(25, 1, 34, NULL, NULL, NULL),
(26, 1, 2, NULL, NULL, NULL),
(27, 1, 20, NULL, NULL, NULL),
(28, 1, 26, NULL, NULL, NULL),
(29, 1, 25, NULL, NULL, NULL),
(30, 1, 27, NULL, NULL, NULL),
(31, 1, 37, NULL, NULL, NULL),
(32, 1, 19, NULL, NULL, NULL),
(33, 1, 32, NULL, NULL, NULL),
(34, 1, 24, NULL, NULL, NULL),
(35, 1, 38, NULL, NULL, NULL),
(36, 1, 15, NULL, NULL, NULL),
(37, 1, 40, NULL, NULL, NULL),
(38, 1, 13, NULL, NULL, NULL),
(39, 1, 5, NULL, NULL, NULL),
(40, 1, 21, NULL, NULL, NULL),
(41, 2, NULL, NULL, 32, NULL),
(42, 2, NULL, NULL, 24, NULL),
(43, 2, NULL, NULL, 37, NULL),
(44, 2, NULL, NULL, 19, NULL),
(45, 2, NULL, NULL, 5, NULL),
(46, 2, NULL, NULL, 21, NULL),
(47, 2, NULL, NULL, 13, NULL),
(48, 2, NULL, NULL, 15, NULL),
(49, 2, NULL, NULL, 2, NULL),
(50, 2, NULL, NULL, 18, NULL),
(51, 2, NULL, NULL, 12, NULL),
(52, 2, NULL, NULL, 10, NULL),
(53, 2, NULL, NULL, 34, NULL),
(54, 2, NULL, NULL, 33, NULL),
(55, 2, NULL, NULL, 17, NULL),
(56, 2, NULL, NULL, 31, NULL),
(57, 2, NULL, NULL, 11, NULL),
(58, 2, NULL, NULL, 27, NULL),
(59, 2, NULL, NULL, 26, NULL),
(60, 2, NULL, NULL, 25, NULL),
(61, 2, NULL, NULL, 20, NULL),
(62, 2, NULL, NULL, 7, NULL),
(63, 2, NULL, NULL, 9, NULL),
(64, 2, NULL, NULL, 14, NULL),
(65, 2, NULL, NULL, 35, NULL),
(66, 2, NULL, NULL, 3, NULL),
(67, 2, NULL, NULL, 1, NULL),
(68, 2, NULL, NULL, 22, NULL),
(69, 2, NULL, NULL, 4, NULL),
(70, 2, NULL, NULL, 36, NULL),
(71, 2, NULL, NULL, 23, NULL),
(72, 2, NULL, NULL, 16, NULL),
(73, 2, NULL, NULL, 29, NULL),
(74, 2, NULL, NULL, 6, NULL),
(75, 2, NULL, NULL, 30, NULL),
(76, 2, NULL, NULL, 28, NULL),
(77, 2, NULL, NULL, 8, NULL),
(78, 3, NULL, NULL, NULL, 4),
(79, 3, NULL, NULL, NULL, 36),
(80, 3, NULL, NULL, NULL, 44),
(81, 3, NULL, NULL, NULL, 23),
(82, 3, NULL, NULL, NULL, 53),
(83, 3, NULL, NULL, NULL, 16),
(84, 3, NULL, NULL, NULL, 54),
(85, 3, NULL, NULL, NULL, 60),
(86, 3, NULL, NULL, NULL, 45),
(87, 3, NULL, NULL, NULL, 1),
(88, 3, NULL, NULL, NULL, 58),
(89, 3, NULL, NULL, NULL, 22),
(90, 3, NULL, NULL, NULL, 49),
(91, 3, NULL, NULL, NULL, 14),
(92, 3, NULL, NULL, NULL, 35),
(93, 3, NULL, NULL, NULL, 43),
(94, 3, NULL, NULL, NULL, 3),
(95, 3, NULL, NULL, NULL, 7),
(96, 3, NULL, NULL, NULL, 9),
(97, 3, NULL, NULL, NULL, 30),
(98, 3, NULL, NULL, NULL, 28),
(99, 3, NULL, NULL, NULL, 48),
(100, 3, NULL, NULL, NULL, 8),
(101, 3, NULL, NULL, NULL, 50),
(102, 3, NULL, NULL, NULL, 51),
(103, 3, NULL, NULL, NULL, 41),
(104, 3, NULL, NULL, NULL, 29),
(105, 3, NULL, NULL, NULL, 6),
(106, 3, NULL, NULL, NULL, 59),
(107, 3, NULL, NULL, NULL, 42),
(108, 3, NULL, NULL, NULL, 15),
(109, 3, NULL, NULL, NULL, 46),
(110, 3, NULL, NULL, NULL, 56),
(111, 3, NULL, NULL, NULL, 40),
(112, 3, NULL, NULL, NULL, 47),
(113, 3, NULL, NULL, NULL, 5),
(114, 3, NULL, NULL, NULL, 21),
(115, 3, NULL, NULL, NULL, 13),
(116, 3, NULL, NULL, NULL, 37),
(117, 3, NULL, NULL, NULL, 52),
(118, 3, NULL, NULL, NULL, 19),
(119, 3, NULL, NULL, NULL, 38),
(120, 3, NULL, NULL, NULL, 55),
(121, 3, NULL, NULL, NULL, 32),
(122, 3, NULL, NULL, NULL, 24),
(123, 3, NULL, NULL, NULL, 20),
(124, 3, NULL, NULL, NULL, 27),
(125, 3, NULL, NULL, NULL, 26),
(126, 3, NULL, NULL, NULL, 25),
(127, 3, NULL, NULL, NULL, 33),
(128, 3, NULL, NULL, NULL, 17),
(129, 3, NULL, NULL, NULL, 31),
(130, 3, NULL, NULL, NULL, 57),
(131, 3, NULL, NULL, NULL, 39),
(132, 3, NULL, NULL, NULL, 11),
(133, 3, NULL, NULL, NULL, 2),
(134, 3, NULL, NULL, NULL, 18),
(135, 3, NULL, NULL, NULL, 10),
(136, 3, NULL, NULL, NULL, 12),
(137, 3, NULL, NULL, NULL, 34),
(138, 4, NULL, NULL, NULL, 1),
(139, 4, NULL, NULL, NULL, 3),
(140, 4, NULL, NULL, NULL, 4),
(141, 4, NULL, NULL, NULL, 5),
(142, 4, NULL, NULL, NULL, 6),
(143, 4, NULL, NULL, NULL, 7),
(144, 4, NULL, NULL, NULL, 10),
(145, 4, NULL, NULL, NULL, 11),
(146, 4, NULL, NULL, NULL, 12),
(147, 4, NULL, NULL, NULL, 13),
(148, 4, NULL, NULL, NULL, 15),
(149, 4, NULL, NULL, NULL, 16),
(150, 4, NULL, NULL, NULL, 17),
(151, 4, NULL, NULL, NULL, 19),
(152, 4, NULL, NULL, NULL, 22),
(153, 4, NULL, NULL, NULL, 23),
(154, 4, NULL, NULL, NULL, 29),
(155, 4, NULL, NULL, NULL, 30),
(156, 4, NULL, NULL, NULL, 43),
(157, 5, NULL, NULL, NULL, 1),
(158, 5, NULL, NULL, NULL, 3),
(159, 5, NULL, NULL, NULL, 4),
(160, 5, NULL, NULL, NULL, 5),
(161, 5, NULL, NULL, NULL, 6),
(162, 5, NULL, NULL, NULL, 7),
(163, 5, NULL, NULL, NULL, 10),
(164, 5, NULL, NULL, NULL, 11),
(165, 5, NULL, NULL, NULL, 12),
(166, 5, NULL, NULL, NULL, 13),
(167, 5, NULL, NULL, NULL, 15),
(168, 5, NULL, NULL, NULL, 16),
(169, 5, NULL, NULL, NULL, 17),
(170, 5, NULL, NULL, NULL, 19),
(171, 5, NULL, NULL, NULL, 22),
(172, 5, NULL, NULL, NULL, 23),
(173, 5, NULL, NULL, NULL, 29),
(174, 5, NULL, NULL, NULL, 30),
(175, 5, NULL, NULL, NULL, 43),
(176, 6, NULL, NULL, NULL, 1),
(177, 6, NULL, NULL, NULL, 3),
(178, 6, NULL, NULL, NULL, 4),
(179, 6, NULL, NULL, NULL, 5),
(180, 6, NULL, NULL, NULL, 6),
(181, 6, NULL, NULL, NULL, 7),
(182, 6, NULL, NULL, NULL, 10),
(183, 6, NULL, NULL, NULL, 11),
(184, 6, NULL, NULL, NULL, 12),
(185, 6, NULL, NULL, NULL, 13),
(186, 6, NULL, NULL, NULL, 15),
(187, 6, NULL, NULL, NULL, 16),
(188, 6, NULL, NULL, NULL, 17),
(189, 6, NULL, NULL, NULL, 19),
(190, 6, NULL, NULL, NULL, 22),
(191, 6, NULL, NULL, NULL, 23),
(192, 6, NULL, NULL, NULL, 29),
(193, 6, NULL, NULL, NULL, 30),
(194, 6, NULL, NULL, NULL, 43)
ON CONFLICT DO NOTHING;

INSERT INTO paquete_turistico (id_paquete, nombre, slug, imagen_url, descripcion, precio, duracion_dias, duracion_noches, cupos_totales, cupos_disponibles, fecha_inicio, fecha_fin, imagen_principal, personalizable, estado, id_destino, id_guia, emoji, video_url) VALUES
(1, 'Cartagena Mágica', 'cartagena-magica', 'img/paquetes/Cartagena.jpeg', 'Descubre la ciudad amurallada con playas privadas e historia colonial.', 1850000.00, 5, 4, 20, 14, '2026-07-01', '2026-07-05', 'img/paquetes/Cartagena.jpeg', TRUE, 'activo', 1, 1, '🧳', NULL),
(2, 'Medellín Innovadora', 'medellin-innovadora', 'img/paquetes/Medellin.jpeg', 'Conoce la ciudad más transformadora de América Latina.', 1200000.00, 4, 3, 25, 20, '2026-07-10', '2026-07-13', 'img/paquetes/Medellin.jpeg', FALSE, 'activo', 2, 2, '🧳', NULL),
(3, 'Guatapé Extremo', 'guatape-extremo', 'img/paquetes/Guatape.jpeg', 'Adrenalina pura: sube la Piedra del Peñol y navega el embalse.', 890000.00, 3, 2, 15, 12, '2026-07-15', '2026-07-17', 'img/paquetes/Guatape.jpeg', TRUE, 'activo', 3, 3, '🧳', NULL),
(4, 'San Andrés Todo Incluido', 'san-andres-todo-incluido', 'img/paquetes/SanAndres.jpeg', 'El mar de los siete colores con todo incluido en resort 5 estrellas.', 3200000.00, 7, 6, 30, 18, '2026-08-01', '2026-08-07', 'img/paquetes/SanAndres.jpeg', FALSE, 'activo', 4, 1, '🧳', NULL),
(5, 'Tayrona Salvaje', 'tayrona-salvaje', 'img/paquetes/Tayrona.jpeg', 'Selva, playas vírgenes y ecosistemas únicos en el Parque Tayrona.', 1450000.00, 5, 4, 12, 8, '2026-08-10', '2026-08-14', 'img/paquetes/Tayrona.jpeg', TRUE, 'activo', 5, 2, '🧳', NULL),
(6, 'Valle del Cocora Místico', 'valle-del-cocora-mistico', 'img/paquetes/Cocora.jpeg', 'Caminata entre palmas de cera y fincas cafeteras del Quindío.', 980000.00, 3, 2, 20, 15, '2026-09-01', '2026-09-03', 'img/paquetes/Cocora.jpeg', FALSE, 'activo', 6, 3, '🧳', NULL),
(7, 'Amazonas Aventura', 'amazonas-aventura', 'img/paquetes/Amazonas.jpeg', 'Explora la selva amazónica y conoce comunidades indígenas.', 2750000.00, 6, 5, 18, 14, '2026-09-10', '2026-09-15', 'img/paquetes/Amazonas.jpeg', TRUE, 'activo', 8, 1, '🧳', NULL),
(8, 'Desierto de la Tatacoa', 'desierto-de-la-tatacoa', 'img/paquetes/Desierto.jpeg', 'Observación astronómica y recorridos por paisajes únicos.', 750000.00, 3, 2, 20, 16, '2026-09-20', '2026-09-22', 'img/paquetes/Desierto.jpeg', FALSE, 'activo', 8, 2, '🧳', NULL),
(9, 'Caño Cristales Premium', 'cano-cristales-premium', 'img/paquetes/Caño.jpeg', 'Visita el río más hermoso del mundo con guía especializado.', 2950000.00, 5, 4, 15, 10, '2026-10-01', '2026-10-05', 'img/paquetes/Caño.jpeg', TRUE, 'activo', 9, 3, '🧳', NULL),
(10, 'Eje Cafetero Tradicional', 'eje-cafetero-tradicional', 'img/paquetes/EjeCafetero.jpeg', 'Recorrido por fincas cafeteras y pueblos patrimonio.', 1350000.00, 4, 3, 25, 18, '2026-10-10', '2026-10-13', 'img/paquetes/EjeCafetero.jpeg', FALSE, 'activo', 10, 1, '🧳', NULL),
(11, 'Nuquí Ecoturismo', 'nuqui-ecoturismo', 'img/paquetes/Nuqui.jpeg', 'Avistamiento de ballenas y playas vírgenes del Pacífico.', 2400000.00, 5, 4, 16, 12, '2026-10-20', '2026-10-24', 'img/paquetes/Nuqui.jpeg', TRUE, 'activo', 11, 2, '🧳', NULL),
(12, 'Barichara Colonial', 'barichara-colonial', 'img/paquetes/Barichara.jpg', 'Conoce uno de los pueblos más bellos de Colombia.', 890000.00, 3, 2, 20, 17, '2026-11-01', '2026-11-03', 'img/paquetes/Barichara.jpg', FALSE, 'activo', 12, 3, '🧳', NULL),
(13, 'Santuario Las Lajas', 'santuario-las-lajas', 'img/paquetes/Santuario.jpeg', 'Recorrido religioso y cultural por Nariño.', 680000.00, 3, 2, 22, 19, '2026-11-08', '2026-11-10', 'img/paquetes/Santuario.jpeg', FALSE, 'activo', 13, 1, '🧳', NULL),
(14, 'Boyacá Histórica', 'boyaca-historica', 'img/paquetes/Boyaca.jpeg', 'Villa de Leyva, Ráquira y monumentos históricos.', 980000.00, 4, 3, 24, 20, '2026-11-15', '2026-11-18', 'img/paquetes/BOYaca.jpeg', TRUE, 'activo', 14, 2, '🧳', NULL),
(15, 'Cañón del Chicamocha', 'canon-del-chicamocha', 'img/paquetes/CañonChica.jpeg', 'Deportes extremos y paisajes espectaculares.', 1150000.00, 4, 3, 18, 13, '2026-11-25', '2026-11-28', 'img/paquetes/CañonChica.jpeg', TRUE, 'activo', 15, 3, '🧳', NULL),
(16, 'Mompox Patrimonial', 'mompox-patrimonial', 'img/paquetes/Mompox.jpg', 'Historia, arquitectura colonial y cultura ribereña.', 1250000.00, 4, 3, 20, 16, '2026-12-01', '2026-12-04', 'img/paquetes/Mompox.jpg', FALSE, 'activo', 16, 1, '🧳', NULL),
(17, 'Sierra Nevada Ancestral', 'sierra-nevada-ancestral', 'img/paquetes/CierraNevada.jpeg', 'Conexión con comunidades indígenas y naturaleza.', 2100000.00, 5, 4, 14, 10, '2026-12-10', '2026-12-14', 'img/paquetes/CierraNevada.jpeg', TRUE, 'activo', 17, 2, '🧳', NULL),
(18, 'Tolú y Coveñas Relax', 'tolu-y-covenas-relax', 'img/paquetes/Tolu.jpeg', 'Playas tranquilas y actividades acuáticas.', 1100000.00, 4, 3, 26, 21, '2026-12-18', '2026-12-21', 'img/paquetes/Tolu.jpeg', FALSE, 'activo', 18, 3, '🧳', NULL),
(19, 'Isla Gorgona Explorer', 'isla-gorgona-explorer', 'img/paquetes/Isla.jpeg', 'Naturaleza, senderismo y biodiversidad marina.', 2800000.00, 5, 4, 12, 8, '2027-01-10', '2027-01-14', 'img/paquetes/Isla.jpeg', TRUE, 'activo', 19, 1, '🧳', NULL),
(20, 'Capurganá Paraíso', 'capurgana-paraiso', 'img/paquetes/Capurgana.jpeg', 'Playas cristalinas y ecoturismo en el Caribe colombiano.', 1900000.00, 5, 4, 18, 13, '2027-01-20', '2027-01-24', 'img/paquetes/Capurgana.jpeg', TRUE, 'activo', 20, 2, '🧳', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO paquete_transporte (id_paquete, id_transporte) VALUES
(1, 10),
(1, 28),
(2, 11),
(2, 33),
(3, 31),
(3, 33),
(4, 7),
(4, 18),
(5, 3),
(5, 37),
(6, 4),
(6, 22),
(7, 9),
(7, 17),
(8, 20),
(8, 29),
(9, 12),
(9, 35),
(10, 4),
(10, 24),
(11, 5),
(11, 36),
(12, 16),
(12, 32),
(13, 8),
(13, 23),
(14, 26),
(14, 27),
(15, 13),
(15, 34),
(16, 14),
(16, 25),
(17, 3),
(17, 15),
(18, 6),
(18, 30),
(19, 1),
(19, 19),
(20, 2),
(20, 21)
ON CONFLICT DO NOTHING;

INSERT INTO paquete_alojamiento (id_paquete, id_alojamiento) VALUES
(1, 36),
(1, 39),
(2, 18),
(2, 20),
(3, 4),
(3, 11),
(4, 1),
(4, 31),
(5, 2),
(5, 12),
(6, 10),
(6, 34),
(7, 15),
(7, 21),
(8, 8),
(8, 32),
(9, 19),
(9, 24),
(10, 27),
(10, 35),
(11, 17),
(11, 26),
(12, 5),
(12, 33),
(13, 9),
(13, 40),
(14, 7),
(14, 25),
(15, 16),
(15, 28),
(16, 22),
(16, 29),
(17, 13),
(17, 23),
(18, 3),
(18, 37),
(19, 6),
(19, 14),
(20, 30),
(20, 38)
ON CONFLICT DO NOTHING;

INSERT INTO paquete_alimentacion (id_paquete, id_alimentacion) VALUES
(1, 21),
(1, 27),
(1, 5),
(2, 26),
(2, 52),
(2, 48),
(3, 54),
(3, 37),
(3, 13),
(4, 55),
(4, 53),
(4, 41),
(5, 58),
(5, 39),
(5, 18),
(6, 47),
(6, 32),
(6, 20),
(7, 42),
(7, 38),
(7, 44),
(8, 59),
(8, 51),
(8, 60),
(9, 23),
(9, 45),
(9, 24),
(10, 16),
(10, 9),
(10, 7),
(11, 14),
(11, 10),
(11, 1),
(12, 28),
(12, 56),
(12, 4),
(13, 17),
(13, 40),
(13, 12),
(14, 8),
(14, 49),
(14, 19),
(15, 35),
(15, 57),
(15, 50),
(16, 33),
(16, 6),
(16, 15),
(17, 25),
(17, 22),
(17, 30),
(18, 11),
(18, 2),
(18, 46),
(19, 43),
(19, 36),
(19, 34),
(20, 29),
(20, 31),
(20, 3)
ON CONFLICT DO NOTHING;

INSERT INTO paquete_actividad (id_paquete, id_actividad) VALUES
(1, 38),
(1, 10),
(1, 54),
(2, 31),
(2, 23),
(2, 47),
(3, 6),
(3, 27),
(3, 14),
(4, 55),
(4, 16),
(4, 57),
(5, 5),
(5, 45),
(5, 35),
(6, 41),
(6, 39),
(6, 13),
(7, 58),
(7, 40),
(7, 3),
(9, 28),
(9, 22),
(9, 25),
(10, 9),
(10, 20),
(10, 1),
(11, 36),
(11, 49),
(11, 30),
(12, 52),
(12, 17),
(12, 56),
(13, 18),
(13, 24),
(13, 7),
(14, 44),
(14, 43),
(14, 59),
(15, 51),
(15, 11),
(15, 42),
(16, 50),
(16, 15),
(16, 26),
(17, 53),
(17, 29),
(17, 37),
(18, 4),
(18, 48),
(18, 21),
(19, 12),
(19, 60),
(19, 32),
(20, 19),
(20, 46),
(20, 33)
ON CONFLICT DO NOTHING;

INSERT INTO servicio_extra (id_servicio_extra, nombre, precio, descripcion, estado, id_paquete) VALUES
(1, 'Snorkel en Islas del Rosario', 180000.00, 'Equipo incluido, 3 horas', TRUE, 1),
(2, 'Foto profesional en la Muralla', 120000.00, 'Sesión de 1 hora con fotógrafo', TRUE, 1),
(3, 'Kayak en el embalse', 95000.00, 'Kayak doble 2 horas', TRUE, 3),
(4, 'Rappel en La Piedra', 140000.00, 'Equipo y seguro de escalada', TRUE, 3),
(5, 'Buceo certificado', 350000.00, 'Bautismo de buceo 2 inmersiones', TRUE, 5),
(6, 'Senderismo nocturno', 120000.00, 'Guía nocturno 4 horas', TRUE, 5)
ON CONFLICT DO NOTHING;

INSERT INTO promocion (id_promocion, codigo, descuento, descripcion, fecha_inicio, fecha_fin, tipo_promocion, id_paquete) VALUES
(1, 'VERANO10', 10.00, '10% de descuento temporada de verano', '2026-06-01', '2026-07-31', 'temporal', 1),
(2, 'PAREJA20', 20.00, '20% para parejas en San Andrés', '2026-07-01', '2026-08-31', 'especial', 4),
(3, 'MOCHILA15', 15.00, '15% para viajeros aventureros', '2026-07-01', '2026-09-30', 'temporal', 5)
ON CONFLICT DO NOTHING;

INSERT INTO salida_paquete (id_salida, id_paquete, fecha_salida, fecha_regreso, cupos_totales, cupos_disponibles, estado, id_guia, observaciones, fecha_creacion) VALUES
(1, 1, '2026-07-01', '2026-07-05', 20, 14, 'cerrada', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(2, 2, '2026-07-10', '2026-07-13', 25, 20, 'cerrada', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(3, 3, '2026-07-15', '2026-07-17', 15, 12, 'cerrada', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(4, 4, '2026-08-01', '2026-08-07', 30, 18, 'cerrada', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(5, 5, '2026-08-10', '2026-08-14', 12, 8, 'cerrada', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(6, 6, '2026-09-01', '2026-09-03', 20, 15, 'cerrada', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(7, 7, '2026-09-10', '2026-09-15', 18, 14, 'cerrada', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(8, 8, '2026-09-20', '2026-09-22', 20, 16, 'disponible', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(9, 9, '2026-10-01', '2026-10-05', 15, 10, 'disponible', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(10, 10, '2026-10-10', '2026-10-13', 25, 18, 'disponible', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(11, 11, '2026-10-20', '2026-10-24', 16, 12, 'disponible', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(12, 12, '2026-11-01', '2026-11-03', 20, 17, 'disponible', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(13, 13, '2026-11-08', '2026-11-10', 22, 19, 'disponible', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(14, 14, '2026-11-15', '2026-11-18', 24, 20, 'disponible', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(15, 15, '2026-11-25', '2026-11-28', 18, 13, 'disponible', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(16, 16, '2026-12-01', '2026-12-04', 20, 16, 'disponible', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(17, 17, '2026-12-10', '2026-12-14', 14, 10, 'disponible', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(18, 18, '2026-12-18', '2026-12-21', 26, 21, 'disponible', 3, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(19, 19, '2027-01-10', '2027-01-14', 12, 8, 'disponible', 1, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(20, 20, '2027-01-20', '2027-01-24', 18, 13, 'disponible', 2, 'Salida inicial generada desde la programación original del paquete.', '2026-09-20 11:59:28.668981'),
(21, 1, '2026-09-05', '2026-09-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(22, 1, '2026-09-12', '2026-09-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(23, 1, '2026-09-19', '2026-09-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(24, 1, '2026-09-26', '2026-09-30', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(25, 2, '2026-09-05', '2026-09-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(26, 2, '2026-09-12', '2026-09-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(27, 2, '2026-09-19', '2026-09-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(28, 2, '2026-09-26', '2026-09-29', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(29, 3, '2026-09-05', '2026-09-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(30, 3, '2026-09-12', '2026-09-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(31, 3, '2026-09-19', '2026-09-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(32, 3, '2026-09-26', '2026-09-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(33, 4, '2026-09-05', '2026-09-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(34, 4, '2026-09-12', '2026-09-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(35, 4, '2026-09-19', '2026-09-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(36, 4, '2026-09-26', '2026-10-02', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(37, 5, '2026-09-05', '2026-09-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(38, 5, '2026-09-12', '2026-09-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(39, 5, '2026-09-19', '2026-09-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(40, 5, '2026-09-26', '2026-09-30', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(41, 6, '2026-09-05', '2026-09-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(42, 6, '2026-09-12', '2026-09-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(43, 6, '2026-09-19', '2026-09-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(44, 6, '2026-09-26', '2026-09-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(45, 7, '2026-09-05', '2026-09-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(46, 7, '2026-09-12', '2026-09-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(47, 7, '2026-09-19', '2026-09-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(48, 7, '2026-09-26', '2026-10-01', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(49, 8, '2026-09-05', '2026-09-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(50, 8, '2026-09-12', '2026-09-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(51, 8, '2026-09-19', '2026-09-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(52, 8, '2026-09-26', '2026-09-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(53, 9, '2026-09-05', '2026-09-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(54, 9, '2026-09-12', '2026-09-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(55, 9, '2026-09-19', '2026-09-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(56, 9, '2026-09-26', '2026-09-30', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(57, 10, '2026-09-05', '2026-09-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(58, 10, '2026-09-12', '2026-09-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(59, 10, '2026-09-19', '2026-09-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(60, 10, '2026-09-26', '2026-09-29', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(61, 11, '2026-09-05', '2026-09-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(62, 11, '2026-09-12', '2026-09-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(63, 11, '2026-09-19', '2026-09-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(64, 11, '2026-09-26', '2026-09-30', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(65, 12, '2026-09-05', '2026-09-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(66, 12, '2026-09-12', '2026-09-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(67, 12, '2026-09-19', '2026-09-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(68, 12, '2026-09-26', '2026-09-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(69, 13, '2026-09-05', '2026-09-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(70, 13, '2026-09-12', '2026-09-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(71, 13, '2026-09-19', '2026-09-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(72, 13, '2026-09-26', '2026-09-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(73, 14, '2026-09-05', '2026-09-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(74, 14, '2026-09-12', '2026-09-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(75, 14, '2026-09-19', '2026-09-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(76, 14, '2026-09-26', '2026-09-29', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(77, 15, '2026-09-05', '2026-09-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(78, 15, '2026-09-12', '2026-09-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(79, 15, '2026-09-19', '2026-09-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(80, 15, '2026-09-26', '2026-09-29', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(81, 16, '2026-09-05', '2026-09-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(82, 16, '2026-09-12', '2026-09-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(83, 16, '2026-09-19', '2026-09-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(84, 16, '2026-09-26', '2026-09-29', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(85, 17, '2026-09-05', '2026-09-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(86, 17, '2026-09-12', '2026-09-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(87, 17, '2026-09-19', '2026-09-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(88, 17, '2026-09-26', '2026-09-30', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(89, 18, '2026-09-05', '2026-09-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(90, 18, '2026-09-12', '2026-09-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(91, 18, '2026-09-19', '2026-09-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(92, 18, '2026-09-26', '2026-09-29', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(93, 19, '2026-09-05', '2026-09-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(94, 19, '2026-09-12', '2026-09-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(95, 19, '2026-09-19', '2026-09-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(96, 19, '2026-09-26', '2026-09-30', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(97, 20, '2026-09-05', '2026-09-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(98, 20, '2026-09-12', '2026-09-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(99, 20, '2026-09-19', '2026-09-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(100, 20, '2026-09-26', '2026-09-30', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(101, 1, '2026-10-05', '2026-10-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(102, 1, '2026-10-12', '2026-10-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(103, 1, '2026-10-19', '2026-10-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(104, 1, '2026-10-26', '2026-10-30', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(105, 2, '2026-10-05', '2026-10-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(106, 2, '2026-10-12', '2026-10-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(107, 2, '2026-10-19', '2026-10-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(108, 2, '2026-10-26', '2026-10-29', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(109, 3, '2026-10-05', '2026-10-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(110, 3, '2026-10-12', '2026-10-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(111, 3, '2026-10-19', '2026-10-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(112, 3, '2026-10-26', '2026-10-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(113, 4, '2026-10-05', '2026-10-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(114, 4, '2026-10-12', '2026-10-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(115, 4, '2026-10-19', '2026-10-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(116, 4, '2026-10-26', '2026-11-01', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(117, 5, '2026-10-05', '2026-10-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(118, 5, '2026-10-12', '2026-10-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(119, 5, '2026-10-19', '2026-10-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(120, 5, '2026-10-26', '2026-10-30', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(121, 6, '2026-10-05', '2026-10-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(122, 6, '2026-10-12', '2026-10-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(123, 6, '2026-10-19', '2026-10-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(124, 6, '2026-10-26', '2026-10-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(125, 7, '2026-10-05', '2026-10-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(126, 7, '2026-10-12', '2026-10-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(127, 7, '2026-10-19', '2026-10-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(128, 7, '2026-10-26', '2026-10-31', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(129, 8, '2026-10-05', '2026-10-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(130, 8, '2026-10-12', '2026-10-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(131, 8, '2026-10-19', '2026-10-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(132, 8, '2026-10-26', '2026-10-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(133, 9, '2026-10-05', '2026-10-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(134, 9, '2026-10-12', '2026-10-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(135, 9, '2026-10-19', '2026-10-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(136, 9, '2026-10-26', '2026-10-30', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(137, 10, '2026-10-05', '2026-10-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(138, 10, '2026-10-12', '2026-10-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(139, 10, '2026-10-19', '2026-10-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(140, 10, '2026-10-26', '2026-10-29', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(141, 11, '2026-10-05', '2026-10-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(142, 11, '2026-10-12', '2026-10-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(143, 11, '2026-10-19', '2026-10-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(144, 11, '2026-10-26', '2026-10-30', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(145, 12, '2026-10-05', '2026-10-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(146, 12, '2026-10-12', '2026-10-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(147, 12, '2026-10-19', '2026-10-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(148, 12, '2026-10-26', '2026-10-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(149, 13, '2026-10-05', '2026-10-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(150, 13, '2026-10-12', '2026-10-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(151, 13, '2026-10-19', '2026-10-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(152, 13, '2026-10-26', '2026-10-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(153, 14, '2026-10-05', '2026-10-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(154, 14, '2026-10-12', '2026-10-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(155, 14, '2026-10-19', '2026-10-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(156, 14, '2026-10-26', '2026-10-29', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(157, 15, '2026-10-05', '2026-10-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(158, 15, '2026-10-12', '2026-10-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(159, 15, '2026-10-19', '2026-10-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(160, 15, '2026-10-26', '2026-10-29', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(161, 16, '2026-10-05', '2026-10-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(162, 16, '2026-10-12', '2026-10-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(163, 16, '2026-10-19', '2026-10-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(164, 16, '2026-10-26', '2026-10-29', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(165, 17, '2026-10-05', '2026-10-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(166, 17, '2026-10-12', '2026-10-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(167, 17, '2026-10-19', '2026-10-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(168, 17, '2026-10-26', '2026-10-30', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(169, 18, '2026-10-05', '2026-10-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(170, 18, '2026-10-12', '2026-10-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(171, 18, '2026-10-19', '2026-10-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(172, 18, '2026-10-26', '2026-10-29', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(173, 19, '2026-10-05', '2026-10-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(174, 19, '2026-10-12', '2026-10-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(175, 19, '2026-10-19', '2026-10-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(176, 19, '2026-10-26', '2026-10-30', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(177, 20, '2026-10-05', '2026-10-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(178, 20, '2026-10-12', '2026-10-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(179, 20, '2026-10-19', '2026-10-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(180, 20, '2026-10-26', '2026-10-30', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(181, 1, '2026-11-05', '2026-11-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(182, 1, '2026-11-12', '2026-11-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(183, 1, '2026-11-19', '2026-11-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(184, 1, '2026-11-26', '2026-11-30', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(185, 2, '2026-11-05', '2026-11-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(186, 2, '2026-11-12', '2026-11-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(187, 2, '2026-11-19', '2026-11-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(188, 2, '2026-11-26', '2026-11-29', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(189, 3, '2026-11-05', '2026-11-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(190, 3, '2026-11-12', '2026-11-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(191, 3, '2026-11-19', '2026-11-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(192, 3, '2026-11-26', '2026-11-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(193, 4, '2026-11-05', '2026-11-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(194, 4, '2026-11-12', '2026-11-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(195, 4, '2026-11-19', '2026-11-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(196, 4, '2026-11-26', '2026-12-02', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(197, 5, '2026-11-05', '2026-11-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(198, 5, '2026-11-12', '2026-11-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(199, 5, '2026-11-19', '2026-11-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(200, 5, '2026-11-26', '2026-11-30', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(201, 6, '2026-11-05', '2026-11-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(202, 6, '2026-11-12', '2026-11-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(203, 6, '2026-11-19', '2026-11-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(204, 6, '2026-11-26', '2026-11-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(205, 7, '2026-11-05', '2026-11-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(206, 7, '2026-11-12', '2026-11-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(207, 7, '2026-11-19', '2026-11-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(208, 7, '2026-11-26', '2026-12-01', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(209, 8, '2026-11-05', '2026-11-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(210, 8, '2026-11-12', '2026-11-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(211, 8, '2026-11-19', '2026-11-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(212, 8, '2026-11-26', '2026-11-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(213, 9, '2026-11-05', '2026-11-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(214, 9, '2026-11-12', '2026-11-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(215, 9, '2026-11-19', '2026-11-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(216, 9, '2026-11-26', '2026-11-30', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(217, 10, '2026-11-05', '2026-11-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(218, 10, '2026-11-12', '2026-11-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(219, 10, '2026-11-19', '2026-11-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(220, 10, '2026-11-26', '2026-11-29', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(221, 11, '2026-11-05', '2026-11-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(222, 11, '2026-11-12', '2026-11-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(223, 11, '2026-11-19', '2026-11-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(224, 11, '2026-11-26', '2026-11-30', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(225, 12, '2026-11-05', '2026-11-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(226, 12, '2026-11-12', '2026-11-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(227, 12, '2026-11-19', '2026-11-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(228, 12, '2026-11-26', '2026-11-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(229, 13, '2026-11-05', '2026-11-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(230, 13, '2026-11-12', '2026-11-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(231, 13, '2026-11-19', '2026-11-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(232, 13, '2026-11-26', '2026-11-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(233, 14, '2026-11-05', '2026-11-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(234, 14, '2026-11-12', '2026-11-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(235, 14, '2026-11-19', '2026-11-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(236, 14, '2026-11-26', '2026-11-29', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(237, 15, '2026-11-05', '2026-11-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(238, 15, '2026-11-12', '2026-11-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(239, 15, '2026-11-19', '2026-11-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(240, 15, '2026-11-26', '2026-11-29', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(241, 16, '2026-11-05', '2026-11-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(242, 16, '2026-11-12', '2026-11-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(243, 16, '2026-11-19', '2026-11-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(244, 16, '2026-11-26', '2026-11-29', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(245, 17, '2026-11-05', '2026-11-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(246, 17, '2026-11-12', '2026-11-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(247, 17, '2026-11-19', '2026-11-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(248, 17, '2026-11-26', '2026-11-30', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(249, 18, '2026-11-05', '2026-11-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(250, 18, '2026-11-12', '2026-11-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(251, 18, '2026-11-19', '2026-11-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(252, 18, '2026-11-26', '2026-11-29', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(253, 19, '2026-11-05', '2026-11-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(254, 19, '2026-11-12', '2026-11-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(255, 19, '2026-11-19', '2026-11-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(256, 19, '2026-11-26', '2026-11-30', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(257, 20, '2026-11-05', '2026-11-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(258, 20, '2026-11-12', '2026-11-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(259, 20, '2026-11-19', '2026-11-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(260, 20, '2026-11-26', '2026-11-30', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(261, 1, '2026-12-05', '2026-12-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(262, 1, '2026-12-12', '2026-12-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(263, 1, '2026-12-19', '2026-12-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(264, 1, '2026-12-26', '2026-12-30', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(265, 2, '2026-12-05', '2026-12-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(266, 2, '2026-12-12', '2026-12-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(267, 2, '2026-12-19', '2026-12-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(268, 2, '2026-12-26', '2026-12-29', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(269, 3, '2026-12-05', '2026-12-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(270, 3, '2026-12-12', '2026-12-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(271, 3, '2026-12-19', '2026-12-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(272, 3, '2026-12-26', '2026-12-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(273, 4, '2026-12-05', '2026-12-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(274, 4, '2026-12-12', '2026-12-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(275, 4, '2026-12-19', '2026-12-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(276, 4, '2026-12-26', '2027-01-01', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(277, 5, '2026-12-05', '2026-12-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(278, 5, '2026-12-12', '2026-12-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(279, 5, '2026-12-19', '2026-12-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(280, 5, '2026-12-26', '2026-12-30', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(281, 6, '2026-12-05', '2026-12-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(282, 6, '2026-12-12', '2026-12-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(283, 6, '2026-12-19', '2026-12-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(284, 6, '2026-12-26', '2026-12-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(285, 7, '2026-12-05', '2026-12-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(286, 7, '2026-12-12', '2026-12-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(287, 7, '2026-12-19', '2026-12-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(288, 7, '2026-12-26', '2026-12-31', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(289, 8, '2026-12-05', '2026-12-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(290, 8, '2026-12-12', '2026-12-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(291, 8, '2026-12-19', '2026-12-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(292, 8, '2026-12-26', '2026-12-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(293, 9, '2026-12-05', '2026-12-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(294, 9, '2026-12-12', '2026-12-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(295, 9, '2026-12-19', '2026-12-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(296, 9, '2026-12-26', '2026-12-30', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(297, 10, '2026-12-05', '2026-12-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(298, 10, '2026-12-12', '2026-12-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(299, 10, '2026-12-19', '2026-12-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(300, 10, '2026-12-26', '2026-12-29', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(301, 11, '2026-12-05', '2026-12-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(302, 11, '2026-12-12', '2026-12-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(303, 11, '2026-12-19', '2026-12-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(304, 11, '2026-12-26', '2026-12-30', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(305, 12, '2026-12-05', '2026-12-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(306, 12, '2026-12-12', '2026-12-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(307, 12, '2026-12-19', '2026-12-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(308, 12, '2026-12-26', '2026-12-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(309, 13, '2026-12-05', '2026-12-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(310, 13, '2026-12-12', '2026-12-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(311, 13, '2026-12-19', '2026-12-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(312, 13, '2026-12-26', '2026-12-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(313, 14, '2026-12-05', '2026-12-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(314, 14, '2026-12-12', '2026-12-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(315, 14, '2026-12-19', '2026-12-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(316, 14, '2026-12-26', '2026-12-29', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(317, 15, '2026-12-05', '2026-12-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(318, 15, '2026-12-12', '2026-12-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(319, 15, '2026-12-19', '2026-12-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(320, 15, '2026-12-26', '2026-12-29', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(321, 16, '2026-12-05', '2026-12-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(322, 16, '2026-12-12', '2026-12-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(323, 16, '2026-12-19', '2026-12-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(324, 16, '2026-12-26', '2026-12-29', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(325, 17, '2026-12-05', '2026-12-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(326, 17, '2026-12-12', '2026-12-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(327, 17, '2026-12-19', '2026-12-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(328, 17, '2026-12-26', '2026-12-30', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(329, 18, '2026-12-05', '2026-12-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(330, 18, '2026-12-12', '2026-12-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(331, 18, '2026-12-19', '2026-12-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(332, 18, '2026-12-26', '2026-12-29', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(333, 19, '2026-12-05', '2026-12-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(334, 19, '2026-12-12', '2026-12-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(335, 19, '2026-12-19', '2026-12-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(336, 19, '2026-12-26', '2026-12-30', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(337, 20, '2026-12-05', '2026-12-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(338, 20, '2026-12-12', '2026-12-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(339, 20, '2026-12-19', '2026-12-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(340, 20, '2026-12-26', '2026-12-30', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(341, 1, '2027-01-05', '2027-01-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(342, 1, '2027-01-12', '2027-01-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(343, 1, '2027-01-19', '2027-01-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(344, 1, '2027-01-26', '2027-01-30', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(345, 2, '2027-01-05', '2027-01-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(346, 2, '2027-01-12', '2027-01-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(347, 2, '2027-01-19', '2027-01-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(348, 2, '2027-01-26', '2027-01-29', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(349, 3, '2027-01-05', '2027-01-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(350, 3, '2027-01-12', '2027-01-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(351, 3, '2027-01-19', '2027-01-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(352, 3, '2027-01-26', '2027-01-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(353, 4, '2027-01-05', '2027-01-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(354, 4, '2027-01-12', '2027-01-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(355, 4, '2027-01-19', '2027-01-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(356, 4, '2027-01-26', '2027-02-01', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(357, 5, '2027-01-05', '2027-01-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(358, 5, '2027-01-12', '2027-01-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(359, 5, '2027-01-19', '2027-01-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(360, 5, '2027-01-26', '2027-01-30', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(361, 6, '2027-01-05', '2027-01-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(362, 6, '2027-01-12', '2027-01-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(363, 6, '2027-01-19', '2027-01-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(364, 6, '2027-01-26', '2027-01-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(365, 7, '2027-01-05', '2027-01-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(366, 7, '2027-01-12', '2027-01-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(367, 7, '2027-01-19', '2027-01-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(368, 7, '2027-01-26', '2027-01-31', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(369, 8, '2027-01-05', '2027-01-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(370, 8, '2027-01-12', '2027-01-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(371, 8, '2027-01-19', '2027-01-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(372, 8, '2027-01-26', '2027-01-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(373, 9, '2027-01-05', '2027-01-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(374, 9, '2027-01-12', '2027-01-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(375, 9, '2027-01-19', '2027-01-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(376, 9, '2027-01-26', '2027-01-30', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(377, 10, '2027-01-05', '2027-01-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(378, 10, '2027-01-12', '2027-01-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(379, 10, '2027-01-19', '2027-01-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(380, 10, '2027-01-26', '2027-01-29', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(381, 11, '2027-01-05', '2027-01-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(382, 11, '2027-01-12', '2027-01-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(383, 11, '2027-01-19', '2027-01-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(384, 11, '2027-01-26', '2027-01-30', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(385, 12, '2027-01-05', '2027-01-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(386, 12, '2027-01-12', '2027-01-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(387, 12, '2027-01-19', '2027-01-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(388, 12, '2027-01-26', '2027-01-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(389, 13, '2027-01-05', '2027-01-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(390, 13, '2027-01-12', '2027-01-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(391, 13, '2027-01-19', '2027-01-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(392, 13, '2027-01-26', '2027-01-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(393, 14, '2027-01-05', '2027-01-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(394, 14, '2027-01-12', '2027-01-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(395, 14, '2027-01-19', '2027-01-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(396, 14, '2027-01-26', '2027-01-29', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(397, 15, '2027-01-05', '2027-01-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(398, 15, '2027-01-12', '2027-01-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(399, 15, '2027-01-19', '2027-01-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(400, 15, '2027-01-26', '2027-01-29', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(401, 16, '2027-01-05', '2027-01-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(402, 16, '2027-01-12', '2027-01-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(403, 16, '2027-01-19', '2027-01-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(404, 16, '2027-01-26', '2027-01-29', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(405, 17, '2027-01-05', '2027-01-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(406, 17, '2027-01-12', '2027-01-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(407, 17, '2027-01-19', '2027-01-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(408, 17, '2027-01-26', '2027-01-30', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(409, 18, '2027-01-05', '2027-01-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(410, 18, '2027-01-12', '2027-01-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(411, 18, '2027-01-19', '2027-01-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(412, 18, '2027-01-26', '2027-01-29', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(413, 19, '2027-01-05', '2027-01-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(414, 19, '2027-01-12', '2027-01-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(415, 19, '2027-01-19', '2027-01-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(416, 19, '2027-01-26', '2027-01-30', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(417, 20, '2027-01-05', '2027-01-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(418, 20, '2027-01-12', '2027-01-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(419, 20, '2027-01-19', '2027-01-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(420, 20, '2027-01-26', '2027-01-30', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(421, 1, '2027-02-05', '2027-02-09', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(422, 1, '2027-02-12', '2027-02-16', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(423, 1, '2027-02-19', '2027-02-23', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(424, 1, '2027-02-26', '2027-03-02', 20, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(425, 2, '2027-02-05', '2027-02-08', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(426, 2, '2027-02-12', '2027-02-15', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(427, 2, '2027-02-19', '2027-02-22', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(428, 2, '2027-02-26', '2027-03-01', 25, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(429, 3, '2027-02-05', '2027-02-07', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(430, 3, '2027-02-12', '2027-02-14', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(431, 3, '2027-02-19', '2027-02-21', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(432, 3, '2027-02-26', '2027-02-28', 15, 12, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(433, 4, '2027-02-05', '2027-02-11', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(434, 4, '2027-02-12', '2027-02-18', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(435, 4, '2027-02-19', '2027-02-25', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(436, 4, '2027-02-26', '2027-03-04', 30, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(437, 5, '2027-02-05', '2027-02-09', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(438, 5, '2027-02-12', '2027-02-16', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(439, 5, '2027-02-19', '2027-02-23', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(440, 5, '2027-02-26', '2027-03-02', 12, 8, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(441, 6, '2027-02-05', '2027-02-07', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(442, 6, '2027-02-12', '2027-02-14', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(443, 6, '2027-02-19', '2027-02-21', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(444, 6, '2027-02-26', '2027-02-28', 20, 15, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(445, 7, '2027-02-05', '2027-02-10', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(446, 7, '2027-02-12', '2027-02-17', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(447, 7, '2027-02-19', '2027-02-24', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(448, 7, '2027-02-26', '2027-03-03', 18, 14, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(449, 8, '2027-02-05', '2027-02-07', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(450, 8, '2027-02-12', '2027-02-14', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(451, 8, '2027-02-19', '2027-02-21', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(452, 8, '2027-02-26', '2027-02-28', 20, 16, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(453, 9, '2027-02-05', '2027-02-09', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(454, 9, '2027-02-12', '2027-02-16', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(455, 9, '2027-02-19', '2027-02-23', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(456, 9, '2027-02-26', '2027-03-02', 15, 10, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(457, 10, '2027-02-05', '2027-02-08', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(458, 10, '2027-02-12', '2027-02-15', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(459, 10, '2027-02-19', '2027-02-22', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(460, 10, '2027-02-26', '2027-03-01', 25, 18, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(461, 11, '2027-02-05', '2027-02-09', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(462, 11, '2027-02-12', '2027-02-16', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(463, 11, '2027-02-19', '2027-02-23', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(464, 11, '2027-02-26', '2027-03-02', 16, 12, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(465, 12, '2027-02-05', '2027-02-07', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(466, 12, '2027-02-12', '2027-02-14', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(467, 12, '2027-02-19', '2027-02-21', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(468, 12, '2027-02-26', '2027-02-28', 20, 17, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(469, 13, '2027-02-05', '2027-02-07', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(470, 13, '2027-02-12', '2027-02-14', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(471, 13, '2027-02-19', '2027-02-21', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(472, 13, '2027-02-26', '2027-02-28', 22, 19, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(473, 14, '2027-02-05', '2027-02-08', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(474, 14, '2027-02-12', '2027-02-15', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(475, 14, '2027-02-19', '2027-02-22', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(476, 14, '2027-02-26', '2027-03-01', 24, 20, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(477, 15, '2027-02-05', '2027-02-08', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(478, 15, '2027-02-12', '2027-02-15', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(479, 15, '2027-02-19', '2027-02-22', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(480, 15, '2027-02-26', '2027-03-01', 18, 13, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(481, 16, '2027-02-05', '2027-02-08', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(482, 16, '2027-02-12', '2027-02-15', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(483, 16, '2027-02-19', '2027-02-22', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(484, 16, '2027-02-26', '2027-03-01', 20, 16, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(485, 17, '2027-02-05', '2027-02-09', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(486, 17, '2027-02-12', '2027-02-16', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(487, 17, '2027-02-19', '2027-02-23', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(488, 17, '2027-02-26', '2027-03-02', 14, 10, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(489, 18, '2027-02-05', '2027-02-08', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(490, 18, '2027-02-12', '2027-02-15', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(491, 18, '2027-02-19', '2027-02-22', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(492, 18, '2027-02-26', '2027-03-01', 26, 21, 'programada', 3, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(493, 19, '2027-02-05', '2027-02-09', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(494, 19, '2027-02-12', '2027-02-16', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(495, 19, '2027-02-19', '2027-02-23', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(496, 19, '2027-02-26', '2027-03-02', 12, 8, 'programada', 1, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(497, 20, '2027-02-05', '2027-02-09', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(498, 20, '2027-02-12', '2027-02-16', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(499, 20, '2027-02-19', '2027-02-23', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981'),
(500, 20, '2027-02-26', '2027-03-02', 18, 13, 'programada', 2, 'Salida programada automáticamente para dar varias opciones de fecha.', '2026-09-20 11:59:28.668981')
ON CONFLICT DO NOTHING;

INSERT INTO reserva (id_reserva, codigo_unico, fecha_reserva, fecha_viaje, estado, valor_referencial, cant_adultos, cant_menores, observaciones, acepta_no_reembolso, metodo_contacto, guia_pdf, id_cliente, id_paquete, precio_total, plan, alergias, mascotas, id_salida, reembolso_estado, motivo_cancelacion, reembolso_fecha, encuesta_enviada, encuesta_enviada_fecha) VALUES
(17, 'MRV-ENCUESTA-DEMO', '2026-11-25', '2026-11-23', 'completada', NULL, 1, 0, NULL, TRUE, NULL, NULL, 11, 1, NULL, NULL, NULL, FALSE, NULL, NULL, NULL, NULL, TRUE, '2026-11-25 21:19:40.393995')
ON CONFLICT DO NOTHING;

INSERT INTO encuesta_pregunta (id_pregunta, texto, tipo_respuesta, orden, estado) VALUES
(1, '¿Cómo calificarías la calidad general del paquete?', 'calificacion', 1, TRUE),
(2, '¿Qué tan satisfecho estás con el servicio del proveedor?', 'calificacion', 2, TRUE),
(3, '¿El proceso de reserva en MAREVA fue fácil y claro?', 'calificacion', 3, TRUE),
(4, '¿Recomendarías MAREVA a un amigo o familiar?', 'calificacion', 4, TRUE),
(5, 'Cuéntanos qué fue lo mejor de tu experiencia:', 'texto', 5, TRUE),
(6, '¿Qué podríamos mejorar?', 'texto', 6, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO resena_paquete (id_resena, id_paquete, id_cliente, id_reserva, calificacion, calificacion_servicio, titulo, comentario, fecha_resena, estado, origen) VALUES
(4, 17, 1, NULL, 5, 5, 'Excelente recorrido', 'Guía atento, paisajes increíbles y muy buena organización.', '2026-10-08 20:56:35.899269', 'visible', 'semilla'),
(5, 9, 1, NULL, 5, 5, 'Excelente recorrido', 'Guía atento, paisajes increíbles y muy buena organización.', '2026-11-01 20:56:35.899269', 'visible', 'semilla'),
(6, 1, 1, NULL, 5, 5, 'Excelente recorrido', 'Guía atento, paisajes increíbles y muy buena organización.', '2026-11-25 20:56:35.899269', 'visible', 'semilla'),
(7, 18, 2, NULL, 4, 5, 'Muy buena experiencia', 'Todo funcionó según lo previsto; repetiría sin dudarlo.', '2026-10-05 20:56:35.899269', 'visible', 'semilla'),
(8, 10, 2, NULL, 4, 5, 'Muy buena experiencia', 'Todo funcionó según lo previsto; repetiría sin dudarlo.', '2026-10-29 20:56:35.899269', 'visible', 'semilla'),
(9, 2, 2, NULL, 4, 5, 'Muy buena experiencia', 'Todo funcionó según lo previsto; repetiría sin dudarlo.', '2026-11-22 20:56:35.899269', 'visible', 'semilla'),
(10, 19, 3, NULL, 3, 4, 'Buena pero mejorable', 'El alojamiento cumplió; las comidas podrían mejorar.', '2026-10-02 20:56:35.899269', 'visible', 'semilla'),
(11, 11, 3, NULL, 3, 4, 'Buena pero mejorable', 'El alojamiento cumplió; las comidas podrían mejorar.', '2026-10-26 20:56:35.899269', 'visible', 'semilla'),
(12, 3, 3, NULL, 3, 4, 'Buena pero mejorable', 'El alojamiento cumplió; las comidas podrían mejorar.', '2026-11-19 20:56:35.899269', 'visible', 'semilla'),
(13, 20, 4, NULL, 2, 3, 'No cumplió expectativas', 'Hubo demasiada espera en el transporte.', '2026-09-29 20:56:35.899269', 'visible', 'semilla'),
(14, 12, 4, NULL, 2, 3, 'No cumplió expectativas', 'Hubo demasiada espera en el transporte.', '2026-10-23 20:56:35.899269', 'visible', 'semilla'),
(15, 4, 4, NULL, 2, 3, 'No cumplió expectativas', 'Hubo demasiada espera en el transporte.', '2026-11-16 20:56:35.899269', 'visible', 'semilla'),
(16, 13, 5, NULL, 5, 4, 'Inolvidable', 'Las actividades fueron excelentes y el equipo muy amable.', '2026-10-20 20:56:35.899269', 'visible', 'semilla'),
(17, 5, 5, NULL, 5, 4, 'Inolvidable', 'Las actividades fueron excelentes y el equipo muy amable.', '2026-11-13 20:56:35.899269', 'visible', 'semilla'),
(18, 14, 6, NULL, 1, 2, 'No lo recomiendo', 'Cancelaron una actividad sin avisar y hubo poca información.', '2026-10-17 20:56:35.899269', 'visible', 'semilla'),
(19, 6, 6, NULL, 1, 2, 'No lo recomiendo', 'Cancelaron una actividad sin avisar y hubo poca información.', '2026-11-10 20:56:35.899269', 'visible', 'semilla'),
(20, 15, 11, NULL, 4, 4, 'Muy recomendable', 'Buena relación precio/calidad, con detalles muy cuidados.', '2026-10-14 20:56:35.899269', 'visible', 'semilla'),
(21, 7, 11, NULL, 4, 4, 'Muy recomendable', 'Buena relación precio/calidad, con detalles muy cuidados.', '2026-11-07 20:56:35.899269', 'visible', 'semilla'),
(22, 16, 14, NULL, 5, 5, 'Superó mis expectativas', 'Atención excelente del proveedor y del guía durante todo el viaje.', '2026-10-11 20:56:35.899269', 'visible', 'semilla'),
(23, 8, 14, NULL, 5, 5, 'Superó mis expectativas', 'Atención excelente del proveedor y del guía durante todo el viaje.', '2026-11-04 20:56:35.899269', 'visible', 'semilla')
ON CONFLICT DO NOTHING;

SELECT setval('public.actividad_turistica_id_actividad_seq', GREATEST(COALESCE((SELECT MAX(id_actividad) FROM actividad_turistica), 1), COALESCE((SELECT last_value FROM public.actividad_turistica_id_actividad_seq), 1)), (SELECT COUNT(*) FROM actividad_turistica) > 0);
SELECT setval('public.alimentacion_id_alimentacion_seq', GREATEST(COALESCE((SELECT MAX(id_alimentacion) FROM alimentacion), 1), COALESCE((SELECT last_value FROM public.alimentacion_id_alimentacion_seq), 1)), (SELECT COUNT(*) FROM alimentacion) > 0);
SELECT setval('public.alojamiento_id_alojamiento_seq', GREATEST(COALESCE((SELECT MAX(id_alojamiento) FROM alojamiento), 1), COALESCE((SELECT last_value FROM public.alojamiento_id_alojamiento_seq), 1)), (SELECT COUNT(*) FROM alojamiento) > 0);
SELECT setval('public.auditoria_admin_id_auditoria_seq', GREATEST(COALESCE((SELECT MAX(id_auditoria) FROM auditoria_admin), 1), COALESCE((SELECT last_value FROM public.auditoria_admin_id_auditoria_seq), 1)), (SELECT COUNT(*) FROM auditoria_admin) > 0);
SELECT setval('public.cliente_id_cliente_seq', GREATEST(COALESCE((SELECT MAX(id_cliente) FROM cliente), 1), COALESCE((SELECT last_value FROM public.cliente_id_cliente_seq), 1)), (SELECT COUNT(*) FROM cliente) > 0);
SELECT setval('public.cliente_insignia_id_cliente_insignia_seq', GREATEST(COALESCE((SELECT MAX(id_cliente_insignia) FROM cliente_insignia), 1), COALESCE((SELECT last_value FROM public.cliente_insignia_id_cliente_insignia_seq), 1)), (SELECT COUNT(*) FROM cliente_insignia) > 0);
SELECT setval('public.contrato_id_contrato_seq', GREATEST(COALESCE((SELECT MAX(id_contrato) FROM contrato), 1), COALESCE((SELECT last_value FROM public.contrato_id_contrato_seq), 1)), (SELECT COUNT(*) FROM contrato) > 0);
SELECT setval('public.destino_id_destino_seq', GREATEST(COALESCE((SELECT MAX(id_destino) FROM destino), 1), COALESCE((SELECT last_value FROM public.destino_id_destino_seq), 1)), (SELECT COUNT(*) FROM destino) > 0);
SELECT setval('public.documento_id_documento_seq', GREATEST(COALESCE((SELECT MAX(id_documento) FROM documento), 1), COALESCE((SELECT last_value FROM public.documento_id_documento_seq), 1)), (SELECT COUNT(*) FROM documento) > 0);
SELECT setval('public.encuesta_pregunta_id_pregunta_seq', GREATEST(COALESCE((SELECT MAX(id_pregunta) FROM encuesta_pregunta), 1), COALESCE((SELECT last_value FROM public.encuesta_pregunta_id_pregunta_seq), 1)), (SELECT COUNT(*) FROM encuesta_pregunta) > 0);
SELECT setval('public.encuesta_respuesta_id_respuesta_seq', GREATEST(COALESCE((SELECT MAX(id_respuesta) FROM encuesta_respuesta), 1), COALESCE((SELECT last_value FROM public.encuesta_respuesta_id_respuesta_seq), 1)), (SELECT COUNT(*) FROM encuesta_respuesta) > 0);
SELECT setval('public.favoritos_id_favorito_seq', GREATEST(COALESCE((SELECT MAX(id_favorito) FROM favoritos), 1), COALESCE((SELECT last_value FROM public.favoritos_id_favorito_seq), 1)), (SELECT COUNT(*) FROM favoritos) > 0);
SELECT setval('public.guia_turistico_id_guia_seq', GREATEST(COALESCE((SELECT MAX(id_guia) FROM guia_turistico), 1), COALESCE((SELECT last_value FROM public.guia_turistico_id_guia_seq), 1)), (SELECT COUNT(*) FROM guia_turistico) > 0);
SELECT setval('public.historial_busqueda_id_busqueda_seq', GREATEST(COALESCE((SELECT MAX(id_busqueda) FROM historial_busqueda), 1), COALESCE((SELECT last_value FROM public.historial_busqueda_id_busqueda_seq), 1)), (SELECT COUNT(*) FROM historial_busqueda) > 0);
SELECT setval('public.insignia_id_insignia_seq', GREATEST(COALESCE((SELECT MAX(id_insignia) FROM insignia), 1), COALESCE((SELECT last_value FROM public.insignia_id_insignia_seq), 1)), (SELECT COUNT(*) FROM insignia) > 0);
SELECT setval('public.itinerario_actividad_id_itin_actividad_seq', GREATEST(COALESCE((SELECT MAX(id_itin_actividad) FROM itinerario_actividad), 1), COALESCE((SELECT last_value FROM public.itinerario_actividad_id_itin_actividad_seq), 1)), (SELECT COUNT(*) FROM itinerario_actividad) > 0);
SELECT setval('public.itinerario_viaje_id_itinerario_seq', GREATEST(COALESCE((SELECT MAX(id_itinerario) FROM itinerario_viaje), 1), COALESCE((SELECT last_value FROM public.itinerario_viaje_id_itinerario_seq), 1)), (SELECT COUNT(*) FROM itinerario_viaje) > 0);
SELECT setval('public.lista_suenos_id_sueno_seq', GREATEST(COALESCE((SELECT MAX(id_sueno) FROM lista_suenos), 1), COALESCE((SELECT last_value FROM public.lista_suenos_id_sueno_seq), 1)), (SELECT COUNT(*) FROM lista_suenos) > 0);
SELECT setval('public.metodo_pago_proveedor_id_metodo_proveedor_seq', GREATEST(COALESCE((SELECT MAX(id_metodo_proveedor) FROM metodo_pago_proveedor), 1), COALESCE((SELECT last_value FROM public.metodo_pago_proveedor_id_metodo_proveedor_seq), 1)), (SELECT COUNT(*) FROM metodo_pago_proveedor) > 0);
SELECT setval('public.nivel_id_nivel_seq', GREATEST(COALESCE((SELECT MAX(id_nivel) FROM nivel), 1), COALESCE((SELECT last_value FROM public.nivel_id_nivel_seq), 1)), (SELECT COUNT(*) FROM nivel) > 0);
SELECT setval('public.notificacion_id_notificacion_seq', GREATEST(COALESCE((SELECT MAX(id_notificacion) FROM notificacion), 1), COALESCE((SELECT last_value FROM public.notificacion_id_notificacion_seq), 1)), (SELECT COUNT(*) FROM notificacion) > 0);
SELECT setval('public.paquete_turistico_id_paquete_seq', GREATEST(COALESCE((SELECT MAX(id_paquete) FROM paquete_turistico), 1), COALESCE((SELECT last_value FROM public.paquete_turistico_id_paquete_seq), 1)), (SELECT COUNT(*) FROM paquete_turistico) > 0);
SELECT setval('public.promocion_id_promocion_seq', GREATEST(COALESCE((SELECT MAX(id_promocion) FROM promocion), 1), COALESCE((SELECT last_value FROM public.promocion_id_promocion_seq), 1)), (SELECT COUNT(*) FROM promocion) > 0);
SELECT setval('public.proveedor_id_proveedor_seq', GREATEST(COALESCE((SELECT MAX(id_proveedor) FROM proveedor), 1), COALESCE((SELECT last_value FROM public.proveedor_id_proveedor_seq), 1)), (SELECT COUNT(*) FROM proveedor) > 0);
SELECT setval('public.referido_id_referido_seq', GREATEST(COALESCE((SELECT MAX(id_referido) FROM referido), 1), COALESCE((SELECT last_value FROM public.referido_id_referido_seq), 1)), (SELECT COUNT(*) FROM referido) > 0);
SELECT setval('public.resena_paquete_id_resena_seq', GREATEST(COALESCE((SELECT MAX(id_resena) FROM resena_paquete), 1), COALESCE((SELECT last_value FROM public.resena_paquete_id_resena_seq), 1)), (SELECT COUNT(*) FROM resena_paquete) > 0);
SELECT setval('public.reserva_id_reserva_seq', GREATEST(COALESCE((SELECT MAX(id_reserva) FROM reserva), 1), COALESCE((SELECT last_value FROM public.reserva_id_reserva_seq), 1)), (SELECT COUNT(*) FROM reserva) > 0);
SELECT setval('public.reserva_seguro_id_reserva_seguro_seq', GREATEST(COALESCE((SELECT MAX(id_reserva_seguro) FROM reserva_seguro), 1), COALESCE((SELECT last_value FROM public.reserva_seguro_id_reserva_seguro_seq), 1)), (SELECT COUNT(*) FROM reserva_seguro) > 0);
SELECT setval('public.salida_paquete_id_salida_seq', GREATEST(COALESCE((SELECT MAX(id_salida) FROM salida_paquete), 1), COALESCE((SELECT last_value FROM public.salida_paquete_id_salida_seq), 1)), (SELECT COUNT(*) FROM salida_paquete) > 0);
SELECT setval('public.seguro_id_seguro_seq', GREATEST(COALESCE((SELECT MAX(id_seguro) FROM seguro), 1), COALESCE((SELECT last_value FROM public.seguro_id_seguro_seq), 1)), (SELECT COUNT(*) FROM seguro) > 0);
SELECT setval('public.seguro_servicio_id_seguro_servicio_seq', GREATEST(COALESCE((SELECT MAX(id_seguro_servicio) FROM seguro_servicio), 1), COALESCE((SELECT last_value FROM public.seguro_servicio_id_seguro_servicio_seq), 1)), (SELECT COUNT(*) FROM seguro_servicio) > 0);
SELECT setval('public.servicio_extra_id_servicio_extra_seq', GREATEST(COALESCE((SELECT MAX(id_servicio_extra) FROM servicio_extra), 1), COALESCE((SELECT last_value FROM public.servicio_extra_id_servicio_extra_seq), 1)), (SELECT COUNT(*) FROM servicio_extra) > 0);
SELECT setval('public.tipo_seguro_id_tipo_seguro_seq', GREATEST(COALESCE((SELECT MAX(id_tipo_seguro) FROM tipo_seguro), 1), COALESCE((SELECT last_value FROM public.tipo_seguro_id_tipo_seguro_seq), 1)), (SELECT COUNT(*) FROM tipo_seguro) > 0);
SELECT setval('public.transporte_id_transporte_seq', GREATEST(COALESCE((SELECT MAX(id_transporte) FROM transporte), 1), COALESCE((SELECT last_value FROM public.transporte_id_transporte_seq), 1)), (SELECT COUNT(*) FROM transporte) > 0);
SELECT setval('public.viajero_reserva_id_viajero_seq', GREATEST(COALESCE((SELECT MAX(id_viajero) FROM viajero_reserva), 1), COALESCE((SELECT last_value FROM public.viajero_reserva_id_viajero_seq), 1)), (SELECT COUNT(*) FROM viajero_reserva) > 0);

COMMIT;
