import uuid

from src.api.schemas.base import BaseAPISchema
from pydantic import BaseModel


class ItemResponse(BaseAPISchema):
    id: uuid.UUID
    title: str
    description: str
    is_active: bool


class ItemRequestCreate(BaseAPISchema):
    title: str
    description: str


class ItemRequestUpdate(BaseAPISchema):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None
