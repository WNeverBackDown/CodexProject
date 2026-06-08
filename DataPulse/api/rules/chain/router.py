from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import current_user_uid
from api.rules.chain.executor import ChainRuleExecutor
from api.rules.chain.models import ChainRule, ChainRuleHistory, ChainRuleSplitHistory, ChainRuleStepHistory
from common.utils.clickhouse_util import execute_clickhouse_query
from common.utils.utils import ensure_select_sql, ok, utc_now
from database import get_db

router = APIRouter(prefix="/api/rules/chain", tags=["链式规则"])


class ChainRulePayload(BaseModel):
    name: str
    description: str | None = None
    status: str = "draft"
    schedule_cron: str | None = None
    split_field: str | None = None
    steps: list[dict] = Field(default_factory=list)
    is_enabled: bool = True


class ExecutePayload(BaseModel):
    rule_id: int | None = None
    steps: list[dict] = Field(default_factory=list)
    split_field: str | None = None


class SQLPayload(BaseModel):
    sql: str


@router.get("")
def list_rules(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ChainRule).order_by(ChainRule.id.desc())).all()
    return ok([serialize_rule(row) for row in rows])


@router.get("/{rule_id}")
def get_rule(rule_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(ChainRule, rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="规则不存在")
    return ok(serialize_rule(row))


@router.post("")
def create_rule(payload: ChainRulePayload, uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    row = ChainRule(
        name=payload.name,
        description=payload.description,
        owner_uid=uid,
        status=payload.status,
        schedule_cron=payload.schedule_cron,
        split_field=payload.split_field,
        steps_json=json.dumps(payload.steps, ensure_ascii=False),
        is_enabled=payload.is_enabled,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(serialize_rule(row), "规则已创建")


@router.put("/{rule_id}")
def update_rule(rule_id: int, payload: ChainRulePayload, db: Session = Depends(get_db)) -> dict:
    row = db.get(ChainRule, rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="规则不存在")
    row.name = payload.name
    row.description = payload.description
    row.status = payload.status
    row.schedule_cron = payload.schedule_cron
    row.split_field = payload.split_field
    row.steps_json = json.dumps(payload.steps, ensure_ascii=False)
    row.is_enabled = payload.is_enabled
    row.updated_at = utc_now()
    db.commit()
    return ok(serialize_rule(row), "规则已更新")


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(ChainRule, rule_id)
    if row:
        db.delete(row)
        db.commit()
    return ok(message="规则已删除")


@router.patch("/{rule_id}/status")
def update_status(rule_id: int, status: str, db: Session = Depends(get_db)) -> dict:
    row = db.get(ChainRule, rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="规则不存在")
    row.status = status
    row.updated_at = utc_now()
    db.commit()
    return ok(serialize_rule(row), "状态已更新")


@router.post("/execute")
def execute(payload: ExecutePayload, db: Session = Depends(get_db)) -> dict:
    if payload.rule_id:
        rule = db.get(ChainRule, payload.rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        steps = json.loads(rule.steps_json)
        split_field = rule.split_field
        rule_id = rule.id
    else:
        steps = payload.steps
        split_field = payload.split_field
        rule_id = 0
    return ok(ChainRuleExecutor(db).execute(rule_id, steps, split_field))


@router.post("/debug-step")
def debug_step(payload: SQLPayload) -> dict:
    sql = ensure_select_sql(payload.sql)
    return ok({"sql": sql, "rows": execute_clickhouse_query(sql), "duration_ms": 96})


@router.post("/execute-sql")
def execute_sql(payload: SQLPayload) -> dict:
    sql = ensure_select_sql(payload.sql)
    return ok({"sql": sql, "rows": execute_clickhouse_query(sql)})


@router.get("/{rule_id}/history")
def history(rule_id: int, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ChainRuleHistory).where(ChainRuleHistory.rule_id == rule_id).order_by(ChainRuleHistory.id.desc())).all()
    return ok([serialize_history(row) for row in rows])


@router.get("/history/{history_id}/steps")
def history_steps(history_id: int, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ChainRuleStepHistory).where(ChainRuleStepHistory.history_id == history_id).order_by(ChainRuleStepHistory.step_index)).all()
    return ok([serialize_step(row) for row in rows])


@router.get("/history/{history_id}/splits")
def history_splits(history_id: int, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ChainRuleSplitHistory).where(ChainRuleSplitHistory.history_id == history_id)).all()
    return ok([serialize_split(row) for row in rows])


def serialize_rule(row: ChainRule) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "owner_uid": row.owner_uid,
        "status": row.status,
        "schedule_cron": row.schedule_cron,
        "split_field": row.split_field,
        "steps": json.loads(row.steps_json or "[]"),
        "is_enabled": row.is_enabled,
        "updated_at": row.updated_at,
    }


def serialize_history(row: ChainRuleHistory) -> dict:
    return {"id": row.id, "rule_id": row.rule_id, "status": row.status, "duration_ms": row.duration_ms, "affected_rows": row.affected_rows, "summary": row.summary, "started_at": row.started_at}


def serialize_step(row: ChainRuleStepHistory) -> dict:
    return {"id": row.id, "step_index": row.step_index, "step_name": row.step_name, "status": row.status, "sql_text": row.sql_text, "output": json.loads(row.output_json or "[]"), "duration_ms": row.duration_ms}


def serialize_split(row: ChainRuleSplitHistory) -> dict:
    return {"id": row.id, "split_value": row.split_value, "status": row.status, "payload": json.loads(row.payload_json or "{}"), "score": row.score}
