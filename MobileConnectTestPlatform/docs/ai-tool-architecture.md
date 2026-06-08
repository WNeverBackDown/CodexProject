# AI 测试工具架构

## 总体架构

平台采用一个项目多模块架构：

- CLI 层：`connect_lab.cli` 提供 doctor、collect、diagnose、generate-cases、build-report。
- 采集层：`adb.py` 和后续 collector 模块负责手机、平板、车机、耳机相关证据采集。
- 诊断层：`diagnosis.py` 负责本地规则和未来 AI 引擎适配。
- 场景层：`scenarios.py` 负责生成智慧互联测试矩阵。
- 复测层：`retest.py` 根据失败分类推荐最小复测集。
- 缺陷层：`defect.py` 生成可贴到缺陷系统的标题、摘要、证据和复测建议。
- 报告层：`reporting.py` 负责输出 Markdown 报告。
- 隐私层：`privacy.py` 负责报告级脱敏。
- 测试层：pytest 覆盖无设备能力，Android marker 覆盖真实设备能力。

## 数据流

1. `collect` 从 Android 设备采集属性、蓝牙状态和 logcat，保存到 artifacts。
2. `diagnose` 读取日志或 artifacts 目录，输出结构化 finding。
3. `generate-cases` 根据 car、phone、tablet、headset 生成功能测试矩阵。
4. `recommend-retests` 根据诊断分类输出最小复测集。
5. `draft-defect` 生成缺陷标题、疑似原因、证据和推荐复测。
6. `build-report` 汇总诊断结果，生成可贴到缺陷单的 Markdown 报告。
7. 未来接入真实 AI 后，仍复用同一份采集数据和报告输出。

## 第一版工具清单

- `connect_lab diagnose`：AI 日志诊断器。
- `connect_lab generate-cases`：AI 测试场景生成器。
- `connect_lab build-report`：AI 报告助手。
- `connect_lab recommend-retests`：AI 复测推荐器。
- `connect_lab draft-defect`：AI 缺陷草稿助手。
- `connect_lab collect`：多设备证据采集底座。
- `mobly_tests/bluetooth_pairing_template.py`：多设备编排模板。

## AI 引擎设计

默认引擎是 `local_rules`：

- 优点：可离线、可解释、不会泄露公司日志。
- 缺点：覆盖依赖规则积累，无法像大模型一样理解复杂上下文。

后续可扩展引擎：

- `company_gateway`：公司内网模型服务，适合真实日志分析。
- `local_http`：本机或局域网大模型服务。
- `openai`：云端模型，适合个人学习和非敏感样例验证。

引擎替换原则：

- 输入保持为脱敏后的日志、设备角色、场景信息。
- 输出保持为 severity、category、evidence、suggestion、confidence。
- 不允许模型直接改写原始证据，只能引用脱敏后的证据摘要。

## 重点场景

车机互联优先：

- 首次连接和授权。
- 断连后重连。
- 手机或车机重启后的恢复。
- 来电、通知、锁屏、切后台打断。
- USB/Wi-Fi 投屏介质切换。

手机互联扩展：

- 文件互传、剪贴板流转、投屏、迁移、跨端登录状态。

平板和耳机扩展：

- 音频流转、蓝牙连接稳定性、低功耗恢复、同账号设备切换。
