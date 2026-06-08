from __future__ import annotations

from dataclasses import dataclass

from connect_lab.diagnosis import diagnose_text


@dataclass(frozen=True)
class Finding:
    severity: str
    title: str
    evidence: str
    suggestion: str


def analyze_text(text: str) -> list[Finding]:
    report = diagnose_text(text)
    return [
        Finding(
            severity=finding.severity,
            title=finding.title,
            evidence=finding.evidence,
            suggestion=finding.suggestion,
        )
        for finding in report.findings
    ]
