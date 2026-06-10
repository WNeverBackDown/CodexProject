from __future__ import annotations

from fastapi import Header


def current_user_uid(x_user_uid: str | None = Header(default=None)) -> str:
    return x_user_uid or "demo-admin"
