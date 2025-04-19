import uuid
from datetime import datetime
from typing import List, Dict, Any, TYPE_CHECKING

from sqlalchemy import Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base_model import Base

if TYPE_CHECKING:
    from .scrape_url import ScrapeUrl


class ScrapeConfig(Base):
    __tablename__ = "scrape_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_name: Mapped[str] = mapped_column(Text, nullable=False)
    selectors: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relación inversa
    scrape_urls: Mapped[List["ScrapeUrl"]] = relationship(
        "ScrapeUrl", back_populates="config"
    )

    def __repr__(self):
        return f"<ScrapeConfig(id={self.id}, site_name='{self.site_name}')>"
