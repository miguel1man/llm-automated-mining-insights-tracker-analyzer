from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from infrastructure.config.settings import settings

# Crea el engine asíncrono
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    # echo=True, # Descomenta para ver las queries SQL generadas (útil para debug)
)

# Crea una fábrica de sesiones asíncronas
AsyncSessionFactory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Importante para async y FastAPI
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener una sesión de base de datos asíncrona.
    Asegura que la sesión se cierre correctamente.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # No necesitas commit aquí si tus operaciones en el repo hacen commit
        except Exception:
            await session.rollback()  # Rollback en caso de error en la ruta
            raise
        finally:
            await session.close()  # Cierra la sesión
