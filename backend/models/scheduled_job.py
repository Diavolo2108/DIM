import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, utcnow, uuid_pk


class JobStatus(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[str] = uuid_pk()
    job_type: Mapped[str] = mapped_column(String(100))
    reference_id: Mapped[str] = mapped_column(String(36))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDIENTE)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
