import json
import os
import threading
import time

from .models import Message


class FileTailMonitor:
    def __init__(self, path, on_message, poll_seconds=0.8):
        self.path = path
        self.on_message = on_message
        self.poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread = None
        self._position = 0

    def start(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        open(self.path, "a", encoding="utf-8").close()
        self._position = os.path.getsize(self.path)
        self._thread = threading.Thread(target=self._run, name="catbaby-file-monitor")
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while not self._stop.is_set():
            try:
                self._read_new_lines()
            except Exception:
                pass
            self._stop.wait(self.poll_seconds)

    def _read_new_lines(self):
        if not os.path.exists(self.path):
            open(self.path, "a", encoding="utf-8").close()
        size = os.path.getsize(self.path)
        if size < self._position:
            self._position = 0
        if size == self._position:
            return

        with open(self.path, "r", encoding="utf-8") as handle:
            handle.seek(self._position)
            lines = handle.readlines()
            self._position = handle.tell()

        for line in lines:
            message = parse_inbox_line(line)
            if message and message.content:
                self.on_message(message)


def parse_inbox_line(line):
    text = (line or "").strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            return Message.from_dict(json.loads(text))
        except ValueError:
            pass
    return Message.from_dict(
        {
            "source": "inbox-file",
            "room": "导入消息",
            "sender": "",
            "content": text,
        }
    )
