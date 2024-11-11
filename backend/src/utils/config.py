import secrets
from typing import Any, List, Optional

from pydantic import (
    AnyHttpUrl,
    PostgresDsn,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


# noinspection PyNestedDecorators
class Settings(BaseSettings):
    PROJECT_NAME: str = "Exampulumi"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ENV_NAME: str = "local"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        postgres_dsn = PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=values.data.get("POSTGRES_DB"),
        )
        return postgres_dsn.unicode_string()

    AWS_LAMBDA_INITIALIZATION_TYPE: str = "Not a lambda"


settings = Settings()
