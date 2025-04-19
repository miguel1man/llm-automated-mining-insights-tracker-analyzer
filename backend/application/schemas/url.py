import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


# --- Base Schema ---
# Contiene los campos comunes que pueden ser compartidos
# por otros schemas para evitar repetición.
class UrlBase(BaseModel):
    url: HttpUrl  # Valida que sea una URL válida
    priority: Optional[int] = Field(
        default=5, ge=1, le=10, description="Prioridad de scraping (1-10)"
    )
    config_id: Optional[uuid.UUID] = (
        None  # Permitimos que sea opcional al crear/actualizar
    )
    job_id: Optional[uuid.UUID] = (
        None  # Permitimos que sea opcional al crear/actualizar
    )

    # Ejemplo de validador personalizado si fuera necesario
    # @field_validator('priority')
    # def priority_must_be_in_range(cls, v):
    #     if v is not None and not (1 <= v <= 10):
    #         raise ValueError('La prioridad debe estar entre 1 y 10')
    #     return v


# --- Create Schema ---
# Schema utilizado para validar los datos al crear una nueva URL.
# Hereda de UrlBase. No incluye campos generados por la DB como id, created_at.
class UrlCreate(UrlBase):
    # El campo 'url' es obligatorio porque no tiene default y no es Optional en UrlBase
    # 'priority', 'config_id', 'job_id' son opcionales o tienen default en UrlBase
    pass  # No necesita campos adicionales por ahora


# --- Update Schema ---
# Schema utilizado para validar los datos al actualizar una URL existente.
# Todos los campos son opcionales, ya que una actualización puede ser parcial.
class UrlUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    priority: Optional[int] = Field(
        default=None, ge=1, le=10, description="Prioridad de scraping (1-10)"
    )
    config_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    status: Optional[str] = (
        None  # Permitir actualizar el estado (quizás con validación específica)
    )

    @field_validator("status")
    def status_must_be_valid(cls, v):
        if v is not None and v not in ("pending", "in_progress", "success", "failed"):
            raise ValueError(
                "El estado debe ser uno de: 'pending', 'in_progress', 'success', 'failed'"
            )
        return v


# --- Read Schema (o Schema in DB) ---
# Schema utilizado para devolver datos de la URL desde la API.
# Incluye campos que están en la base de datos, como id y timestamps.
# Hereda de UrlBase para obtener url, priority, config_id, job_id.
class UrlRead(UrlBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    last_scraped_at: Optional[datetime] = None

    # Configuración para permitir crear este schema desde un objeto ORM (SQLAlchemy model)
    # Para Pydantic V2:
    model_config = {"from_attributes": True}
    # Para Pydantic V1 (si usas una versión anterior):
    # class Config:
    #     orm_mode = True
