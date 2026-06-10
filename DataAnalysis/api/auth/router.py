from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth.models import User
from api.dependencies import current_user_uid
from common.utils.utils import ok, utc_now
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.get("/login")
def login() -> dict:
    return ok({"login_url": "/api/auth/callback?uid=demo-admin", "mode": "4A-demo"}, "开发环境已启用4A兼容登录")


@router.get("/callback")
def callback(uid: str = "demo-admin", db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.uid == uid))
    if user:
        user.last_login_at = utc_now()
        db.commit()
    return ok({"uid": uid, "token": f"demo-token-{uid}"}, "登录成功")


@router.get("/logout")
def logout() -> dict:
    return ok(message="已登出")


@router.get("/check")
def check(uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.uid == uid)) or db.scalar(select(User).limit(1))
    return ok({"is_login": True, "user": serialize_user(user)})


@router.get("/menu")
def menu() -> dict:
    items = [
        {"path": "/", "name": "总览", "icon": "LayoutDashboard"},
        {"path": "/ai", "name": "AI分析", "icon": "Bot"},
        {"path": "/drill-down", "name": "下钻分析", "icon": "GitBranch"},
        {"path": "/rules", "name": "链式规则", "icon": "Workflow"},
        {"path": "/portrait", "name": "用户画像", "icon": "UserRoundSearch"},
        {"path": "/reports", "name": "报告推送", "icon": "FileText"},
        {"path": "/mcp", "name": "MCP服务", "icon": "ServerCog"},
        {"path": "/users", "name": "用户管理", "icon": "Users"},
    ]
    return ok(items)


@router.get("/users")
def list_users(db: Session = Depends(get_db)) -> dict:
    users = db.scalars(select(User).order_by(User.id)).all()
    return ok([serialize_user(user) for user in users])


def serialize_user(user: User | None) -> dict:
    if not user:
        return {}
    return {
        "id": user.id,
        "uid": user.uid,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "department": user.department,
        "is_active": user.is_active,
        "last_login_at": user.last_login_at,
    }
