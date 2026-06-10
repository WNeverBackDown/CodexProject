from __future__ import annotations


class SQLCorrectorAgent:
    def correct(self, sql: str) -> dict[str, str | bool]:
        fixed = sql.strip().rstrip(";")
        if " limit " not in fixed.lower():
            fixed += " limit 100"
        return {"changed": fixed != sql.strip(), "sql": fixed, "message": "已补充安全 limit 并移除结尾分号"}
