from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = uuid_pk()
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    post_id: Mapped[str | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    r2_key: Mapped[str] = mapped_column(String(512))
    r2_url: Mapped[str] = mapped_column(String(1024))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    client: Mapped["Client"] = relationship(back_populates="assets")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="assets")
    post: Mapped["Post | None"] = relationship(back_populates="assets")
