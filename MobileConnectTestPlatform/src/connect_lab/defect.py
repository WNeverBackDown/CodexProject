from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from connect_lab.diagnosis import DiagnosisReport, diagnose_path
from connect_lab.retest import RetestItem, recommend_retests


@dataclass(frozen=True)
class DefectDraft:
    title: str
    severity: str
    summary: str
    suspected_causes: list[str]
    evidence: list[str]
    retests: list[RetestItem]


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


def build_defect_draft(path: str | Path) -> DefectDraft:
    diagnosis = diagnose_path(path)
    return draft_from_diagnosis(diagnosis)


def draft_from_diagnosis(diagnosis: DiagnosisReport) -> DefectDraft:
    sorted_findings = sorted(diagnosis.findings, key=lambda finding: SEVERITY_ORDER.get(finding.severity, 9))
    lead = sorted_findings[0]
    evidence = [finding.evidence for finding in sorted_findings if finding.evidence]
    suspected = [f"{finding.category}: {finding.suggestion}" for finding in sorted_findings]
    return DefectDraft(
        title=f"[智慧互联][{lead.category}] {lead.title}",
        severity=lead.severity,
        summary=diagnosis.summary,
        suspected_causes=suspected,
        evidence=evidence,
        retests=recommend_retests(diagnosis),
    )


def defect_to_markdown(draft: DefectDraft) -> str:
    lines = [
        f"# {draft.title}",
        "",
        f"- Severity: {draft.severity}",
        f"- Summary: {draft.summary}",
        "",
        "## Suspected Causes",
        "",
    ]
    lines.extend(f"- {cause}" for cause in draft.suspected_causes)
    lines.extend(["", "## Evidence", ""])
    lines.extend(f"- {item}" for item in draft.evidence)
    lines.extend(["", "## Recommended Retests", ""])
    for item in draft.retests:
        lines.append(f"- [{item.priority}] {item.title}: {item.reason}")
    lines.extend(
        [
            "",
            "## Attachments To Provide",
            "",
            "- logcat",
            "- HCI snoop or Wi-Fi dump when available",
            "- Screenshot or video",
            "- Device roles, software versions, and connection medium",
        ]
    )
    return "\n".join(lines)
