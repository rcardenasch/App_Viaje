
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelos import db
from modelos.viaje import Viaje


class BloqueoAsiento(db.Model):

    __tablename__ = "bloqueos_asientos"

    __table_args__ = (
        # Un solo bloqueo activo por asiento y viaje.
        Index(
            "uq_bloqueo_viaje_asiento_activo",
            "id_viaje",
            "id_asiento",
            unique=True,
            postgresql_where=text("estado = 'ACTIVO'")
        ),
    )

    id_bloqueo: Mapped[int] = mapped_column(
        primary_key=True
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

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        index=True
    )

    token: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVO",
        nullable=False
    )

    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    fecha_expiracion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    viaje: Mapped["Viaje"] = relationship(
        back_populates="bloqueos"
    )
