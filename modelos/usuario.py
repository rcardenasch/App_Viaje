
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from typing import Optional
from modelos import db

if TYPE_CHECKING:
    from modelos.reserva import Reserva
    from modelos.vehiculo import Vehiculo
    from modelos.propietario import Propietario


class Usuario(db.Model):

    __tablename__ = "usuarios"

    __table_args__ = (
        CheckConstraint(
            "rol IN ('ADMINISTRADOR', 'PROPIETARIO', 'PASAJERO')",
            name="ck_usuarios_rol"
        ),
    )

    id_usuario: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombres: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    apellidos: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    correo: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        String(30)
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    rol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PASAJERO"
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    vehiculos: Mapped[List["Vehiculo"]] = relationship(
        back_populates="propietario"
    )

    reservas: Mapped[List["Reserva"]] = relationship(
        back_populates="pasajero"
    )

    perfil_propietario: Mapped[Optional["Propietario"]] = relationship(
    back_populates="usuario",
    uselist=False,
    cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario {self.correo}>"
