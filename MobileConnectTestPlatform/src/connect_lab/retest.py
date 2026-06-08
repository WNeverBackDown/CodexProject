from __future__ import annotations

from dataclasses import asdict, dataclass

from connect_lab.diagnosis import DiagnosisReport


@dataclass(frozen=True)
class RetestItem:
    id: str
    title: str
    priority: str
    reason: str
    evidence_required: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


RETEST_LIBRARY: dict[str, list[RetestItem]] = {
    "bluetooth_disconnect": [
        RetestItem(
            id="bt_disconnect_reconnect_10x",
            title="蓝牙断连后连续重连 10 次",
            priority="P0",
            reason="确认断连是偶发链路抖动还是稳定复现问题。",
            evidence_required=["logcat", "bluetooth_state", "hci_snoop"],
        ),
        RetestItem(
            id="bt_disconnect_screen_off",
            title="熄屏 5 分钟后的蓝牙连接保持",
            priority="P1",
            reason="覆盖低功耗、后台限制和控制器状态切换。",
            evidence_required=["logcat", "hci_snoop"],
        ),
    ],
    "gatt_timeout": [
        RetestItem(
            id="gatt_discovery_retry",
            title="GATT 服务发现重试和 MTU 协商",
            priority="P0",
            reason="GATT timeout 常见于服务发现、MTU、外设响应慢或后台限制。",
            evidence_required=["logcat", "hci_snoop", "peripheral_log"],
        )
    ],
    "pairing_failure": [
        RetestItem(
            id="pairing_clear_bond_both_sides",
            title="双端清配对记录后重新配对",
            priority="P0",
            reason="排除历史 bond 记录、密钥不一致和弹窗授权残留。",
            evidence_required=["logcat", "bluetooth_state", "screenshot"],
        )
    ],
    "car_projection_failure": [
        RetestItem(
            id="car_projection_usb_wifi_switch",
            title="车机投屏 USB/Wi-Fi 介质切换",
            priority="P0",
            reason="投屏失败常发生在连接介质切换、认证握手和路由建立阶段。",
            evidence_required=["logcat", "head_unit_log", "video"],
        ),
        RetestItem(
            id="car_projection_reboot_recovery",
            title="手机和车机分别重启后的投屏恢复",
            priority="P1",
            reason="验证可信连接记录、授权状态和投屏服务恢复能力。",
            evidence_required=["logcat", "head_unit_log", "screenshot"],
        ),
    ],
    "wifi_direct_instability": [
        RetestItem(
            id="p2p_group_owner_handover",
            title="Wi-Fi Direct 组创建、移除和角色恢复",
            priority="P1",
            reason="确认 P2P group remove 是否导致互联链路不可恢复。",
            evidence_required=["logcat", "wifi_dump", "peer_log"],
        )
    ],
    "adapter_state_change": [
        RetestItem(
            id="adapter_toggle_baseline",
            title="蓝牙/Wi-Fi 开关基线稳定性",
            priority="P2",
            reason="确认 adapter state 变化是否由测试步骤触发。",
            evidence_required=["logcat", "settings_dump"],
        )
    ],
}


def recommend_retests(report: DiagnosisReport) -> list[RetestItem]:
    selected: list[RetestItem] = []
    seen: set[str] = set()
    for finding in report.findings:
        for item in RETEST_LIBRARY.get(finding.category, []):
            if item.id not in seen:
                selected.append(item)
                seen.add(item.id)
    if not selected:
        selected.append(
            RetestItem(
                id="manual_triage_pack",
                title="人工初筛材料补齐",
                priority="P2",
                reason="当前日志未命中明确规则，需要补齐多源证据后再归因。",
                evidence_required=["logcat", "screenshot", "video", "device_props"],
            )
        )
    return sorted(selected, key=lambda item: item.priority)


def retests_to_markdown(items: list[RetestItem]) -> str:
    lines = ["# 推荐复测集", ""]
    for item in items:
        lines.extend(
            [
                f"## {item.id} - {item.title}",
                f"- Priority: {item.priority}",
                f"- Reason: {item.reason}",
                f"- Evidence Required: {'; '.join(item.evidence_required)}",
                "",
            ]
        )
    return "\n".join(lines)
