from __future__ import annotations

from common.mcp.base_client import MCPBaseClient


class NoahDefectClient(MCPBaseClient):
    service_key = "noah-defect"

    def query_defect_detail(self, defect_id: str) -> dict[str, object]:
        return {
            "defect_id": defect_id,
            "title": "埋点大数据监控异常",
            "severity": "P1",
            "status": "处理中",
            "owner": "DataPulse",
        }

    def add_defect_label(self, defect_id: str, label: str) -> dict[str, object]:
        return {"defect_id": defect_id, "label": label, "applied": True}
