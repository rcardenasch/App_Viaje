
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Importar todos los modelos para registrar las tablas
from modelos.usuario import Usuario
from modelos.vehiculo import Vehiculo
from modelos.plantilla_asientos import PlantillaAsientos
from modelos.asiento import Asiento
from modelos.viaje import Viaje
from modelos.reserva import Reserva
from modelos.bloqueo_asiento import BloqueoAsiento


__all__ = [
    "db",
    "Usuario",
    "Vehiculo",
    "PlantillaAsientos",
    "Asiento",
    "Viaje",
    "Reserva",
    "BloqueoAsiento"
]
