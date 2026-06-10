# MCP 服务管理

当前内置 `NoahDefectClient` 的兼容演示实现。生产环境可以在 `common/mcp/base_client.py`
中替换为真实 HTTP、stdio 或 SSE MCP 客户端。

```python
from common.mcp import NoahDefectClient

client = NoahDefectClient()
defect = client.query_defect_detail(defect_id="12345")
client.add_defect_label(defect_id="12345", label="埋点大数据监控")
```
