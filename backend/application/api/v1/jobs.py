import uuid
import logging
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import get_db
from infrastructure.database.repositories.url_repo import url_repo
from application.schemas.url import UrlCreate, UrlRead


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/urls/", response_model=UrlRead, status_code=status.HTTP_201_CREATED)
async def create_scrape_url(*, db: AsyncSession = Depends(get_db), url_in: UrlCreate):
    """
    Crea una nueva URL para scrapear.

    Puede lanzar errores:
    - 422 Unprocessable Entity: Si los datos de entrada no son válidos.
    - 503 Service Unavailable: Si hay un error de base de datos al crear.
    - 500 Internal Server Error: Para otros errores inesperados.
    """
    logger.info(f"Received request to create URL: {url_in.url}")
    created_url = await url_repo.create(db=db, obj_in=url_in)
    return created_url


@router.get("/urls/{url_id}", response_model=UrlRead)
async def read_scrape_url(url_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request to read URL with ID: {url_id}")
    # Usa get_or_404 para que lance ResourceNotFound si no existe,
    # el manejador global lo convertirá en un 404 Not Found.
    db_url = await url_repo.get_or_404(db=db, id=url_id)
    return db_url
