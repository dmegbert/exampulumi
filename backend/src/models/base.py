import uuid
from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, from_attributes=True, extra="ignore"
    )


class BaseDatabaseModel(SQLModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, from_attributes=True, extra="ignore"
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    is_active: bool = True
