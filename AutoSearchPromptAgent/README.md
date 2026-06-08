# 人群挖掘 Agent

这是一个本地可运行的 AutoSearch Prompt Agent 演示项目。它现在不仅展示截图里的内容，还可以通过本地 Node 服务调用 DeepSeek API，生成真实的结构化 Agent 运行结果。

## 能做什么

- 输入业务场景和需求描述。
- 填入 DeepSeek API key，选择模型。
- 调用 DeepSeek 生成特征抽取、Prompt 候选、评估指标、Judge 判断和 MR 草案。
- 没有 API key 时，可以用本地规则引擎做兜底预估。

## API key 安全边界

- API key 不写入系统环境变量。
- API key 不保存到项目文件。
- 页面会把 key 发给本机 `127.0.0.1` 上的 Node 服务，由本机服务请求 DeepSeek。
- 浏览器当前会话内会用 `sessionStorage` 暂存 key，关闭浏览器会话后失效。

## 运行

```powershell
cd E:\CodexProject\AutoSearchPromptAgent
npm.cmd run dev
```

打开终端输出的地址，例如：

```text
http://127.0.0.1:4173
```

如果端口被占用，服务会自动尝试后续端口，比如 `4174`。

## 检查

```powershell
npm.cmd run build
```

当前版本没有第三方运行依赖，不需要执行 `npm install`。使用 `npm.cmd` 是为了绕开本机 PowerShell 对 `npm.ps1` 的执行策略限制，不会修改系统配置或环境变量。

## 文档

详细架构说明见：

```text
docs/ARCHITECTURE.md
```
