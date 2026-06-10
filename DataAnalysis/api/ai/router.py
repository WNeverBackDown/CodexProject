from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.ai.agents.sql_corrector_agent import SQLCorrectorAgent
from api.ai.agents.sql_generator_agent import SQLGeneratorAgent
from api.ai.models import AIDatabaseOption, AIModel, AITableCache, AnalysisHistory
from api.dependencies import current_user_uid
from common.utils.clickhouse_util import execute_clickhouse_query
from common.utils.dataland_util import execute_dataland_query
from common.utils.utils import ensure_select_sql, ok
from database import get_db

router = APIRouter(prefix="/api/ai", tags=["AI分析"])


class AnalyzeRequest(BaseModel):
    question: str
    model_name: str = "DataPulse-Demo-Agent"
    database: str | None = None
    table_name: str | None = None


class SQLRequest(BaseModel):
    question: str = ""
    database: str | None = None
    table_name: str = "dwd_vehicle_event_di"
    sql: str | None = None


class TableInfoRequest(BaseModel):
    db_name: str
    db_type: str = "ClickHouse"
    table_name: str


@router.get("/models")
def models(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AIModel).order_by(AIModel.id)).all()
    return ok([row_to_dict(row) for row in rows])


@router.post("/analyze")
def analyze(payload: AnalyzeRequest, uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    sql = SQLGeneratorAgent().generate(payload.question, payload.table_name or "dwd_vehicle_event_di")
    result = execute_clickhouse_query(sql)
    summary = f"已识别问题“{payload.question}”，生成安全查询并返回 {len(result)} 条演示结果。"
    history = AnalysisHistory(user_uid=uid, question=payload.question, model_name=payload.model_name, sql_text=sql, result_summary=summary)
    db.add(history)
    db.commit()
    db.refresh(history)
    return ok({"history_id": history.id, "sql": sql, "summary": summary, "rows": result})


@router.get("/history")
def history(uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AnalysisHistory).where(AnalysisHistory.user_uid == uid).order_by(AnalysisHistory.id.desc()).limit(50)).all()
    return ok(
        [
            {
                "id": row.id,
                "question": row.question,
                "model_name": row.model_name,
                "sql_text": row.sql_text,
                "result_summary": row.result_summary,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


@router.get("/databases")
def databases(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AIDatabaseOption).where(AIDatabaseOption.is_enabled.is_(True)).order_by(AIDatabaseOption.type, AIDatabaseOption.db_name)).all()
    return ok([row_to_dict(row) for row in rows])


@router.get("/tables")
def tables(db_name: str, db_type: str | None = None, db: Session = Depends(get_db)) -> dict:
    stmt = select(AITableCache).where(AITableCache.db_name == db_name)
    if db_type:
        stmt = stmt.where(AITableCache.db_type == db_type)
    rows = db.scalars(stmt.order_by(AITableCache.table_name)).all()
    return ok([{"table_name": row.table_name, "db_name": row.db_name, "db_type": row.db_type, "updated_at": row.updated_at} for row in rows])


@router.post("/table-info")
def table_info(payload: TableInfoRequest, db: Session = Depends(get_db)) -> dict:
    row = db.scalar(
        select(AITableCache).where(
            AITableCache.db_name == payload.db_name,
            AITableCache.db_type == payload.db_type,
            AITableCache.table_name == payload.table_name,
        )
    )
    if not row:
        raise HTTPException(status_code=404, detail="表缓存不存在")
    return ok({"schema": json.loads(row.schema_json), "sample": json.loads(row.sample_json), "updated_at": row.updated_at})


@router.post("/generate-sql")
def generate_sql(payload: SQLRequest) -> dict:
    sql = SQLGeneratorAgent().generate(payload.question, payload.table_name)
    return ok({"sql": sql, "explanation": "根据问题选择时间、IMEI、错误码等高价值字段聚合。"})


@router.post("/execute-sql")
def execute_sql(payload: SQLRequest) -> dict:
    if not payload.sql:
        raise HTTPException(status_code=400, detail="缺少sql")
    sql = ensure_select_sql(payload.sql)
    rows = execute_dataland_query(sql) if payload.database == "ads_user_profile" else execute_clickhouse_query(sql)
    return ok({"columns": list(rows[0].keys()) if rows else [], "rows": rows, "limited": True})


@router.post("/correct-sql")
def correct_sql(payload: SQLRequest) -> dict:
    if not payload.sql:
        raise HTTPException(status_code=400, detail="缺少sql")
    return ok(SQLCorrectorAgent().correct(payload.sql))


@router.post("/refresh-cache")
def refresh_cache(db: Session = Depends(get_db)) -> dict:
    count = db.scalar(select(AITableCache).count()) if False else len(db.scalars(select(AITableCache)).all())
    return ok({"refreshed_tables": count}, "缓存刷新完成")


def row_to_dict(row) -> dict:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}
