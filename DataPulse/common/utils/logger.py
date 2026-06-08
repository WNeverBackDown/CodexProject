from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from config_env import settings


def build_logger() -> logging.Logger:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("datapulse")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.env == "development" else logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] [%(user)s] %(message)s")

    class UserFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "user"):
                record.user = "未登录"
            return True

    logger.addFilter(UserFilter())

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    app_file = TimedRotatingFileHandler(settings.log_dir / "datapulse.log", when="midnight", backupCount=30, encoding="utf-8")
    app_file.setFormatter(formatter)
    logger.addHandler(app_file)

    error_file = TimedRotatingFileHandler(settings.log_dir / "error.log", when="midnight", backupCount=30, encoding="utf-8")
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(formatter)
    logger.addHandler(error_file)
    return logger


logger = build_logger()
