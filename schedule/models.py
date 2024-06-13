from __future__ import annotations
from typing import List
from datetime import datetime, date, time

from sqlalchemy import ForeignKey, Boolean, String, DateTime, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from db_config.storage_config import (
    Base,
    intpk,
    chapter,
    affair,
    pictures,
    points,
    points_date,
    points_time,
    user_fk,
)


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    owner: Mapped[user_fk]
    st_hour: Mapped[points]
    en_hour: Mapped[points]
    hours: Mapped[time] = mapped_column(ARRAY(Time), nullable=True)
    occupied: Mapped[time] = mapped_column(ARRAY(Time), nullable=True)
    Completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[points]
    modified_at: Mapped[points]
    to_recording: Mapped[List[Recording]] = relationship()

    def __int__(self):
        return int(self.id)


class Recording(Base):
    __tablename__ = "recording"

    id: Mapped[intpk]
    owner: Mapped[user_fk]
    to_schedule: Mapped[int] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False
    )
    record_d: Mapped[points_date]
    record_h: Mapped[points_time]
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[points]
    modified_at: Mapped[points]

    def __int__(self):
        return int(self.id)
