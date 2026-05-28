# CatBaby 设计方案

## 目标

CatBaby 的目标是把“优惠消息采集”和“关键词提醒”拆开。提醒核心必须本地可跑、可测试、可替换采集端；微信接入能力后续按合规方式补充。

## MVP 范围

- 本地 HTTP 服务：`127.0.0.1:8765`
- 关键词规则：启用状态、关键词、排除词
- 去重：同一规则下相同内容在配置窗口内只提醒一次
- 实时推送：Server-Sent Events
- 前端提醒：页面列表、声音、浏览器 Notification
- 输入来源：网页测试消息、`data/inbox.txt` 追加监测

## 架构

```text
采集适配器
  ├─ 文件尾随 data/inbox.txt
  └─ 手动测试 API
        │
        ▼
Message 标准结构
        │
        ▼
RuleEngine
        │
        ▼
去重与持久化
        │
        ├─ data/messages.jsonl
        ├─ data/alerts.jsonl
        └─ data/seen.json
        │
        ▼
SSE 推送到 Web 控制台
```

## 数据结构

规则配置位于 `config/rules.json`：

```json
{
  "settings": {
    "dedupe_minutes": 30,
    "max_alerts": 200
  },
  "rules": [
    {
      "id": "cat-food",
      "name": "猫粮和主食罐",
      "enabled": true,
      "terms": ["猫粮", "主食罐"],
      "exclude": ["已结束", "无货"]
    }
  ]
}
```

消息统一结构：

```json
{
  "source": "manual-test",
  "room": "猫猫购物群",
  "sender": "群友",
  "content": "主食罐限时好价 https://example.com",
  "url": "https://example.com"
}
```

## 微信接入判断

微信小程序不能读取聊天记录。直接读取或解密微信本地数据库也不适合作为项目默认路径，因为稳定性、账号风险和隐私边界都不可控。

可行的后续路线：

1. 主动转发路线：你把群消息转发到一个固定入口，入口再调用 CatBaby API。
2. 文本导入路线：定期导出或复制群消息到 `data/inbox.txt`。
3. OCR 辅助路线：本地截图识别微信 PC 窗口，只识别屏幕上可见消息，需要单独确认隐私边界。
4. 官方能力路线：如果后续有企业微信、公众号、开放平台的合规消息源，再写新适配器。

## 扩展点

- `catbaby.monitor.FileTailMonitor` 是当前采集适配器。
- 新采集端只需要生成 `Message` 并调用 `CatBabyApp.process_message`。
- 规则引擎可以继续扩展价格阈值、平台识别、链接域名白名单、静默时段。
