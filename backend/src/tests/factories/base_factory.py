import uuid
from datetime import datetime

import factory
from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_COMMIT

    @factory.lazy_attribute
    def id(self) -> uuid.UUID:
        return uuid.uuid4()

    created: datetime | None = None
    updated: datetime | None = None
    is_active: bool = True
