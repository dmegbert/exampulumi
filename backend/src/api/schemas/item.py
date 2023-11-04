import uuid

from pydantic import BaseModel


class ItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
