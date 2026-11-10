
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Boolean,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelos import db
from modelos.asiento import Asiento
from modelos.plantilla_asientos import PlantillaAsientos
from modelos.usuario import Usuario
from modelos.viaje import Viaje


class Vehiculo(db.Model):

    __tablename__ = "vehiculos"

    __table_args__ = (
        CheckConstraint(
            "cantidad_asientos > 0",
            name="ck_vehiculo_asientos"
        ),
        CheckConstraint(
            "tipo IN ('AUTO', 'VAN', 'MINIBUS', 'BUS', 'OTRO')",
            name="ck_vehiculo_tipo"
        ),
    )

    id_vehiculo: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_propietario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        index=True
    )

    id_plantilla: Mapped[int] = mapped_column(
        ForeignKey("plantillas_asientos.id_plantilla"),
        nullable=False
    )

    placa: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    marca: Mapped[str | None] = mapped_column(
        String(80)
    )

    modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    cantidad_asientos: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    propietario: Mapped["Usuario"] = relationship(
        back_populates="vehiculos"
    )

    plantilla: Mapped["PlantillaAsientos"] = relationship(
        back_populates="vehiculos"
    )

    asientos: Mapped[list["Asiento"]] = relationship(
        back_populates="vehiculo",
        cascade="all, delete-orphan"
    )

    viajes: Mapped[list["Viaje"]] = relationship(
        back_populates="vehiculo"
    )
