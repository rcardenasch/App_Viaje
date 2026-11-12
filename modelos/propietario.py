# modelos/propietario.py

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelos import db

if TYPE_CHECKING:
    from modelos.usuario import Usuario


class Propietario(db.Model):

    __tablename__ = "propietarios"

    __table_args__ = (
        UniqueConstraint(
            "numero_documento",
            name="uq_propietario_documento"
        ),
        CheckConstraint(
            "tipo_documento IN ('DNI', 'CE', 'RUC', 'PASAPORTE')",
            name="ck_propietario_tipo_documento"
        ),
    )

    id_propietario: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    tipo_documento: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        default="DNI"
    )

    numero_documento: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    direccion: Mapped[Optional[str]] = mapped_column(
        String(250)
    )

    licencia_mtc: Mapped[Optional[str]] = mapped_column(
        String(40)
    )

    verificado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
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

    usuario: Mapped["Usuario"] = relationship(
        back_populates="perfil_propietario"
    )