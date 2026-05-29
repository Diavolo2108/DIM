import enum
from datetime import datetime, date

from sqlalchemy import String, Enum, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class CampaignStatus(str, enum.Enum):
    PLANIFICACION = "PLANIFICACION"
    ACTIVA = "ACTIVA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = uuid_pk()
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    name: Mapped[str] = mapped_column(String(255))
    objetivo: Mapped[str] = mapped_column(Text)
    duracion_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    duracion_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    frecuencia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tono: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashtags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.PLANIFICACION
    )
    contexto_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    aprobacion_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    client: Mapped["Client"] = relationship(back_populates="campaigns")
    posts: Mapped[list["Post"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="campaign")
