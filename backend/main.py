import logging
from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager
from infrastructure.config.logger import setup_logging
from application.services.error_handler import register_exception_handlers

from infrastructure.config.settings import settings
from application.api.v1 import (
    # auth,
    jobs as url_jobs,  # Renombrar para claridad
    # results,
    configs as config_jobs,  # Nuevo
    scraping_jobs as job_jobs,  # Nuevo
)

setup_logging()

logger = logging.getLogger(__name__)


# --- Ciclo de vida con lifespan (recomendado en FastAPI moderno) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    # await connect_to_db()
    yield
    logger.info("Application shutdown...")
    # await close_db_connection()


# Pasamos el lifespan para manejar startup/shutdown
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,  # Usar lifespan
)

register_exception_handlers(app)

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(config_jobs.router, prefix="/configs", tags=["configs"])
api_router.include_router(job_jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(url_jobs.router, prefix="/urls", tags=["urls"])

app.include_router(api_router)


# --- Ruta Raíz (Opcional) ---
@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# --- Ejecución con Uvicorn (si ejecutas este archivo directamente) ---
# Esto es más para desarrollo/debug. En producción usarás un comando uvicorn/gunicorn.
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Escucha en todas las interfaces
        port=8000,
        reload=True,  # Activa reload (solo para desarrollo)
        log_level=logging.getLevelName(
            logger.getEffectiveLevel()
        ).lower(),  # Pasar nivel de log a uvicorn
    )
