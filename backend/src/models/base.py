import uuid
from datetime import datetime
from typing import Any, TypeAlias, Literal

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel

IncEx: TypeAlias = set[int] | set[str] | dict[int, Any] | dict[str, Any] | None


class BaseSQLModel(SQLModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        arbitrary_types_allowed=True,
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        context: Any | None = None,
        by_alias: bool = False,
        # Set this to True by default
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        return self.__pydantic_serializer__.to_python(
            self,
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        context: Any | None = None,
        # set this by True to default to camelCase
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> str:
        return self.__pydantic_serializer__.to_json(
            self,
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        ).decode()


class BaseDatabaseModel(SQLModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, from_attributes=True, extra="ignore"
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    is_active: bool = True
