from __future__ import annotations


class DrillDownAgent:
    def recommend(self, fields: list[str]) -> list[dict[str, str]]:
        candidates = ["error_code", "domain", "imei", "event_name", "dt"]
        return [
            {"field": field, "reason": "适合做分布、趋势或异常定位", "next_step": f"按 {field} 聚合并观察长尾"}
            for field in candidates
            if field in fields
        ]
