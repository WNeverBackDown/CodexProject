from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.utils.utils import utc_now
from database import Base


class ReportChannel(Base):
    __tablename__ = "report_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="generic")
    robot_name: Mapped[str] = mapped_column(String(128), default="DataPulseBot")
    webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_type: Mapped[str] = mapped_column(String(32), default="none")
    secret_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    headers_json: Mapped[str] = mapped_column(Text, default="{}")
    payload_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)


class ReportPushHistory(Base):
    __tablename__ = "report_push_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    channel_name: Mapped[str] = mapped_column(String(128))
    provider: Mapped[str] = mapped_column(String(32), default="generic")
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    recipients_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    request_json: Mapped[str] = mapped_column(Text, default="{}")
    response_json: Mapped[str] = mapped_column(Text, default="{}")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(64), default="demo-admin")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)
