from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config_env import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import api.auth.models  # noqa: F401
    import api.dashboard.models  # noqa: F401
    import api.ai.models  # noqa: F401
    import api.ai.drill_down.models  # noqa: F401
    import api.rules.chain.models  # noqa: F401
    import api.reports.models  # noqa: F401
    import api.user_portrait.behavior_config.models  # noqa: F401
    import api.user_portrait.user_behavior.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
