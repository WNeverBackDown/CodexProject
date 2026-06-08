from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from common.mcp import NoahDefectClient
from common.mcp.config import MCP_SERVICES
from common.utils.utils import ok

router = APIRouter(prefix="/api/mcp", tags=["MCP服务"])


class DefectPayload(BaseModel):
    defect_id: str
    label: str | None = None


@router.get("/services")
def services() -> dict:
    return ok([{"key": key, **value} for key, value in MCP_SERVICES.items()])


@router.post("/noah-defect/query")
def query_defect(payload: DefectPayload) -> dict:
    return ok(NoahDefectClient().query_defect_detail(payload.defect_id))


@router.post("/noah-defect/label")
def label_defect(payload: DefectPayload) -> dict:
    return ok(NoahDefectClient().add_defect_label(payload.defect_id, payload.label or "埋点大数据监控"))
