import enum
from datetime import datetime

from sqlalchemy import Integer, String, Enum, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class PostFormat(str, enum.Enum):
    IMAGE = "IMAGE"
    CAROUSEL = "CAROUSEL"
    REEL = "REEL"


class PostStatus(str, enum.Enum):
    PROGRAMADO = "PROGRAMADO"
    PUBLICADO = "PUBLICADO"
    FALLIDO = "FALLIDO"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = uuid_pk()
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    format: Mapped[PostFormat] = mapped_column(Enum(PostFormat), default=PostFormat.IMAGE)
    copy: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    instagram_media_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.PROGRAMADO)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    client: Mapped["Client"] = relationship(back_populates="posts")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="posts")
    assets: Mapped[list["Asset"]] = relationship(back_populates="post")
    messages: Mapped[list["Message"]] = relationship(back_populates="post")
