import os
import queue
import threading
import time

from .models import Alert, Message, new_id, stable_hash, utc_now_iso
from .monitor import FileTailMonitor
from .rules import RuleEngine, extract_url, normalize_text, validate_config
from .storage import append_jsonl, ensure_runtime_files, read_json, read_jsonl, truncate, write_json


class CatBabyApp:
    def __init__(self, root):
        self.root = root
        self.config_path = os.path.join(root, "config", "rules.json")
        self.inbox_path = os.path.join(root, "data", "inbox.txt")
        self.alerts_path = os.path.join(root, "data", "alerts.jsonl")
        self.messages_path = os.path.join(root, "data", "messages.jsonl")
        self.seen_path = os.path.join(root, "data", "seen.json")
        self.lock = threading.RLock()
        self.subscribers = []
        self.monitor = None

        ensure_runtime_files(root)
        self.config = validate_config(read_json(self.config_path, {"settings": {}, "rules": []}))
        self.engine = RuleEngine(self.config)
        self.seen = read_json(self.seen_path, {})

    def start(self):
        self.monitor = FileTailMonitor(self.inbox_path, self.process_message)
        self.monitor.start()

    def stop(self):
        if self.monitor:
            self.monitor.stop()

    def get_state(self):
        with self.lock:
            return {
                "status": "running",
                "config": self.config,
                "alerts": list(reversed(read_jsonl(self.alerts_path, limit=80))),
                "inbox_path": self.inbox_path,
                "version": "0.1.0",
            }

    def update_config(self, config):
        with self.lock:
            self.config = validate_config(config)
            self.engine = RuleEngine(self.config)
            write_json(self.config_path, self.config)
        self.publish("config", {"config": self.config})
        return self.config

    def clear_alerts(self):
        with self.lock:
            truncate(self.alerts_path)
        self.publish("alerts-cleared", {})

    def process_payload(self, payload):
        message = Message.from_dict(payload)
        return self.process_message(message)

    def process_message(self, message):
        if not message.url:
            message.url = extract_url(message.content)

        message_dict = message.to_dict()
        append_jsonl(self.messages_path, message_dict)

        matches = self.engine.match(message)
        alerts = []
        with self.lock:
            self._prune_seen()
            for match in matches:
                if self._is_duplicate(match["rule_id"], message):
                    continue
                alert = Alert(
                    id=new_id(match["rule_id"], message.id, message.content),
                    created_at=utc_now_iso(),
                    rule_id=match["rule_id"],
                    rule_name=match["rule_name"],
                    matched_terms=match["matched_terms"],
                    message=message_dict,
                ).to_dict()
                append_jsonl(self.alerts_path, alert)
                alerts.append(alert)
            write_json(self.seen_path, self.seen)

        for alert in alerts:
            self.publish("alert", alert)
        return alerts

    def subscribe(self):
        subscriber = queue.Queue()
        with self.lock:
            self.subscribers.append(subscriber)
        return subscriber

    def unsubscribe(self, subscriber):
        with self.lock:
            if subscriber in self.subscribers:
                self.subscribers.remove(subscriber)

    def publish(self, event_type, payload):
        event = {"type": event_type, "payload": payload, "time": utc_now_iso()}
        with self.lock:
            subscribers = list(self.subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                pass

    def _is_duplicate(self, rule_id, message):
        minutes = int(self.config.get("settings", {}).get("dedupe_minutes", 30))
        ttl = max(0, minutes) * 60
        key = stable_hash(rule_id, normalize_text(message.content), message.url)
        now = time.time()
        previous = float(self.seen.get(key, 0) or 0)
        if ttl and previous and now - previous < ttl:
            return True
        self.seen[key] = now
        return False

    def _prune_seen(self):
        keep_seconds = max(3600, int(self.config.get("settings", {}).get("dedupe_minutes", 30)) * 60 * 3)
        cutoff = time.time() - keep_seconds
        self.seen = {key: value for key, value in self.seen.items() if float(value or 0) >= cutoff}
