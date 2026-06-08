from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.utils.utils import utc_now
from database import Base


class BehaviorConfig(Base):
    __tablename__ = "portrait_behavior_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[str] = mapped_column(String(128), index=True)
    db_name: Mapped[str] = mapped_column(String(128))
    sql_template: Mapped[str] = mapped_column(Text)
    fields_json: Mapped[str] = mapped_column(Text)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)


class MonitorIMEI(Base):
    __tablename__ = "portrait_monitor_imei"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    imei: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(255))
    config_ids: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)
