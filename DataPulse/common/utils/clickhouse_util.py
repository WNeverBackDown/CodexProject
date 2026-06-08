from __future__ import annotations

from common.utils.utils import ensure_select_sql


def execute_clickhouse_query(sql: str) -> list[dict[str, object]]:
    ensure_select_sql(sql)
    return [
        {"dt": "2026-06-01", "uv": 128430, "error_rate": 0.014, "source": "clickhouse-demo"},
        {"dt": "2026-06-02", "uv": 134912, "error_rate": 0.011, "source": "clickhouse-demo"},
    ]
