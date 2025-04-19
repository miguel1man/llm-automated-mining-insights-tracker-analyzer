import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ConfigBase(BaseModel):
    site_name: str = Field(
        ..., description="Nombre descriptivo del sitio o configuración"
    )
    selectors: Dict[str, Any] = Field(
        ..., description="Diccionario JSON con los selectores CSS/XPath"
    )


class ConfigCreate(ConfigBase):
    pass  # Solo necesita site_name y selectors


class ConfigUpdate(BaseModel):
    # Solo permite actualizar los campos que quedan
    site_name: Optional[str] = None
    selectors: Optional[Dict[str, Any]] = None


class ConfigRead(ConfigBase):
    # Muestra los campos que quedan más los generados por la DB
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # Los campos retry_interval, max_retries, auth_settings no se leerán desde Python,
    # pero existirán en la base de datos con sus valores DEFAULT.

    model_config = {"from_attributes": True}
