from __future__ import annotations

from pathlib import Path

import pytest

from connect_lab.adb import AdbClient
from connect_lab.artifacts import ArtifactStore
from connect_lab.config import load_testbed


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("mobile-connect")
    group.addoption("--testbed", default="configs/testbed.example.yaml", help="Path to testbed YAML.")
    group.addoption("--serial", default="", help="Android device serial.")
    group.addoption("--require-device", action="store_true", help="Fail instead of skip when no device is online.")


@pytest.fixture(scope="session")
def testbed_config(pytestconfig: pytest.Config):
    return load_testbed(pytestconfig.getoption("--testbed"))


@pytest.fixture(scope="session")
def adb_client(testbed_config):
    return AdbClient(testbed_config.android.adb_path)


@pytest.fixture(scope="session")
def android_serial(pytestconfig: pytest.Config, testbed_config, adb_client):
    preferred = pytestconfig.getoption("--serial") or testbed_config.android.default_serial
    online = [device.serial for device in adb_client.devices() if device.state == "device"]

    if preferred:
        if preferred in online:
            return preferred
        message = f"Android device is not online: {preferred}"
        if pytestconfig.getoption("--require-device"):
            pytest.fail(message)
        pytest.skip(message)

    if len(online) == 1:
        return online[0]

    if not online:
        message = "No online Android device found."
    else:
        message = f"Multiple Android devices found; pass --serial. Online devices: {', '.join(online)}"

    if pytestconfig.getoption("--require-device"):
        pytest.fail(message)
    pytest.skip(message)


@pytest.fixture
def android_device(adb_client, android_serial):
    return adb_client.device(android_serial)


@pytest.fixture
def artifact_store(testbed_config, request: pytest.FixtureRequest):
    name = request.node.nodeid.replace("/", "_").replace("::", "_")
    root = Path(testbed_config.artifacts.root)
    return ArtifactStore.create(root, name)
