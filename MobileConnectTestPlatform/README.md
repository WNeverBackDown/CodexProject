# Mobile Connect Test Platform

伟哥，这是一个面向手机大厂智慧互联测试开发岗位的 AI 测试工具箱骨架，优先覆盖手机-车机互联，同时预留手机-手机、手机-平板、手机-耳机等方向。

第一版默认离线运行，不调用外部 AI API。当前的“AI”能力先落成可解释的本地规则诊断、测试场景生成、报告摘要和脱敏能力，后续可以把诊断引擎替换成公司内网模型、本地大模型或云端模型。

## 已包含能力

- ADB 设备发现、属性采集、蓝牙状态采集、logcat 采集。
- pytest smoke 测试和 Android 设备测试入口。
- Appium 和 Mobly 接入模板，便于扩展系统设置页、车载互联 App 和多设备场景。
- 本地 AI 诊断器：识别蓝牙断连、GATT timeout、配对失败、车机投屏失败、Wi-Fi Direct 不稳定等模式。
- 智慧互联测试场景生成器：按 car、phone、tablet、headset 输出测试矩阵。
- AI 复测推荐器：根据失败分类给出最小复测集。
- AI 缺陷草稿助手：生成缺陷标题、疑似原因、证据和复测建议。
- Markdown 测试分析报告生成器。
- 隐私脱敏：默认掩码 MAC、VIN、手机号、邮箱、serial、IMEI 等敏感字段。

完整交付总览见 `docs\deliverables.md`。

## 环境

使用你指定的 Python 环境：

```powershell
D:\Anaconda\envs\py312\python.exe
```

安装依赖：

```powershell
cd E:\CodexProject\MobileConnectTestPlatform
D:\Anaconda\envs\py312\python.exe -m pip install -r requirements.txt
```

## 快速验证

```powershell
.\scripts\doctor.cmd
.\scripts\run_smoke.cmd
```

无设备环境下，Android 设备测试会自动跳过。当前本地验证命令：

```powershell
D:\Anaconda\envs\py312\python.exe -m pytest -q
```

## AI 诊断日志

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli diagnose examples\car_projection_failure.log
```

输出 JSON：

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli diagnose examples\car_projection_failure.log --json
```

## 生成智慧互联测试场景

车机互联：

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli generate-cases --domain car
```

手机互联、平板、耳机方向：

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli generate-cases --domain phone
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli generate-cases --domain tablet
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli generate-cases --domain headset
```

## 生成 Markdown 分析报告

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli build-report examples\car_projection_failure.log --output reports\car_projection_failure.md
```

## 推荐最小复测集

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli recommend-retests examples\car_projection_failure.log
```

输出 JSON：

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli recommend-retests examples\car_projection_failure.log --json
```

## 生成缺陷草稿

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli draft-defect examples\car_projection_failure.log --output reports\car_projection_failure_defect.md
```

## 采集真实 Android 设备证据

连接 Android 设备并开启 USB 调试后：

```powershell
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli collect --serial <device_serial>
```

如果只有一台在线设备，可以省略 `--serial`。

## 推荐下一步

1. 把真实测试机、车机、平板、耳机信息写入 `configs\testbed.example.yaml` 的副本中。
2. 用真实失败日志扩展 `src\connect_lab\diagnosis.py` 的规则库。
3. 把常测 SOP 固化为 pytest、Appium 或 Mobly 测试。
4. 后续如需接入公司内网模型，只替换 AI engine 适配层，不改变采集、用例和报告模块。
