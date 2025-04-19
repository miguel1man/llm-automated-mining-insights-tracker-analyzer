from .base_repo import BaseRepository
from domain.models.config import ScrapeConfig
from application.schemas.config import ConfigCreate, ConfigUpdate


class ConfigRepository(BaseRepository[ScrapeConfig, ConfigCreate, ConfigUpdate]):
    pass


config_repo = ConfigRepository(ScrapeConfig)
