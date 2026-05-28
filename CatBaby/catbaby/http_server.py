import json
import mimetypes
import os
import queue
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .app import CatBabyApp


def run_server(root, host, port):
    app = CatBabyApp(root)
    app.start()

    class Handler(CatBabyRequestHandler):
        catbaby_app = app
        project_root = root

    server = ThreadingHTTPServer((host, port), Handler)
    url = "http://%s:%s" % (host, port)
    print("CatBaby is running at %s" % url)
    print("Inbox file: %s" % app.inbox_path)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CatBaby...")
    finally:
        app.stop()
        server.server_close()


class CatBabyRequestHandler(BaseHTTPRequestHandler):
    catbaby_app = None
    project_root = None

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            return self._send_json(self.catbaby_app.get_state())
        if parsed.path == "/api/events":
            return self._send_events()
        if parsed.path == "/healthz":
            return self._send_json({"ok": True})
        return self._send_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/messages":
            payload = self._read_json_body()
            alerts = self.catbaby_app.process_payload(payload)
            return self._send_json({"ok": True, "alerts": alerts})
        if parsed.path == "/api/rules":
            payload = self._read_json_body()
            try:
                config = self.catbaby_app.update_config(payload)
            except ValueError as exc:
                return self._send_json({"ok": False, "error": str(exc)}, status=400)
            return self._send_json({"ok": True, "config": config})
        if parsed.path == "/api/alerts/clear":
            self.catbaby_app.clear_alerts()
            return self._send_json({"ok": True})
        return self._send_json({"ok": False, "error": "Not found"}, status=404)

    def _send_events(self):
        subscriber = self.catbaby_app.subscribe()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(b": connected\n\n")
        self.wfile.flush()
        try:
            while True:
                try:
                    event = subscriber.get(timeout=15)
                    self._write_event(event)
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.catbaby_app.unsubscribe(subscriber)

    def _write_event(self, event):
        body = json.dumps(event, ensure_ascii=False)
        self.wfile.write(("data: %s\n\n" % body).encode("utf-8"))
        self.wfile.flush()

    def _send_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        relative = path.lstrip("/").replace("/", os.sep)
        static_path = os.path.abspath(os.path.join(self.project_root, "web", relative))
        static_root = os.path.abspath(os.path.join(self.project_root, "web"))
        if os.path.commonpath([static_root, static_path]) != static_root or not os.path.exists(static_path):
            return self._send_json({"ok": False, "error": "Not found"}, status=404)
        with open(static_path, "rb") as handle:
            data = handle.read()
        content_type = mimetypes.guess_type(static_path)[0] or "application/octet-stream"
        if static_path.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        elif static_path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif static_path.endswith(".html"):
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
