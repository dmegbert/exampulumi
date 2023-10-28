import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    class Config:
        arbitrary_types_allowed = True
        orm_mode = True
        read_with_orm_mode = True


class BaseDatabaseModel(SQLModel):
    class Config:
        arbitrary_types_allowed = True
        orm_mode = True
        read_with_orm_mode = True

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
    )
    created: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    is_active: bool = True
