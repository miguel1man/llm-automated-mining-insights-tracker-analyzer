import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobBase(BaseModel):
    schedule_id: Optional[uuid.UUID] = Field(
        None, description="ID de la programación asociada (si existe)"
    )
    status: Optional[str] = Field(
        default="pending",
        description="Estado actual del trabajo ('pending', 'running', 'completed', 'failed')",
    )


class JobCreate(JobBase):
    # Al crear un job, quizás solo necesitemos el schedule_id (o ni eso si se crea manualmente)
    # Los contadores y timestamps se inicializan por defecto o en la lógica de negocio
    pass


class JobUpdate(BaseModel):
    finished_at: Optional[datetime] = None
    total_urls: Optional[int] = Field(default=None, ge=0)
    success_count: Optional[int] = Field(default=None, ge=0)
    error_count: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = Field(default=None, description="Nuevo estado del trabajo")
    # No permitir actualizar schedule_id o started_at usualmente


class JobRead(JobBase):
    id: uuid.UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    total_urls: int
    success_count: int
    error_count: int
    status: str  # En lectura, el status no es opcional

    model_config = {"from_attributes": True}
