from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.ai.models import AIDatabaseOption
from api.user_portrait.behavior_config.models import BehaviorConfig, MonitorIMEI
from api.user_portrait.user_behavior.models import UserBehaviorData
from common.utils.utils import ok
from database import get_db

router = APIRouter(prefix="/api/user-portrait", tags=["用户画像"])


class BehaviorConfigPayload(BaseModel):
    name: str
    domain: str
    db_name: str
    sql_template: str
    fields: list[str] = Field(default_factory=list)
    is_enabled: bool = True


class ImeiPayload(BaseModel):
    imei: str
    label: str
    config_ids: list[int] = Field(default_factory=list)
    status: str = "active"


@router.get("/behavior-config")
def behavior_configs(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(BehaviorConfig).order_by(BehaviorConfig.id.desc())).all()
    return ok([serialize_config(row) for row in rows])


@router.get("/behavior-config/{config_id}")
def behavior_config(config_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(BehaviorConfig, config_id)
    if not row:
        raise HTTPException(status_code=404, detail="配置不存在")
    return ok(serialize_config(row))


@router.post("/behavior-config")
def create_behavior_config(payload: BehaviorConfigPayload, db: Session = Depends(get_db)) -> dict:
    row = BehaviorConfig(name=payload.name, domain=payload.domain, db_name=payload.db_name, sql_template=payload.sql_template, fields_json=json.dumps(payload.fields, ensure_ascii=False), is_enabled=payload.is_enabled)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(serialize_config(row), "配置已创建")


@router.put("/behavior-config/{config_id}")
def update_behavior_config(config_id: int, payload: BehaviorConfigPayload, db: Session = Depends(get_db)) -> dict:
    row = db.get(BehaviorConfig, config_id)
    if not row:
        raise HTTPException(status_code=404, detail="配置不存在")
    row.name = payload.name
    row.domain = payload.domain
    row.db_name = payload.db_name
    row.sql_template = payload.sql_template
    row.fields_json = json.dumps(payload.fields, ensure_ascii=False)
    row.is_enabled = payload.is_enabled
    db.commit()
    return ok(serialize_config(row), "配置已更新")


@router.delete("/behavior-config/{config_id}")
def delete_behavior_config(config_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(BehaviorConfig, config_id)
    if row:
        db.delete(row)
        db.commit()
    return ok(message="配置已删除")


@router.get("/behavior-config/databases/list")
def database_options(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AIDatabaseOption).order_by(AIDatabaseOption.db_name)).all()
    return ok([{"db_name": row.db_name, "type": row.type, "description": row.description} for row in rows])


@router.get("/behavior-config/domains/list")
def domains(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(BehaviorConfig.domain).distinct()).all()
    return ok(rows or ["车联网", "移动互联", "智能座舱"])


@router.get("/monitor-imei")
def imeis(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(MonitorIMEI).order_by(MonitorIMEI.id.desc())).all()
    return ok([serialize_imei(row) for row in rows])


@router.get("/monitor-imei/{imei_id}")
def imei_detail(imei_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(MonitorIMEI, imei_id)
    if not row:
        raise HTTPException(status_code=404, detail="IMEI不存在")
    return ok(serialize_imei(row))


@router.post("/monitor-imei")
def create_imei(payload: ImeiPayload, db: Session = Depends(get_db)) -> dict:
    row = MonitorIMEI(imei=payload.imei, label=payload.label, config_ids=",".join(map(str, payload.config_ids)), status=payload.status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(serialize_imei(row), "IMEI已创建")


@router.put("/monitor-imei/{imei_id}")
def update_imei(imei_id: int, payload: ImeiPayload, db: Session = Depends(get_db)) -> dict:
    row = db.get(MonitorIMEI, imei_id)
    if not row:
        raise HTTPException(status_code=404, detail="IMEI不存在")
    row.imei = payload.imei
    row.label = payload.label
    row.config_ids = ",".join(map(str, payload.config_ids))
    row.status = payload.status
    db.commit()
    return ok(serialize_imei(row), "IMEI已更新")


@router.delete("/monitor-imei/{imei_id}")
def delete_imei(imei_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(MonitorIMEI, imei_id)
    if row:
        db.delete(row)
        db.commit()
    return ok(message="IMEI已删除")


@router.post("/monitor-imei/execute")
def execute_imei(payload: ImeiPayload, db: Session = Depends(get_db)) -> dict:
    data = UserBehaviorData(imei=payload.imei, domain="车联网", behavior_name="实时监控执行", payload_json=json.dumps({"configs": payload.config_ids, "hit": True}, ensure_ascii=False), risk_level="medium")
    db.add(data)
    db.commit()
    return ok({"imei": payload.imei, "generated_behavior_id": data.id}, "执行完成")


def serialize_config(row: BehaviorConfig) -> dict:
    return {"id": row.id, "name": row.name, "domain": row.domain, "db_name": row.db_name, "sql_template": row.sql_template, "fields": json.loads(row.fields_json or "[]"), "is_enabled": row.is_enabled}


def serialize_imei(row: MonitorIMEI) -> dict:
    return {"id": row.id, "imei": row.imei, "label": row.label, "config_ids": [int(x) for x in row.config_ids.split(",") if x], "status": row.status, "created_at": row.created_at}
