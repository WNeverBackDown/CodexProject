from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def stable_id(value: str, length: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def ensure_select_sql(sql: str) -> str:
    normalized = sql.strip().rstrip(";")
    if not re.match(r"^(select|with)\b", normalized, flags=re.IGNORECASE):
        raise ValueError("仅允许执行 SELECT/WITH 查询")
    forbidden = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|replace|grant|revoke)\b", re.IGNORECASE)
    if forbidden.search(normalized):
        raise ValueError("查询包含不允许的写入或结构变更关键字")
    return normalized


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def fail(message: str, data: Any = None) -> dict[str, Any]:
    return {"success": False, "message": message, "data": data}
