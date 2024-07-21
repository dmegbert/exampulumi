from typing import Generator

import pytest
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlmodel import Session

from src import crud, models
from src.api.deps import get_session
from src.main import app
from src.models.base import BaseDatabaseModel
from src.tests.factories.base_factory import BaseFactory

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@test_db:5432/app"


# SQLAlchemy transaction code example:
# https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2
@pytest.fixture
def engine() -> Engine:
    return create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)


@pytest.fixture
def tables(engine) -> Generator[None, None, None]:
    BaseDatabaseModel.metadata.create_all(engine)
    yield
    BaseDatabaseModel.metadata.drop_all(engine)


@pytest.fixture(name="db")
def dbsession(
    engine: Engine, tables: Generator[None, None, None]
) -> Generator[Session, None, None]:
    """Returns a sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection, autoflush=True)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


# register all factories example:
# https://github.com/tiangolo/sqlmodel/discussions/615#discussioncomment-6395112
@pytest.fixture(autouse=True)
def register_factories(db: Session) -> None:
    for factory in BaseFactory.__subclasses__():
        factory._meta.sqlalchemy_session = db


@pytest.fixture(name="client")
def api_client_fixture(db: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return db

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
