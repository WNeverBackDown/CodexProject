from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.user_portrait.user_behavior.models import UserBehaviorData
from common.utils.utils import ok
from database import get_db

router = APIRouter(prefix="/api/user-portrait/user-behavior", tags=["用户行为"])


@router.get("/data")
def data(imei: str | None = None, db: Session = Depends(get_db)) -> dict:
    stmt = select(UserBehaviorData).order_by(UserBehaviorData.id.desc())
    if imei:
        stmt = stmt.where(UserBehaviorData.imei == imei)
    rows = db.scalars(stmt).all()
    return ok([serialize(row) for row in rows])


@router.get("/data/{data_id}")
def detail(data_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(UserBehaviorData, data_id)
    if not row:
        raise HTTPException(status_code=404, detail="行为数据不存在")
    return ok(serialize(row))


@router.get("/user-profile")
def user_profile(imei: str | None = None, db: Session = Depends(get_db)) -> dict:
    stmt = select(UserBehaviorData)
    if imei:
        stmt = stmt.where(UserBehaviorData.imei == imei)
    rows = db.scalars(stmt).all()
    domains: dict[str, dict] = {}
    for row in rows:
        bucket = domains.setdefault(row.domain, {"domain": row.domain, "behaviors": [], "risk": "low"})
        bucket["behaviors"].append(serialize(row))
        if row.risk_level in {"high", "critical"}:
            bucket["risk"] = row.risk_level
    return ok({"imei": imei or "全部", "domains": list(domains.values())})


def serialize(row: UserBehaviorData) -> dict:
    return {"id": row.id, "imei": row.imei, "domain": row.domain, "behavior_name": row.behavior_name, "payload": json.loads(row.payload_json or "{}"), "risk_level": row.risk_level, "created_at": row.created_at}
