from __future__ import annotations


class SQLGeneratorAgent:
    def generate(self, question: str, table_name: str = "dwd_vehicle_event_di") -> str:
        lower = question.lower()
        if "错误" in question or "失败" in question or "error" in lower:
            return f"select error_code, sum(cnt) as cnt from {table_name} group by error_code order by cnt desc limit 20"
        if "imei" in lower or "用户" in question:
            return f"select imei, sum(cnt) as cnt from {table_name} group by imei order by cnt desc limit 20"
        return f"select dt, sum(cnt) as cnt from {table_name} group by dt order by dt desc limit 30"
