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