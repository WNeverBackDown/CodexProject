from __future__ import annotations

from pathlib import Path

from connect_lab.diagnosis import DiagnosisReport, diagnose_path


LOG_CANDIDATES = ("logcat_tail.txt", "logcat.txt", "phone_logcat.txt")


def build_markdown_report(run_dir: str | Path) -> str:
    root = Path(run_dir)
    if root.is_file():
        diagnosis = diagnose_path(root)
        title = root.name
    else:
        diagnosis = _diagnose_run_dir(root)
        title = root.name or str(root)

    return render_diagnosis_report(title, diagnosis)


def render_diagnosis_report(title: str, diagnosis: DiagnosisReport) -> str:
    lines = [
        f"# 智慧互联测试分析报告 - {title}",
        "",
        f"- Source: {diagnosis.source}",
        f"- Summary: {diagnosis.summary}",
        "",
        "## Findings",
        "",
    ]
    for finding in diagnosis.findings:
        lines.extend(
            [
                f"### [{finding.severity}] {finding.title}",
                f"- Category: {finding.category}",
                f"- Confidence: {finding.confidence:.2f}",
                f"- Evidence: {finding.evidence}",
                f"- Suggestion: {finding.suggestion}",
                "",
            ]
        )
    return "\n".join(lines)


def _diagnose_run_dir(root: Path) -> DiagnosisReport:
    if not root.exists():
        raise FileNotFoundError(f"Run directory not found: {root}")
    for name in LOG_CANDIDATES:
        candidate = root / name
        if candidate.exists():
            return diagnose_path(candidate)
    texts = sorted(root.rglob("*.txt"))
    if texts:
        return diagnose_path(texts[0])
    raise FileNotFoundError(f"No text log found in run directory: {root}")
