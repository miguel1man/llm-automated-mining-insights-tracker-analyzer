import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Text,
    String,
    TIMESTAMP,
    SmallInteger,
    ForeignKey,
    CheckConstraint,
    # Index # Descomenta si añades índices aquí
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID  # Quita JSONB si no se usa aquí

from .base_model import Base

# Para type hints sin importación circular en runtime
if TYPE_CHECKING:
    from .config import ScrapeConfig
    from .job import ScrapingJob


class ScrapeUrl(Base):
    __tablename__ = "scrape_url"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    config_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scrape_config.id", ondelete="CASCADE"),
        nullable=True,
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scraping_job.id", ondelete="CASCADE"),
        nullable=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False
    )
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    priority: Mapped[int] = mapped_column(SmallInteger, default=5, nullable=False)

    # --- Relaciones ---
    # Usar string references es más seguro contra imports circulares
    config: Mapped[Optional["ScrapeConfig"]] = relationship(
        "ScrapeConfig", back_populates="scrape_urls"
    )
    job: Mapped[Optional["ScrapingJob"]] = relationship(
        "ScrapingJob", back_populates="scrape_urls"
    )
    # Ejemplo si tuvieras ScrapedData con relación uno a uno/muchos
    # scraped_data_rel: Mapped[Optional["ScrapedData"]] = relationship(
    #    "ScrapedData", back_populates="scrape_url", uselist=False, cascade="all, delete-orphan"
    # )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'success', 'failed')",
            name="ck_scrape_url_status",
        ),
        CheckConstraint("priority BETWEEN 1 AND 10", name="ck_scrape_url_priority"),
        # Index('ix_scrape_url_status_priority', 'status', 'priority'), # Ejemplo de índice
    )

    def __repr__(self):
        return f"<ScrapeUrl(id={self.id}, url='{self.url[:30]}...', status='{self.status}')>"
