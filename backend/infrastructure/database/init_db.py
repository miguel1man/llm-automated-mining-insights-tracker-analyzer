import asyncio
from .session import async_engine
from domain.models.base_model import Base

from domain.models.scrape_url import ScrapeUrl
from domain.models.config import ScrapeConfig
from domain.models.job import ScrapingJob
from domain.models.base_model import Base


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")


if __name__ == "__main__":
    asyncio.run(init_db())
