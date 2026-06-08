from __future__ import annotations

import re


REDACTION_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"), "<MAC>"),
    (re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b"), "<VIN>"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "<PHONE>"),
    (re.compile(r"(?i)\b(?:serial|sn|device_id|imei|meid)\s*[:=]\s*[\w.-]+"), "<DEVICE_ID>"),
    (re.compile(r"(?i)\b[\w.%+-]+@[\w.-]+\.[A-Z]{2,}\b"), "<EMAIL>"),
]


def redact_text(text: str) -> str:
    redacted = text
    for pattern, replacement in REDACTION_RULES:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_mapping(data: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = redact_text(value)
        elif isinstance(value, dict):
            result[key] = redact_mapping(value)
        elif isinstance(value, list):
            result[key] = [redact_text(item) if isinstance(item, str) else item for item in value]
        else:
            result[key] = value
    return result
