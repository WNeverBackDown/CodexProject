# 智慧互联 AI 测试工具交付总览

## 目标

面向手机智慧互联测试开发岗位，沉淀一套可离线运行、可扩展到真实设备和内网 AI 的测试提效工具箱。第一版优先覆盖手机-车机互联，同时保留手机-手机、手机-平板、手机-耳机方向。

## 可以做的 AI 测试工具方向

1. AI 日志诊断器：从 logcat、蓝牙状态、车机日志、HCI snoop 摘要里识别断连、超时、配对失败、投屏失败等模式。
2. AI 用例生成器：按 car、phone、tablet、headset 生成功能测试矩阵和证据要求。
3. AI 复测推荐器：根据失败分类给出最小复测集，减少盲目全量回归。
4. AI 缺陷草稿助手：自动生成缺陷标题、疑似原因、关键证据、复测建议和附件清单。
5. AI 报告助手：把诊断结果整理成 Markdown 报告，方便贴到缺陷单或测试日报。
6. 多设备证据采集器：统一采集 DUT、peer phone、tablet、headset、car/head-unit 的属性、连接状态和日志。
7. 历史缺陷规则沉淀器：把历史高频问题转成本地规则或模型 prompt，逐步提升命中率。
8. 互联链路健康检查器：对蓝牙、Wi-Fi Direct、USB、投屏服务、账号状态做冒烟检查。
9. 测试矩阵风险排序器：按场景风险、历史失败率、设备组合复杂度排序执行优先级。
10. 内网 AI 适配器：后续对接公司模型网关、本地大模型或云端模型，但默认保持离线可用。

## 已搭建的第一版工具

当前项目路径：

```text
E:\CodexProject\MobileConnectTestPlatform
```

已落地能力：

- `connect_lab diagnose`：分析日志或 artifacts 目录。
- `connect_lab generate-cases`：生成智慧互联测试场景。
- `connect_lab recommend-retests`：推荐最小复测集。
- `connect_lab draft-defect`：生成缺陷草稿。
- `connect_lab build-report`：生成 Markdown 分析报告。
- `connect_lab collect`：采集真实 Android 设备基础证据。
- `mobly_tests/bluetooth_pairing_template.py`：多 Android 设备编排模板。

## 架构

```text
CLI
  ├─ collect           -> ADB evidence collector
  ├─ diagnose          -> local_rules diagnosis engine
  ├─ generate-cases    -> scenario matrix generator
  ├─ recommend-retests -> focused retest recommender
  ├─ draft-defect      -> defect draft builder
  └─ build-report      -> Markdown report builder

Core modules
  ├─ adb.py            -> Android device access
  ├─ diagnosis.py      -> finding model and rule engine
  ├─ scenarios.py      -> car/phone/tablet/headset scenarios
  ├─ retest.py         -> retest library and recommendation
  ├─ defect.py         -> defect draft generation
  ├─ reporting.py      -> diagnosis report rendering
  ├─ privacy.py        -> MAC/VIN/phone/email/device-id redaction
  └─ config.py         -> testbed, AI engine and privacy config
```

## 快速验收命令

```powershell
cd E:\CodexProject\MobileConnectTestPlatform
D:\Anaconda\envs\py312\python.exe -m pytest -q
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli diagnose examples\car_projection_failure.log
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli generate-cases --domain car
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli recommend-retests examples\car_projection_failure.log
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli draft-defect examples\car_projection_failure.log --output reports\car_projection_failure_defect.md
D:\Anaconda\envs\py312\python.exe -m connect_lab.cli build-report examples\car_projection_failure.log --output reports\car_projection_failure.md
```

## 当前边界

- 默认不调用外部 AI API，适合公司内网或无网环境。
- 没有真实 Android 设备时，Android 测试会跳过；本地规则、场景、报告、复测、缺陷草稿仍可完整验证。
- 后续接入内网模型时，建议保持输出结构不变：`severity`、`category`、`evidence`、`suggestion`、`confidence`。
