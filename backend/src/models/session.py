import sqlmodel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.utils.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sqlmodel_engine = sqlmodel.create_engine(
    settings.SQLALCHEMY_DATABASE_URI, echo=False, pool_pre_ping=True
)
