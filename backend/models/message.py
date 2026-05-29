import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class MessageType(str, enum.Enum):
    DM = "DM"
    COMMENT = "COMMENT"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = uuid_pk()
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    post_id: Mapped[str | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    instagram_thread_id: Mapped[str] = mapped_column(String(100))
    instagram_message_id: Mapped[str] = mapped_column(String(100), unique=True)
    sender_id: Mapped[str] = mapped_column(String(100))
    sender_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[MessageType] = mapped_column(Enum(MessageType))
    is_from_page: Mapped[bool] = mapped_column(Boolean, default=False)
    replied: Mapped[bool] = mapped_column(Boolean, default=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    client: Mapped["Client"] = relationship(back_populates="messages")
    post: Mapped["Post | None"] = relationship(back_populates="messages")
