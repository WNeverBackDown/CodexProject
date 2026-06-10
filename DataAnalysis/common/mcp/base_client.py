from __future__ import annotations

from typing import Any

from common.mcp.config import MCP_SERVICES
from common.mcp.exceptions import MCPServiceUnavailable


class MCPBaseClient:
    service_key = ""

    def __init__(self) -> None:
        if self.service_key not in MCP_SERVICES:
            raise MCPServiceUnavailable(f"未知MCP服务: {self.service_key}")

    @property
    def metadata(self) -> dict[str, Any]:
        return MCP_SERVICES[self.service_key]
