from datetime import datetime, date

from sqlalchemy import Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow, uuid_pk


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = uuid_pk()
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    date: Mapped[date] = mapped_column(Date)
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    reach: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    profile_views: Mapped[int] = mapped_column(Integer, default=0)
    website_clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    client: Mapped["Client"] = relationship(back_populates="metrics")
