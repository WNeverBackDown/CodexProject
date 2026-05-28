import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(*parts):
    raw = "|".join([str(part or "") for part in parts]) + "|" + str(time.time())
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def stable_hash(*parts):
    raw = "|".join([str(part or "") for part in parts])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


@dataclass
class Message:
    id: str
    source: str
    room: str
    sender: str
    content: str
    url: str
    received_at: str

    @classmethod
    def from_dict(cls, payload):
        content = str(payload.get("content") or "").strip()
        received_at = str(payload.get("received_at") or utc_now_iso())
        return cls(
            id=str(payload.get("id") or new_id(payload.get("source"), payload.get("room"), content)),
            source=str(payload.get("source") or "manual"),
            room=str(payload.get("room") or "未分组"),
            sender=str(payload.get("sender") or ""),
            content=content,
            url=str(payload.get("url") or ""),
            received_at=received_at,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "room": self.room,
            "sender": self.sender,
            "content": self.content,
            "url": self.url,
            "received_at": self.received_at,
        }


@dataclass
class Alert:
    id: str
    created_at: str
    rule_id: str
    rule_name: str
    matched_terms: list
    message: dict

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "matched_terms": self.matched_terms,
            "message": self.message,
        }
