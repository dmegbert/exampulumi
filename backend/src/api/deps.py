from typing import Generator

from fastapi.security import HTTPBearer
from sqlmodel import Session

from src.models.session import sqlmodel_engine

# This just enables auth on the interactive api docs
oauth2_scheme = HTTPBearer(
    auto_error=False,
)


def get_session() -> Generator:  # pragma: no cover - tested implicitly
    with Session(sqlmodel_engine) as session:
        yield session
