from .base_repo import BaseRepository
from domain.models.job import ScrapingJob
from application.schemas.job import JobCreate, JobUpdate


class JobRepository(BaseRepository[ScrapingJob, JobCreate, JobUpdate]):
    pass


job_repo = JobRepository(ScrapingJob)
