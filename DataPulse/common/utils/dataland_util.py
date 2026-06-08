from __future__ import annotations

from common.utils.utils import ensure_select_sql


def execute_dataland_query(sql: str) -> list[dict[str, object]]:
    ensure_select_sql(sql)
    return [
        {"domain": "车联网", "active_users": 48210, "risk_score": 72},
        {"domain": "移动互联", "active_users": 93118, "risk_score": 44},
    ]
