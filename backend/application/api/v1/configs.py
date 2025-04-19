import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import get_db
from infrastructure.database.repositories.config_repo import config_repo
from application.schemas.config import ConfigCreate, ConfigRead, ConfigUpdate
from domain.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ConfigRead, status_code=status.HTTP_201_CREATED)
async def create_scrape_config(
    *, db: AsyncSession = Depends(get_db), config_in: ConfigCreate
):
    """Crea una nueva configuración de scraping."""
    logger.info(f"Received request to create config: {config_in.site_name}")
    created_config = await config_repo.create(db=db, obj_in=config_in)
    return created_config


@router.get("/{config_id}", response_model=ConfigRead)
async def read_scrape_config(config_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene una configuración por su ID."""
    logger.info(f"Received request to read config with ID: {config_id}")
    try:
        db_config = await config_repo.get_or_404(db=db, id=config_id)
        return db_config
    except ResourceNotFound as e:
        logger.warning(f"Config not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=List[ConfigRead])
async def read_scrape_configs(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    """Obtiene una lista de configuraciones."""
    logger.info(f"Received request to read configs list (skip={skip}, limit={limit})")
    configs = await config_repo.get_multi(db=db, skip=skip, limit=limit)
    return configs


@router.put("/{config_id}", response_model=ConfigRead)
async def update_scrape_config(
    config_id: uuid.UUID, *, db: AsyncSession = Depends(get_db), config_in: ConfigUpdate
):
    """Actualiza una configuración existente."""
    logger.info(f"Received request to update config with ID: {config_id}")
    try:
        db_config = await config_repo.get_or_404(db=db, id=config_id)
        updated_config = await config_repo.update(
            db=db, db_obj=db_config, obj_in=config_in
        )
        return updated_config
    except ResourceNotFound as e:
        logger.warning(f"Config not found for update: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scrape_config(
    config_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Elimina una configuración."""
    logger.info(f"Received request to delete config with ID: {config_id}")
    try:
        # Usamos get_or_404 para asegurar que existe antes de intentar borrar
        await config_repo.get_or_404(db=db, id=config_id)
        await config_repo.remove(db=db, id=config_id)
        # No retornamos contenido en un 204
    except ResourceNotFound as e:
        logger.warning(f"Config not found for delete: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
