import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    TIMESTAMP,
    SmallInteger,
    String,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base_model import Base


if TYPE_CHECKING:
    from .scrape_url import ScrapeUrl


class ScrapingJob(Base):
    __tablename__ = "scraping_job"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    schedule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scraping_schedule.id", ondelete="SET NULL"),
        nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    total_urls: Mapped[Optional[int]] = mapped_column(SmallInteger, default=0)
    success_count: Mapped[Optional[int]] = mapped_column(SmallInteger, default=0)
    error_count: Mapped[Optional[int]] = mapped_column(SmallInteger, default=0)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="ck_scraping_job_status",
        ),
    )

    # Relación inversa: Usa string reference "ScrapeUrl"
    scrape_urls: Mapped[List["ScrapeUrl"]] = relationship(
        "ScrapeUrl", back_populates="job"
    )
    # Relación con Schedule (si tienes el modelo Schedule)
    # schedule: Mapped[Optional["ScrapingSchedule"]] = relationship("ScrapingSchedule", back_populates="jobs")
