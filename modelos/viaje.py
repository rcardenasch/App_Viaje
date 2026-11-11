
from datetime import date, time, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Date,
    Time,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from modelos import db

if TYPE_CHECKING:
    from modelos.bloqueo_asiento import BloqueoAsiento
    from modelos.reserva import Reserva
    from modelos.vehiculo import Vehiculo 

class Viaje(db.Model):

    __tablename__ = "viajes"

    __table_args__ = (
        CheckConstraint(
            "precio >= 0",
            name="ck_viaje_precio"
        ),
        CheckConstraint(
            "estado IN ('PROGRAMADO', 'ACTIVO', 'EN_CURSO', 'FINALIZADO', 'CANCELADO')",
            name="ck_viaje_estado"
        ),
    )

    id_viaje: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_vehiculo: Mapped[int] = mapped_column(
        ForeignKey("vehiculos.id_vehiculo"),
        nullable=False,
        index=True
    )

    origen: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    destino: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    fecha_salida: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    hora_salida: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    hora_llegada: Mapped[Optional[time]] = mapped_column(
        Time
    )

    precio: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        default="PROGRAMADO",
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    vehiculo: Mapped["Vehiculo"] = relationship(
        back_populates="viajes"
    )

    reservas: Mapped[List["Reserva"]] = relationship(
        back_populates="viaje"
    )

    bloqueos: Mapped[List["BloqueoAsiento"]] = relationship(
        back_populates="viaje"
    )
