from __future__ import annotations

from pathlib import Path

from connect_lab.cli import main
from connect_lab.reporting import build_markdown_report


def test_build_markdown_report_from_log_file():
    report = build_markdown_report("examples/car_projection_failure.log")

    assert "智慧互联测试分析报告" in report
    assert "car_projection_failure" in report
    assert "projection fail" in report
    assert "AA:BB:CC:DD:EE:FF" not in report


def test_build_report_cli_writes_output(tmp_path: Path):
    output = tmp_path / "report.md"

    rc = main(["build-report", "examples/car_projection_failure.log", "--output", str(output)])

    assert rc == 0
    assert output.exists()
    assert "Findings" in output.read_text(encoding="utf-8")
