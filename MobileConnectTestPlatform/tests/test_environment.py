from __future__ import annotations

import importlib.util

import pytest

from connect_lab.analysis import analyze_text


@pytest.mark.smoke
def test_required_python_modules_are_available():
    modules = ["pytest", "yaml", "adbutils", "appium", "mobly"]
    missing = [module for module in modules if importlib.util.find_spec(module) is None]
    assert not missing, f"Missing Python modules: {missing}"


@pytest.mark.smoke
def test_testbed_config_loads(testbed_config):
    assert testbed_config.android.adb_path
    assert testbed_config.artifacts.root


@pytest.mark.smoke
def test_local_log_analyzer_returns_findings():
    findings = analyze_text("Bluetooth GATT timeout while reconnecting")
    assert findings
    assert findings[0].severity in {"high", "medium", "low", "info"}
