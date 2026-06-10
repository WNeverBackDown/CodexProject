from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from common.utils.utils import utc_now
from database import Base


class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    provider: Mapped[str] = mapped_column(String(64), default="local")
    capability: Mapped[str] = mapped_column(String(128), default="SQL生成,异常分析")
    latency_ms: Mapped[int] = mapped_column(Integer, default=320)
    quality_score: Mapped[float] = mapped_column(Float, default=0.92)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uid: Mapped[str] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(128))
    sql_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)


class AIDatabaseOption(Base):
    __tablename__ = "ai_database_options"
    __table_args__ = (UniqueConstraint("db_name", "type", name="uq_ai_database_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    db_name: Mapped[str] = mapped_column(String(128), index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AITableCache(Base):
    __tablename__ = "ai_table_cache"
    __table_args__ = (UniqueConstraint("db_name", "db_type", "table_name", name="uq_ai_table_cache"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    db_name: Mapped[str] = mapped_column(String(128), index=True)
    db_type: Mapped[str] = mapped_column(String(32), index=True)
    table_name: Mapped[str] = mapped_column(String(128), index=True)
    schema_json: Mapped[str] = mapped_column(Text)
    sample_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=utc_now)
