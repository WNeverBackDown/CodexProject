from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.ai.models import AIDatabaseOption, AIModel, AITableCache
from api.auth.models import User
from api.dashboard.models import DashboardData, DashboardMetric
from api.reports.models import ReportChannel
from api.rules.chain.models import ChainRule
from api.user_portrait.behavior_config.models import BehaviorConfig, MonitorIMEI
from api.user_portrait.user_behavior.models import UserBehaviorData


def seed_demo_data(db: Session) -> None:
    ensure_default_report_channel(db)
    if db.scalar(select(User).limit(1)):
        db.commit()
        return

    db.add(
        User(
            uid="demo-admin",
            username="admin",
            display_name="演示管理员",
            email="admin@datapulse.local",
            department="大数据AI分析中心",
        )
    )
    db.add_all(
        [
            DashboardMetric(code="daily_queries", name="今日查询量", value=18240, unit="次", trend=12.4, status="success"),
            DashboardMetric(code="active_users", name="活跃用户", value=1286, unit="人", trend=7.8, status="success"),
            DashboardMetric(code="ai_success", name="AI成功率", value=96.7, unit="%", trend=2.1, status="success"),
            DashboardMetric(code="risk_events", name="高危异常", value=18, unit="个", trend=-4.2, status="warning"),
        ]
    )
    for idx, item in enumerate(
        [
            ("trend", "06-01", 120, {"uv": 128430, "errors": 140}),
            ("trend", "06-02", 138, {"uv": 134912, "errors": 118}),
            ("trend", "06-03", 142, {"uv": 148330, "errors": 211}),
            ("trend", "06-04", 155, {"uv": 151002, "errors": 166}),
            ("domain", "车联网", 48210, {"risk": 72}),
            ("domain", "移动互联", 93118, {"risk": 44}),
            ("domain", "智能座舱", 23104, {"risk": 58}),
        ],
        start=1,
    ):
        db.add(DashboardData(id=idx, category=item[0], label=item[1], value=item[2], payload=json.dumps(item[3], ensure_ascii=False)))

    db.add_all(
        [
            AIModel(name="DataPulse-Demo-Agent", provider="local", capability="SQL生成,SQL纠错,下钻推荐", latency_ms=280, quality_score=0.91),
            AIModel(name="DeepInsight-Compatible", provider="openai-compatible", capability="根因分析,自然语言总结", latency_ms=520, quality_score=0.94),
            AIModel(name="RuleGuard-Mini", provider="local", capability="规则风险识别,字段推荐", latency_ms=180, quality_score=0.86),
        ]
    )
    db.add_all(
        [
            AIDatabaseOption(db_name="dwd_vehicle_event", type="ClickHouse", description="车辆事件明细与埋点聚合"),
            AIDatabaseOption(db_name="ads_user_profile", type="Hive", description="用户画像宽表与行为标签"),
            AIDatabaseOption(db_name="app_quality_monitor", type="ClickHouse", description="APP质量与异常监控"),
        ]
    )
    table_schema = [
        {"name": "dt", "type": "String", "comment": "日期分区"},
        {"name": "domain", "type": "String", "comment": "业务领域"},
        {"name": "imei", "type": "String", "comment": "设备标识"},
        {"name": "event_name", "type": "String", "comment": "事件名"},
        {"name": "error_code", "type": "String", "comment": "错误码"},
        {"name": "cnt", "type": "UInt64", "comment": "次数"},
    ]
    sample = [
        {"dt": "2026-06-01", "domain": "车联网", "imei": "860000000000001", "event_name": "car_projection_start", "error_code": "0", "cnt": 128},
        {"dt": "2026-06-01", "domain": "车联网", "imei": "860000000000002", "event_name": "car_projection_fail", "error_code": "E102", "cnt": 7},
    ]
    db.add_all(
        [
            AITableCache(db_name="dwd_vehicle_event", db_type="ClickHouse", table_name="dwd_vehicle_event_di", schema_json=json.dumps(table_schema, ensure_ascii=False), sample_json=json.dumps(sample, ensure_ascii=False)),
            AITableCache(db_name="ads_user_profile", db_type="Hive", table_name="ads_user_profile_df", schema_json=json.dumps(table_schema, ensure_ascii=False), sample_json=json.dumps(sample, ensure_ascii=False)),
        ]
    )
    db.add(
        ChainRule(
            name="车机投屏失败链路排查",
            description="按 IMEI 聚合异常，再下钻错误码并输出缺陷标签",
            owner_uid="demo-admin",
            status="published",
            split_field="error_code",
            steps_json=json.dumps(
                [
                    {"name": "定位异常IMEI", "sql": "select imei, sum(cnt) as fail_cnt from dwd_vehicle_event_di where event_name='car_projection_fail' group by imei"},
                    {"name": "错误码分布", "sql": "select error_code, sum(cnt) as cnt from ${step1} group by error_code"},
                ],
                ensure_ascii=False,
            ),
        )
    )
    db.add_all(
        [
            BehaviorConfig(name="投屏连续失败", domain="车联网", db_name="dwd_vehicle_event", sql_template="select * from dwd_vehicle_event_di where imei=:imei", fields_json=json.dumps(["imei", "error_code", "cnt"], ensure_ascii=False)),
            MonitorIMEI(imei="860000000000001", label="重点投诉用户", config_ids="1", status="active"),
            UserBehaviorData(imei="860000000000001", domain="车联网", behavior_name="投屏失败", payload_json=json.dumps({"fail_cnt": 7, "last_error": "E102"}, ensure_ascii=False), risk_level="high"),
        ]
    )
    db.commit()


def ensure_default_report_channel(db: Session) -> None:
    exists = db.scalar(select(ReportChannel).limit(1))
    if exists:
        return
    db.add(
        ReportChannel(
            name="内部聊天机器人演示通道",
            provider="generic",
            robot_name="DataPulseBot",
            webhook_url=None,
            auth_type="none",
            headers_json="{}",
            payload_template=None,
            is_enabled=True,
            dry_run=True,
        )
    )
