# CatBaby

CatBaby 是一个本地运行的优惠关键词监测工具。当前版本不读取微信私有数据库，也不绕过微信权限；它先提供稳定的本地监测核心，后续可以接入更合规的采集来源。

它不是纯后端工具。启动后会在本机运行一个小服务，并打开浏览器控制台：

```text
http://127.0.0.1:8765
```

## 为什么不是微信小程序

微信小程序没有读取用户微信聊天记录的权限，也不能后台扫描群聊消息。手机端微信聊天数据也没有面向个人工具的实时读取接口。为了不做不稳定或有风险的逆向方案，CatBaby 采用本地服务加可替换采集适配器：

- 当前可用：网页控制台、关键词规则、去重、实时提醒、测试消息、本地 `data/inbox.txt` 文件监测。
- 后续可接：你主动转发到固定入口、合规开放平台消息源、OCR 辅助采集、其他购物群导出文本。

## 运行

双击项目根目录的 `启动CatBaby.bat` 可以一键启动，并自动打开浏览器页面。双击 `关闭CatBaby.bat` 可以停止 CatBaby 相关进程。

推荐使用本机指定解释器：

```powershell
cd E:\CodexProject\CatBaby
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
```

等价于：

```powershell
cd E:\CodexProject\CatBaby
D:\Anaconda\envs\py312\python.exe server.py
```

打开：

```text
http://127.0.0.1:8765
```

## 使用

1. 在网页里维护关键词规则。
2. 点击“开启通知”，允许浏览器通知。
3. 用“测试消息”验证提醒。
4. 也可以把一行消息追加到 `data/inbox.txt`，服务会自动读取新增行。

`data/inbox.txt` 支持普通文本行，也支持 JSON 行：

```json
{"room":"猫猫购物群","sender":"群友","content":"主食罐限时好价 https://example.com"}
```

## 自测

```powershell
cd E:\CodexProject\CatBaby
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

## 依赖

当前 MVP 只使用 Python 标准库，没有必须安装的外部依赖。后续如果增加依赖，写入 `requirements.txt` 后使用：

```powershell
cd E:\CodexProject\CatBaby
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

依赖会安装到项目内的 `.deps` 目录，`server.py` 启动时会自动加载。

## 目录

```text
CatBaby/
  catbaby/              后端核心
  config/               默认规则和运行规则
  data/                 本地消息、提醒、去重数据
  docs/                 设计文档
  tests/                单元测试
  web/                  本地控制台
  server.py             启动入口
```

## 当前限制

- 不能自动读取手机微信聊天记录。
- 本地服务需要电脑开着，浏览器页面打开时才能收到浏览器通知。
- `data/inbox.txt` 文件监测适合先验证规则链路，不等于微信实时接入。
