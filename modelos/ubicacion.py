
from sqlalchemy import (
    String,
    Boolean,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING, Optional

from modelos import db

if TYPE_CHECKING:
    from modelos.viaje import Viaje


class Ubicacion(db.Model):

    __tablename__ = "ubicaciones"

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            "departamento",
            "provincia",
            "distrito",
            name="uq_ubicacion_completa"
        ),
        Index("ix_ubicacion_nombre", "nombre"),
    )

    id_ubicacion: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    departamento: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    provincia: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    distrito: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    referencia: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    viajes_origen: Mapped[List["Viaje"]] = relationship(
        back_populates="ubicacion_origen",
        foreign_keys="Viaje.id_origen"
    )

    viajes_destino: Mapped[List["Viaje"]] = relationship(
        back_populates="ubicacion_destino",
        foreign_keys="Viaje.id_destino"
    )

    @property
    def nombre_completo(self):
        return (
            f"{self.nombre} - {self.distrito}, "
            f"{self.provincia}, {self.departamento}"
        )

    def __repr__(self):
        return f"<Ubicacion {self.nombre_completo}>"
