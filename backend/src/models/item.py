from datetime import datetime
import uuid

from src.models.base import BaseDatabaseModel, BaseSQLModel
from sqlalchemy import Column, Text
from sqlmodel import Field


class ItemBase(BaseSQLModel):
    title: str
    description: str


class Item(ItemBase, BaseDatabaseModel, table=True):
    title: str = Field(sa_column=Column(Text, unique=True))


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: uuid.UUID
    is_active: bool
    updated: datetime


class ItemUpdate(ItemBase):
    description: str | None = None
    is_active: bool | None = None
    title: str | None = None
