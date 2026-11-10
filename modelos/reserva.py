
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelos import db
from modelos.asiento import Asiento
from modelos.usuario import Usuario
from modelos.viaje import Viaje


class Reserva(db.Model):

    __tablename__ = "reservas"

    __table_args__ = (
        CheckConstraint(
            "estado IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'VENCIDA')",
            name="ck_reserva_estado"
        ),

        CheckConstraint(
            "importe >= 0",
            name="ck_reserva_importe"
        ),

        # Un asiento solo puede tener una reserva confirmada
        # para el mismo viaje.
        Index(
            "uq_reserva_viaje_asiento_confirmada",
            "id_viaje",
            "id_asiento",
            unique=True,
            postgresql_where=text("estado = 'CONFIRMADA'")
        ),
    )

    id_reserva: Mapped[int] = mapped_column(
        primary_key=True
    )

    codigo_reserva: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    clave_idempotencia: Mapped[str | None] = mapped_column(
        String(100),
        unique=True
    )

    id_viaje: Mapped[int] = mapped_column(
        ForeignKey("viajes.id_viaje"),
        nullable=False,
        index=True
    )

    id_asiento: Mapped[int] = mapped_column(
        ForeignKey("asientos.id_asiento"),
        nullable=False,
        index=True
    )

    id_pasajero: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        index=True
    )

    importe: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        default="PENDIENTE",
        nullable=False
    )

    fecha_reserva: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    fecha_confirmacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    viaje: Mapped["Viaje"] = relationship(
        back_populates="reservas"
    )

    asiento: Mapped["Asiento"] = relationship(
        back_populates="reservas"
    )

    pasajero: Mapped["Usuario"] = relationship(
        back_populates="reservas"
    )
