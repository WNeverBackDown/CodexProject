from __future__ import annotations

import json

from connect_lab.cli import main
from connect_lab.scenarios import generate_scenarios, scenarios_to_json, scenarios_to_markdown


def test_generate_car_scenarios_contains_reconnect_and_reboot():
    scenarios = generate_scenarios("car")
    ids = {scenario.id for scenario in scenarios}

    assert "car_projection_reconnect_after_disconnect" in ids
    assert "car_projection_phone_reboot_recovery" in ids
    assert all(scenario.evidence for scenario in scenarios)


def test_scenario_renderers_produce_markdown_and_json():
    scenarios = generate_scenarios("car")
    markdown = scenarios_to_markdown(scenarios)
    payload = json.loads(scenarios_to_json(scenarios))

    assert "智慧互联测试场景矩阵" in markdown
    assert payload[0]["domain"] == "car"


def test_generate_cases_cli_prints_markdown(capsys):
    rc = main(["generate-cases", "--domain", "car"])

    captured = capsys.readouterr()
    assert rc == 0
    assert "car_projection_first_connect" in captured.out
