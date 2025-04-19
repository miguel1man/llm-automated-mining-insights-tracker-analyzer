import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
)  # Importar excepciones de SQLAlchemy

from domain.models.base_model import Base
from domain.exceptions import (
    DatabaseError,
    ResourceNotFound,
)  # Importar excepciones personalizadas

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)  # Obtener logger


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def _execute_query(
        self, db: AsyncSession, statement, operation: str = "query execution"
    ):
        """Método helper para ejecutar queries y manejar errores comunes."""
        try:
            result = await db.execute(statement)
            return result
        except IntegrityError as e:
            await db.rollback()
            logger.error(
                f"Database integrity error during {operation} for {self.model.__name__}: {e}",
                exc_info=True,
            )
            # Podrías analizar 'e' para dar un mensaje más específico (ej: constraint violation)
            raise DatabaseError(
                f"Data conflict during {operation}.", original_exception=e
            )
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Database error during {operation} for {self.model.__name__}: {e}",
                exc_info=True,
            )
            raise DatabaseError(
                f"Could not complete {operation} due to a database issue.",
                original_exception=e,
            )
        except Exception as e:  # Captura otros posibles errores inesperados
            await db.rollback()
            logger.error(
                f"Unexpected error during {operation} for {self.model.__name__}: {e}",
                exc_info=True,
            )
            raise DatabaseError(
                f"An unexpected error occurred during {operation}.",
                original_exception=e,
            )

    async def _commit_and_refresh(
        self, db: AsyncSession, db_obj: ModelType, operation: str = "commit"
    ):
        """Método helper para hacer commit, refresh y manejar errores."""
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:  # Puede ocurrir en commit diferido
            await db.rollback()
            logger.error(
                f"Database integrity error during {operation} for {self.model.__name__} (ID: {getattr(db_obj, 'id', 'N/A')}): {e}",
                exc_info=True,
            )
            raise DatabaseError(
                f"Data conflict during {operation}.", original_exception=e
            )
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Database error during {operation} for {self.model.__name__} (ID: {getattr(db_obj, 'id', 'N/A')}): {e}",
                exc_info=True,
            )
            raise DatabaseError(
                f"Could not complete {operation} due to a database issue.",
                original_exception=e,
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Unexpected error during {operation} for {self.model.__name__} (ID: {getattr(db_obj, 'id', 'N/A')}): {e}",
                exc_info=True,
            )
            raise DatabaseError(
                f"An unexpected error occurred during {operation}.",
                original_exception=e,
            )

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == id)
        result = await self._execute_query(db, statement, operation="get")
        return result.scalar_one_or_none()

    async def get_or_404(self, db: AsyncSession, id: Any) -> ModelType:
        """Obtiene por ID o lanza ResourceNotFound."""
        db_obj = await self.get(db, id)
        if db_obj is None:
            raise ResourceNotFound(resource=self.model.__name__, identifier=f"ID {id}")
        return db_obj

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await self._execute_query(db, statement, operation="get_multi")
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        logger.debug(f"Attempting to create {self.model.__name__} with data: {obj_in}")
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        # El commit y refresh se manejan en el helper
        created_obj = await self._commit_and_refresh(db, db_obj, operation="create")
        logger.info(
            f"Successfully created {self.model.__name__} with ID: {created_obj.id}"
        )
        return created_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        logger.debug(
            f"Attempting to update {self.model.__name__} (ID: {db_obj.id}) with data: {obj_in}"
        )
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)  # SQLAlchemy maneja esto como una actualización
        updated_obj = await self._commit_and_refresh(db, db_obj, operation="update")
        logger.info(
            f"Successfully updated {self.model.__name__} with ID: {updated_obj.id}"
        )
        return updated_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        logger.debug(f"Attempting to remove {self.model.__name__} with ID: {id}")
        # Usamos get_or_404 para asegurar que existe antes de intentar borrar
        # obj = await self.get_or_404(db, id) # Opcional: Lanza 404 si no existe
        obj = await self.get(db, id)  # O simplemente intenta borrar
        if obj:
            try:
                await db.delete(obj)
                await db.commit()
                logger.info(f"Successfully removed {self.model.__name__} with ID: {id}")
                return obj
            except (
                IntegrityError
            ) as e:  # Ej: Si otras tablas dependen de esta fila y no hay CASCADE
                await db.rollback()
                logger.error(
                    f"Database integrity error during remove for {self.model.__name__} (ID: {id}): {e}",
                    exc_info=True,
                )
                raise DatabaseError(
                    f"Cannot remove {self.model.__name__} due to dependencies.",
                    original_exception=e,
                )
            except SQLAlchemyError as e:
                await db.rollback()
                logger.error(
                    f"Database error during remove for {self.model.__name__} (ID: {id}): {e}",
                    exc_info=True,
                )
                raise DatabaseError(
                    f"Could not remove {self.model.__name__} due to a database issue.",
                    original_exception=e,
                )
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"Unexpected error during remove for {self.model.__name__} (ID: {id}): {e}",
                    exc_info=True,
                )
                raise DatabaseError(
                    f"An unexpected error occurred during remove.", original_exception=e
                )
        else:
            logger.warning(
                f"Attempted to remove non-existent {self.model.__name__} with ID: {id}"
            )
            # Opcionalmente lanzar ResourceNotFound aquí si se espera que siempre exista
            # raise ResourceNotFound(resource=self.model.__name__, identifier=f"ID {id}")
            return None  # O retornar None si es aceptable intentar borrar algo que no existe
