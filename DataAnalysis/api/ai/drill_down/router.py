from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.ai.agents.drill_down_agent import DrillDownAgent
from api.ai.agents.sql_generator_agent import SQLGeneratorAgent
from api.ai.drill_down.models import DrillDownSession
from api.ai.models import AITableCache
from api.dependencies import current_user_uid
from common.utils.utils import ok, stable_id, utc_now
from database import get_db

router = APIRouter(prefix="/api/ai/drill-down", tags=["下钻分析"])


class DrillRequest(BaseModel):
    db_name: str = "dwd_vehicle_event"
    db_type: str = "ClickHouse"
    table_name: str = "dwd_vehicle_event_di"
    field: str | None = None
    question: str = ""
    state: dict = Field(default_factory=dict)


class SessionRequest(DrillRequest):
    title: str = "未命名下钻会话"


@router.post("/analyze-distribution")
def analyze_distribution(payload: DrillRequest) -> dict:
    field = payload.field or "error_code"
    values = [
        {"value": "E102", "count": 1240, "ratio": 0.42},
        {"value": "E201", "count": 680, "ratio": 0.23},
        {"value": "0", "count": 590, "ratio": 0.20},
        {"value": "OTHER", "count": 440, "ratio": 0.15},
    ]
    return ok({"field": field, "values": values, "insight": f"{field} 存在明显头部集中，可继续按 IMEI 与 dt 交叉分析。"})


@router.post("/analyze")
def analyze(payload: DrillRequest, db: Session = Depends(get_db)) -> dict:
    cache = db.scalar(select(AITableCache).where(AITableCache.table_name == payload.table_name))
    fields = [item["name"] for item in json.loads(cache.schema_json)] if cache else ["dt", "domain", "imei", "event_name", "error_code", "cnt"]
    return ok({"focus_fields": fields[:5], "recommendations": DrillDownAgent().recommend(fields)})


@router.post("/generate-sql")
def generate_sql(payload: DrillRequest) -> dict:
    sql = SQLGeneratorAgent().generate(payload.question or f"分析 {payload.field or 'error_code'}", payload.table_name)
    return ok({"sql": sql, "next_actions": ["执行SQL", "分析异常", "保存会话"]})


@router.post("/analyze-anomalies")
def analyze_anomalies(payload: DrillRequest) -> dict:
    return ok(
        {
            "level": "warning",
            "summary": "E102 在车联网领域占比高于近7日均值 31%，建议检查投屏初始化链路。",
            "evidence": [{"field": "error_code", "value": "E102", "score": 0.87}],
        }
    )


@router.post("/save-session")
def save_session(payload: SessionRequest, uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    key = stable_id(f"{uid}:{payload.title}:{payload.table_name}:{utc_now().isoformat()}")
    session = DrillDownSession(
        session_key=key,
        user_uid=uid,
        title=payload.title,
        db_name=payload.db_name,
        table_name=payload.table_name,
        state_json=json.dumps(payload.state, ensure_ascii=False),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return ok(serialize(session), "会话已保存")


@router.get("/sessions")
def sessions(uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(DrillDownSession).where(DrillDownSession.user_uid == uid).order_by(DrillDownSession.id.desc())).all()
    return ok([serialize(row) for row in rows])


@router.get("/session/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(DrillDownSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return ok(serialize(row))


@router.put("/session/{session_id}")
def update_session(session_id: int, payload: SessionRequest, db: Session = Depends(get_db)) -> dict:
    row = db.get(DrillDownSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    row.title = payload.title
    row.state_json = json.dumps(payload.state, ensure_ascii=False)
    row.updated_at = utc_now()
    db.commit()
    return ok(serialize(row), "会话已更新")


@router.delete("/session/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(DrillDownSession, session_id)
    if row:
        db.delete(row)
        db.commit()
    return ok(message="会话已删除")


def serialize(row: DrillDownSession) -> dict:
    return {
        "id": row.id,
        "session_key": row.session_key,
        "title": row.title,
        "db_name": row.db_name,
        "table_name": row.table_name,
        "state": json.loads(row.state_json or "{}"),
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
