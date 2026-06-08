from __future__ import annotations

import json
from pathlib import Path

from connect_lab.cli import main
from connect_lab.defect import build_defect_draft, defect_to_markdown
from connect_lab.diagnosis import diagnose_path
from connect_lab.retest import recommend_retests, retests_to_markdown


def test_retest_recommendations_follow_diagnosis_categories():
    report = diagnose_path("examples/car_projection_failure.log")
    items = recommend_retests(report)
    ids = {item.id for item in items}

    assert "bt_disconnect_reconnect_10x" in ids
    assert "gatt_discovery_retry" in ids
    assert "car_projection_usb_wifi_switch" in ids
    assert retests_to_markdown(items).startswith("# 推荐复测集")


def test_defect_draft_contains_title_evidence_and_retests():
    draft = build_defect_draft("examples/car_projection_failure.log")
    markdown = defect_to_markdown(draft)

    assert "[智慧互联]" in draft.title
    assert draft.evidence
    assert draft.retests
    assert "Recommended Retests" in markdown
    assert "AA:BB:CC:DD:EE:FF" not in markdown


def test_recommend_retests_cli_outputs_json(capsys):
    rc = main(["recommend-retests", "examples/car_projection_failure.log", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert payload[0]["priority"].startswith("P")


def test_draft_defect_cli_writes_output(tmp_path: Path):
    output = tmp_path / "defect.md"

    rc = main(["draft-defect", "examples/car_projection_failure.log", "--output", str(output)])

    assert rc == 0
    assert output.exists()
    assert "Suspected Causes" in output.read_text(encoding="utf-8")
