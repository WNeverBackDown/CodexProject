from __future__ import annotations

import json

from connect_lab.cli import main
from connect_lab.diagnosis import diagnose_text
from connect_lab.privacy import redact_text


def test_diagnosis_finds_car_projection_and_redacts_private_data():
    text = """
    CarProjection: projection fail during auth handshake
    btif_av: disconnect reason=0x13 peer=AA:BB:CC:DD:EE:FF
    DeviceInfo: serial=ABC123456789 phone=13800138000 vin=LSVABCD12N1234567
    """

    report = diagnose_text(text)

    categories = {finding.category for finding in report.findings}
    evidence = "\n".join(finding.evidence for finding in report.findings)
    assert "car_projection_failure" in categories
    assert "bluetooth_disconnect" in categories
    assert "AA:BB:CC:DD:EE:FF" not in evidence
    assert "13800138000" not in evidence
    assert "LSVABCD12N1234567" not in evidence


def test_redact_text_masks_common_identifiers():
    redacted = redact_text("serial=ABC123 imei=123456789000000 mail=a@example.com mac=AA:BB:CC:DD:EE:FF")

    assert "ABC123" not in redacted
    assert "123456789000000" not in redacted
    assert "a@example.com" not in redacted
    assert "AA:BB:CC:DD:EE:FF" not in redacted


def test_diagnose_cli_outputs_json(capsys):
    rc = main(["diagnose", "examples/car_projection_failure.log", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert payload["findings"]
    assert payload["summary"]
