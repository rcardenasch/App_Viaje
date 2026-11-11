CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombres VARCHAR(150) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(30),
    rol VARCHAR(20) NOT NULL
        CHECK (rol IN ('ADMINISTRADOR','PASAJERO')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehiculos (
    id_vehiculo SERIAL PRIMARY KEY,
    id_propietario INTEGER NOT NULL,
    placa VARCHAR(20) UNIQUE NOT NULL,
    modelo VARCHAR(100),
    tipo_plantilla VARCHAR(50),
    cantidad_asientos INTEGER NOT NULL,
    FOREIGN KEY(id_propietario)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE viajes (
    id_viaje SERIAL PRIMARY KEY,
    id_vehiculo INTEGER NOT NULL,
    origen VARCHAR(150) NOT NULL,
    destino VARCHAR(150) NOT NULL,
    fecha_salida DATE NOT NULL,
    hora_salida TIME NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    FOREIGN KEY(id_vehiculo)
        REFERENCES vehiculos(id_vehiculo)
);

CREATE TABLE asientos (
    id_asiento SERIAL PRIMARY KEY,
    id_vehiculo INTEGER NOT NULL,
    numero_asiento VARCHAR(10) NOT NULL,
    fila INTEGER,
    columna INTEGER,
    FOREIGN KEY(id_vehiculo)
        REFERENCES vehiculos(id_vehiculo)
);

CREATE UNIQUE INDEX idx_asiento_vehiculo
ON asientos(id_vehiculo, numero_asiento);

CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_viaje INTEGER NOT NULL,
    id_asiento INTEGER NOT NULL,
    id_pasajero INTEGER NOT NULL,

    estado VARCHAR(20)
        DEFAULT 'CONFIRMADO',

    fecha_reserva TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(id_viaje)
        REFERENCES viajes(id_viaje),

    FOREIGN KEY(id_asiento)
        REFERENCES asientos(id_asiento),

    FOREIGN KEY(id_pasajero)
        REFERENCES usuarios(id_usuario)
);

-- EVITA DOBLE RESERVA
CREATE UNIQUE INDEX uq_reserva_asiento_viaje
ON reservas(id_viaje,id_asiento)
WHERE estado='CONFIRMADO';

CREATE TABLE bloqueos_asientos (
    id_bloqueo SERIAL PRIMARY KEY,
    id_viaje INTEGER NOT NULL,
    id_asiento INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    token VARCHAR(36) NOT NULL UNIQUE,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_expiracion TIMESTAMPTZ NOT NULL,

    -- Llaves foráneas
    CONSTRAINT fk_bloqueos_viaje 
        FOREIGN KEY (id_viaje) REFERENCES viajes (id_viaje),
    CONSTRAINT fk_bloqueos_asiento 
        FOREIGN KEY (id_asiento) REFERENCES asientos (id_asiento),
    CONSTRAINT fk_bloqueos_usuario 
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
);

-- Índices simples (equivalentes a index=True en las columnas)
CREATE INDEX ix_bloqueos_asientos_id_viaje ON bloqueos_asientos (id_viaje);
CREATE INDEX ix_bloqueos_asientos_id_asiento ON bloqueos_asientos (id_asiento);
CREATE INDEX ix_bloqueos_asientos_id_usuario ON bloqueos_asientos (id_usuario);

-- Índice único parcial (equivalente a postgresql_where=text("estado = 'ACTIVO'"))
CREATE UNIQUE INDEX uq_bloqueo_viaje_asiento_activo 
    ON bloqueos_asientos (id_viaje, id_asiento) 
    WHERE estado = 'ACTIVO';

    CREATE TABLE plantillas_asientos (
    id_plantilla SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(250),
    filas INTEGER NOT NULL,
    columnas INTEGER NOT NULL,
    cantidad_asientos INTEGER NOT NULL,
    distribucion JSONB NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    -- Restricción única
    CONSTRAINT uq_plantilla_nombre UNIQUE (nombre)
);
