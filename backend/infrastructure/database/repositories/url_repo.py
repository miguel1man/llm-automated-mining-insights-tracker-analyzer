from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
)
from typing import List

from .base_repo import BaseRepository
from domain.models.scrape_url import ScrapeUrl
from application.schemas.url import UrlCreate, UrlUpdate


class UrlRepository(BaseRepository[ScrapeUrl, UrlCreate, UrlUpdate]):
    """
    Repositorio específico para manejar las operaciones CRUD de la entidad ScrapeUrl.
    Hereda la funcionalidad genérica de BaseRepository.
    """

    # Estos métodos usarán self.model (que es ScrapeUrl) y requerirán AsyncSession.
    async def get_pending_urls_ordered(
        self, db: AsyncSession, limit: int = 100
    ) -> List[ScrapeUrl]:
        """
        Obtiene URLs pendientes, ordenadas por prioridad (desc) y fecha de creación (asc).
        """
        statement = (
            select(self.model)
            .where(self.model.status == "pending")
            .order_by(self.model.priority.desc(), self.model.created_at.asc())
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()


# Crea una instancia singleton del repositorio.
# Esta es la instancia que otros módulos importarán.
# Pasa el modelo SQLAlchemy (ScrapeUrl) al constructor de la clase base.
url_repo = UrlRepository(ScrapeUrl)
