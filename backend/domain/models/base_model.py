from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from datetime import datetime

# Define una convención de nombres para índices y constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata
    # Ejemplo si tuvieras un ID común aquí:
    # id: Mapped[int] = mapped_column(primary_key=True)
    # created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
