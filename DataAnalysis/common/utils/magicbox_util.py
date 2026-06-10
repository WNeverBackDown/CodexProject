from __future__ import annotations

import hmac
from hashlib import sha256
from urllib.parse import urlencode

from config_env import settings


def sign_payload(payload: dict[str, str]) -> str:
    canonical = urlencode(sorted(payload.items()))
    return hmac.new(settings.app_secret.encode("utf-8"), canonical.encode("utf-8"), sha256).hexdigest()


def verify_payload(payload: dict[str, str], signature: str) -> bool:
    return hmac.compare_digest(sign_payload(payload), signature)
