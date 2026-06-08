from __future__ import annotations

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class TestScenario:
    id: str
    domain: str
    title: str
    preconditions: list[str]
    steps: list[str]
    expected: list[str]
    evidence: list[str]
    risk: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


CAR_SCENARIOS = [
    TestScenario(
        id="car_projection_first_connect",
        domain="car",
        title="车机投屏首次连接",
        preconditions=["DUT 未连接目标车机", "车机处于可连接状态"],
        steps=["清理历史配对", "连接 USB 或 Wi-Fi 投屏入口", "完成授权弹窗", "等待投屏主界面出现"],
        expected=["手机端显示已连接", "车机端出现投屏画面", "logcat 无高风险断连或认证失败"],
        evidence=["logcat", "device_props", "screenshot", "head_unit_log"],
        risk="high",
    ),
    TestScenario(
        id="car_projection_reconnect_after_disconnect",
        domain="car",
        title="车机投屏断开后自动重连",
        preconditions=["DUT 已成功投屏", "已开启日志采集"],
        steps=["断开 USB 或关闭车机 Wi-Fi", "等待 10 秒", "恢复连接介质", "观察自动重连"],
        expected=["连接可恢复", "恢复后音频/导航/触控可用", "失败时报告断连 reason"],
        evidence=["logcat", "hci_snoop", "video", "head_unit_log"],
        risk="high",
    ),
    TestScenario(
        id="car_projection_phone_reboot_recovery",
        domain="car",
        title="手机重启后的车机连接恢复",
        preconditions=["DUT 与车机已有可信连接记录"],
        steps=["手机重启", "解锁进入桌面", "靠近或接入车机", "观察自动连接"],
        expected=["历史连接记录保留", "无需重复授权或授权流程符合预期", "投屏可恢复"],
        evidence=["logcat", "device_props", "screenshot"],
        risk="medium",
    ),
    TestScenario(
        id="car_projection_background_call",
        domain="car",
        title="投屏中来电和切后台稳定性",
        preconditions=["DUT 正在投屏导航或音乐"],
        steps=["触发来电或通知", "切换前后台", "锁屏再解锁", "回到投屏界面"],
        expected=["投屏不中断", "音频焦点切换符合预期", "恢复后无黑屏或触控失效"],
        evidence=["logcat", "screenshot", "video"],
        risk="medium",
    ),
]


PHONE_SCENARIOS = [
    TestScenario(
        id="phone_to_phone_file_transfer",
        domain="phone",
        title="手机间文件互传",
        preconditions=["两台手机互联功能开启"],
        steps=["选择大文件", "发起传输", "传输中切后台", "校验接收文件"],
        expected=["传输完成", "文件大小和名称正确", "失败时有明确错误提示"],
        evidence=["logcat", "screenshot"],
        risk="medium",
    )
]


ACCESSORY_SCENARIOS = [
    TestScenario(
        id="headset_audio_handover",
        domain="headset",
        title="耳机音频流转",
        preconditions=["耳机已与手机配对", "平板登录同账号"],
        steps=["手机播放音乐", "平板发起音频接管", "手机来电", "切回手机"],
        expected=["音频路由正确", "连接状态展示正确", "无异常断连"],
        evidence=["logcat", "bluetooth_state", "hci_snoop"],
        risk="medium",
    )
]


SCENARIOS = {
    "car": CAR_SCENARIOS,
    "phone": PHONE_SCENARIOS,
    "tablet": ACCESSORY_SCENARIOS,
    "headset": ACCESSORY_SCENARIOS,
}


def generate_scenarios(domain: str = "car") -> list[TestScenario]:
    normalized = domain.lower().strip()
    if normalized not in SCENARIOS:
        valid = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"Unsupported domain: {domain}. Valid domains: {valid}")
    return SCENARIOS[normalized]


def scenarios_to_markdown(scenarios: list[TestScenario]) -> str:
    lines = ["# 智慧互联测试场景矩阵", ""]
    for scenario in scenarios:
        lines.extend(
            [
                f"## {scenario.id} - {scenario.title}",
                f"- Domain: {scenario.domain}",
                f"- Risk: {scenario.risk}",
                f"- Preconditions: {'; '.join(scenario.preconditions)}",
                f"- Steps: {'; '.join(scenario.steps)}",
                f"- Expected: {'; '.join(scenario.expected)}",
                f"- Evidence: {'; '.join(scenario.evidence)}",
                "",
            ]
        )
    return "\n".join(lines)


def scenarios_to_json(scenarios: list[TestScenario]) -> str:
    return json.dumps([scenario.to_dict() for scenario in scenarios], indent=2, ensure_ascii=False)
