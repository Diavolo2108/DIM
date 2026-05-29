import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class ClientStatus(str, enum.Enum):
    EN_CAMPANA = "EN_CAMPANA"
    EN_PAUSA = "EN_PAUSA"
    INACTIVA = "INACTIVA"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    instagram_username: Mapped[str] = mapped_column(String(100), unique=True)
    instagram_account_id: Mapped[str] = mapped_column(String(100))
    access_token_encrypted: Mapped[str] = mapped_column(String(1024))
    app_secret_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus), default=ClientStatus.EN_PAUSA
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    posts: Mapped[list["Post"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    auto_reply: Mapped["AutoReply | None"] = relationship(back_populates="client", cascade="all, delete-orphan")
    metrics: Mapped[list["Metric"]] = relationship(back_populates="client", cascade="all, delete-orphan")
