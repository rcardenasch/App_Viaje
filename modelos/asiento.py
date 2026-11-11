
from typing import TYPE_CHECKING, List
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelos import db

if TYPE_CHECKING:
    from modelos.vehiculo import Vehiculo
    from modelos.reserva import Reserva

class Asiento(db.Model):

    __tablename__ = "asientos"

    __table_args__ = (
        UniqueConstraint(
            "id_vehiculo",
            "numero_asiento",
            name="uq_asiento_vehiculo_numero"
        ),
    )

    id_asiento: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_vehiculo: Mapped[int] = mapped_column(
        ForeignKey("vehiculos.id_vehiculo"),
        nullable=False,
        index=True
    )

    numero_asiento: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    fila: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    columna: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    vehiculo: Mapped["Vehiculo"] = relationship(
        back_populates="asientos"
    )

    reservas: Mapped[List["Reserva"]] = relationship(
        back_populates="asiento"
    )
