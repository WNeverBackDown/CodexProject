# DataPulse 大数据AI分析系统

基于 FastAPI + SQLAlchemy + Vue 3 + Element Plus + Vite 的大数据 AI 分析平台。

## 已实现模块

- 4A 兼容登录演示、用户信息同步与菜单接口
- 基础看板、KPI、趋势、模型健康和规则动态
- AI 分析、多模型管理、分析历史、数据库/表缓存、SQL 生成/执行/纠错
- 下钻分析、字段分布、智能推荐、会话保存
- 链式规则、多步骤 SQL、执行历史、步骤记录、分化记录
- 用户画像、行为配置、IMEI 监控、画像聚合
- 报告推送、通用机器人协议、飞书/钉钉/企业微信风格 payload 兼容预览、推送历史
- MCP 服务管理，内置诺亚缺陷管理兼容演示客户端

## 环境

后端使用你指定的 Python：

```powershell
D:\Anaconda\envs\py312\python.exe -m pip install -r requirements.txt
D:\Anaconda\envs\py312\python.exe main.py
```

前端依赖安装在项目目录下：

```powershell
cd frontend
npm install
npm run dev
```

也可以直接双击：

- `start_backend.bat`
- `start_frontend.bat`

## 配置

默认 `DATAPULSE_ENV=development` 使用 SQLite：`datapulse_dev.db`。

生产环境可切换 MySQL：

```powershell
set DATAPULSE_ENV=production
set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=datapulse
set DB_USER=datapulse
set DB_PASSWORD=your_password
set SECRET_KEY=your_secret_key
set APP_SECRET=your_app_secret
```

也可以直接设置 `DATABASE_URL`，例如：

```text
mysql+pymysql://user:password@host:3306/datapulse?charset=utf8mb4
```

## 访问

- 后端 API：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- 前端页面：http://localhost:5173

开发环境会自动创建表并写入演示数据。缺失的外部系统（4A、ClickHouse、Hive、真实 MCP、AI 模型）均提供兼容演示实现，后续可按同名工具类替换为真实连接。

## 报告推送

报告模块位于 `api/reports/` 和 `frontend/src/views/ReportPushView.vue`。

当前先实现“机器人账号推送到用户聊天界面”的兼容层：

- `generic`：通用 JSON 机器人协议，适合内部自研平台。
- `feishu`：飞书机器人消息结构风格。
- `dingtalk`：钉钉机器人消息结构风格。
- `wecom`：企业微信机器人消息结构风格。

默认通道为 `dry_run=true`，只生成请求结构并写入推送历史，不会真实发送。平台确定后，在“报告推送”页面新增通道，填入 webhook、认证方式和密钥，并关闭 dry-run 即可真实发送。
