from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dashboard.models import DashboardData, DashboardMetric
from common.utils.utils import ok
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["基础看板"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    metrics = db.scalars(select(DashboardMetric).order_by(DashboardMetric.id)).all()
    trend = db.scalars(select(DashboardData).where(DashboardData.category == "trend").order_by(DashboardData.id)).all()
    domains = db.scalars(select(DashboardData).where(DashboardData.category == "domain").order_by(DashboardData.value.desc())).all()
    return ok(
        {
            "metrics": [
                {"code": m.code, "name": m.name, "value": m.value, "unit": m.unit, "trend": m.trend, "status": m.status}
                for m in metrics
            ],
            "trend": [serialize_data(row) for row in trend],
            "domains": [serialize_data(row) for row in domains],
            "ai_insights": [
                "车联网投屏失败在 06-03 出现短时升高，建议按 error_code 下钻。",
                "AI SQL 生成成功率保持在 96% 以上，RuleGuard-Mini 延迟最低。",
                "高危 IMEI 监控命中 1 个重点投诉用户，已关联用户画像。",
            ],
        }
    )


@router.get("/statistics")
def statistics(db: Session = Depends(get_db)) -> dict:
    domain_rows = db.scalars(select(DashboardData).where(DashboardData.category == "domain")).all()
    return ok(
        {
            "domain_rank": [serialize_data(row) for row in domain_rows],
            "model_health": [
                {"name": "DataPulse-Demo-Agent", "success": 96.7, "latency": 280},
                {"name": "DeepInsight-Compatible", "success": 94.2, "latency": 520},
                {"name": "RuleGuard-Mini", "success": 91.5, "latency": 180},
            ],
            "rule_timeline": [
                {"time": "09:10", "name": "车机投屏失败链路排查", "status": "success"},
                {"time": "11:30", "name": "画像标签刷新", "status": "running"},
                {"time": "14:00", "name": "高危异常分化执行", "status": "warning"},
            ],
        }
    )


def serialize_data(row: DashboardData) -> dict:
    return {"label": row.label, "value": row.value, "payload": json.loads(row.payload or "{}")}
