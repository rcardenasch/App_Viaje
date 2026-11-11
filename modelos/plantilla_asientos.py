
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    JSON,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from modelos import db

if TYPE_CHECKING:
    from modelos.vehiculo import Vehiculo


class PlantillaAsientos(db.Model):

    __tablename__ = "plantillas_asientos"

    __table_args__ = (
        UniqueConstraint(
            "nombre",
            name="uq_plantilla_nombre"
        ),
    )

    id_plantilla: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        String(250)
    )

    filas: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    columnas: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    cantidad_asientos: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    distribucion: Mapped[List] = mapped_column(
        JSON,
        nullable=False
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    vehiculos: Mapped[List["Vehiculo"]] = relationship(
        back_populates="plantilla"
    )
