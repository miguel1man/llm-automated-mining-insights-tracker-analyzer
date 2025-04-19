import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import get_db
from infrastructure.database.repositories.job_repo import job_repo
from application.schemas.job import JobCreate, JobRead
from domain.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_scraping_job(*, db: AsyncSession = Depends(get_db), job_in: JobCreate):
    """Crea un nuevo trabajo de scraping."""
    logger.info(f"Received request to create job")
    created_job = await job_repo.create(db=db, obj_in=job_in)
    return created_job


@router.get("/{job_id}", response_model=JobRead)
async def read_scraping_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene un trabajo de scraping por su ID."""
    logger.info(f"Received request to read job with ID: {job_id}")
    try:
        db_job = await job_repo.get_or_404(db=db, id=job_id)
        return db_job
    except ResourceNotFound as e:
        logger.warning(f"Job not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
