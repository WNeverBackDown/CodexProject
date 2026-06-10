from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.utils.utils import utc_now
from database import Base


class ChainRule(Base):
    __tablename__ = "rules_chain"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_uid: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    schedule_cron: Mapped[str | None] = mapped_column(String(64), nullable=True)
    split_field: Mapped[str | None] = mapped_column(String(128), nullable=True)
    steps_json: Mapped[str] = mapped_column(Text)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)


class ChainRuleHistory(Base):
    __tablename__ = "rules_chain_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(32))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    affected_rows: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text)
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)


class ChainRuleStepHistory(Base):
    __tablename__ = "rules_chain_step_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, index=True)
    step_index: Mapped[int] = mapped_column(Integer)
    step_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    sql_text: Mapped[str] = mapped_column(Text)
    output_json: Mapped[str] = mapped_column(Text)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)


class ChainRuleSplitHistory(Base):
    __tablename__ = "rules_chain_split_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(Integer, index=True)
    split_value: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    payload_json: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0)
