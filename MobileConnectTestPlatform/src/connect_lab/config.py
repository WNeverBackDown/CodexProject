from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AndroidConfig:
    adb_path: str = "adb"
    default_serial: str = ""
    devices: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ArtifactConfig:
    root: str = "artifacts"
    logcat_tail_lines: int = 500


@dataclass(frozen=True)
class AppiumConfig:
    server_url: str = "http://127.0.0.1:4723"
    capabilities: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AiConfig:
    engine: str = "local_rules"
    endpoint: str = ""


@dataclass(frozen=True)
class PrivacyConfig:
    redact: bool = True


@dataclass(frozen=True)
class TestbedConfig:
    path: Path
    android: AndroidConfig
    artifacts: ArtifactConfig
    appium: AppiumConfig
    ai: AiConfig
    privacy: PrivacyConfig
    raw: dict[str, Any]


def load_testbed(path: str | Path) -> TestbedConfig:
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Testbed config not found: {config_path}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    android_data = data.get("android", {}) or {}
    artifact_data = data.get("artifacts", {}) or {}
    appium_data = data.get("appium", {}) or {}
    ai_data = data.get("ai", {}) or {}
    privacy_data = data.get("privacy", {}) or {}

    return TestbedConfig(
        path=config_path,
        android=AndroidConfig(
            adb_path=str(android_data.get("adb_path") or "adb"),
            default_serial=str(android_data.get("default_serial") or ""),
            devices=list(android_data.get("devices") or []),
        ),
        artifacts=ArtifactConfig(
            root=str(artifact_data.get("root") or "artifacts"),
            logcat_tail_lines=int(artifact_data.get("logcat_tail_lines") or 500),
        ),
        appium=AppiumConfig(
            server_url=str(appium_data.get("server_url") or "http://127.0.0.1:4723"),
            capabilities=dict(appium_data.get("capabilities") or {}),
        ),
        ai=AiConfig(
            engine=str(ai_data.get("engine") or "local_rules"),
            endpoint=str(ai_data.get("endpoint") or ""),
        ),
        privacy=PrivacyConfig(
            redact=bool(privacy_data.get("redact", True)),
        ),
        raw=data,
    )
