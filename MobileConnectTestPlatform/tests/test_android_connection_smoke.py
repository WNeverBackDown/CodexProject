from __future__ import annotations

import json

import pytest


@pytest.mark.android
@pytest.mark.smoke
def test_android_device_basic_properties(android_device, artifact_store):
    props = {
        "manufacturer": android_device.getprop("ro.product.manufacturer"),
        "model": android_device.getprop("ro.product.model"),
        "release": android_device.getprop("ro.build.version.release"),
        "sdk": android_device.getprop("ro.build.version.sdk"),
    }
    artifact_store.write_text("device_props.json", json.dumps(props, indent=2, ensure_ascii=False))

    assert props["model"], "Device model should not be empty."
    assert props["sdk"].isdigit(), "Android SDK should be numeric."


@pytest.mark.android
@pytest.mark.bluetooth
@pytest.mark.smoke
def test_android_bluetooth_state_can_be_collected(android_device, artifact_store):
    state = android_device.bluetooth_state()
    artifact_store.write_text("bluetooth_state.json", json.dumps(state, indent=2, ensure_ascii=False))

    assert "global_bluetooth_on" in state
    assert "manager_summary" in state
