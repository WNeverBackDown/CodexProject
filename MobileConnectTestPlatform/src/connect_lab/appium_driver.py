from __future__ import annotations

from typing import Any


def create_android_driver(server_url: str, capabilities: dict[str, Any]):
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options().load_capabilities(capabilities)
    return webdriver.Remote(server_url, options=options)
