from __future__ import annotations

from datetime import datetime, date, time

from typing_extensions import Annotated

from sqlalchemy import String, Text, DateTime, Date, Time, ForeignKey

from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column

from db_config.settings import settings


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
chapter = Annotated[str, mapped_column(String(30), unique=True, index=True)]
affair = Annotated[str, mapped_column(Text, nullable=True)]
pictures = Annotated[str, mapped_column(String, nullable=True)]
# ..
points = Annotated[datetime, mapped_column(DateTime, nullable=True)]
points_date = Annotated[date, mapped_column(Date, nullable=True)]
points_time = Annotated[time, mapped_column(Time, nullable=True)]
# ..
user_fk = Annotated[
    int, mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
]
