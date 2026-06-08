from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from connect_lab.privacy import redact_text


@dataclass(frozen=True)
class DiagnosticFinding:
    severity: str
    category: str
    title: str
    evidence: str
    suggestion: str
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DiagnosisReport:
    source: str
    findings: list[DiagnosticFinding]
    summary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
        }


RULES = [
    {
        "severity": "high",
        "category": "bluetooth_disconnect",
        "keywords": ["btif", "disconnect", "reason"],
        "title": "Bluetooth disconnect reason appears in logs",
        "suggestion": "Correlate phone logcat with HCI snoop and check whether disconnect came from phone, peer, or controller.",
        "confidence": 0.82,
    },
    {
        "severity": "high",
        "category": "gatt_timeout",
        "keywords": ["gatt", "timeout"],
        "title": "GATT operation timeout appears in logs",
        "suggestion": "Retest service discovery, MTU negotiation, background restrictions, and peripheral response timing.",
        "confidence": 0.8,
    },
    {
        "severity": "medium",
        "category": "pairing_failure",
        "keywords": ["bond", "fail"],
        "title": "Bonding or pairing failure appears in logs",
        "suggestion": "Clear paired records on both sides, repeat pairing, and capture HCI snoop before filing the defect.",
        "confidence": 0.75,
    },
    {
        "severity": "high",
        "category": "car_projection_failure",
        "keywords": ["projection", "fail"],
        "title": "Car projection failure appears in logs",
        "suggestion": "Check USB/Wi-Fi switch timing, certificate/authentication logs, and head-unit side connection events.",
        "confidence": 0.78,
    },
    {
        "severity": "medium",
        "category": "wifi_direct_instability",
        "keywords": ["p2p", "group", "remove"],
        "title": "Wi-Fi Direct group removal appears in logs",
        "suggestion": "Retest under screen-off, network handover, hotspot coexistence, and peer reboot scenarios.",
        "confidence": 0.7,
    },
    {
        "severity": "low",
        "category": "adapter_state_change",
        "keywords": ["adapter", "state"],
        "title": "Connectivity adapter state changes appear",
        "suggestion": "Confirm whether the test intentionally toggled Bluetooth, Wi-Fi, airplane mode, or power saving.",
        "confidence": 0.62,
    },
]


def diagnose_text(text: str, source: str = "inline") -> DiagnosisReport:
    lower = text.lower()
    findings: list[DiagnosticFinding] = []

    for rule in RULES:
        keywords = list(rule["keywords"])
        if all(keyword in lower for keyword in keywords):
            findings.append(
                DiagnosticFinding(
                    severity=str(rule["severity"]),
                    category=str(rule["category"]),
                    title=str(rule["title"]),
                    evidence=redact_text(_first_matching_line(text, keywords)),
                    suggestion=str(rule["suggestion"]),
                    confidence=float(rule["confidence"]),
                )
            )

    if not findings:
        findings.append(
            DiagnosticFinding(
                severity="info",
                category="no_rule_hit",
                title="No obvious connectivity risk found by local rules",
                evidence="No configured rule matched.",
                suggestion="Attach logcat, HCI snoop, screenshots, video, and exact device roles for deeper analysis.",
                confidence=0.5,
            )
        )

    return DiagnosisReport(source=source, findings=findings, summary=_summarize(findings))


def diagnose_path(path: str | Path) -> DiagnosisReport:
    log_path = Path(path)
    if log_path.is_dir():
        log_path = _find_log_in_dir(log_path)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return diagnose_text(text, source=str(log_path))


def _first_matching_line(text: str, keywords: list[str]) -> str:
    for line in text.splitlines():
        lower = line.lower()
        if all(keyword in lower for keyword in keywords):
            return line.strip()[:500]
    for line in text.splitlines():
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            return line.strip()[:500]
    return ""


def _summarize(findings: list[DiagnosticFinding]) -> str:
    severe = [finding for finding in findings if finding.severity in {"high", "medium"}]
    if severe:
        categories = ", ".join(finding.category for finding in severe[:3])
        return f"Potential connectivity risks found: {categories}."
    return "No high or medium risk matched by local diagnosis rules."


def _find_log_in_dir(root: Path) -> Path:
    for name in ("logcat_tail.txt", "logcat.txt", "phone_logcat.txt"):
        candidate = root / name
        if candidate.exists():
            return candidate
    texts = sorted(root.rglob("*.txt"))
    if texts:
        return texts[0]
    raise FileNotFoundError(f"No text log found in run directory: {root}")
