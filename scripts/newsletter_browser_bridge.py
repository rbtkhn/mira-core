"""Loopback HTML form transport for fresh, reviewed browser DOM captures.

This receiver acquires no browser credentials and performs no archive admission.
The caller supplies a private temporary root; article review and intake follow.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import parse_qs

from newsletter_capture import canonical, digest, write
from portable_paths import require_private_path

MAX_BYTES = 4 * 1024 * 1024


def persist(root, payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be an object")
    for field in ("url", "title", "html", "text", "observed_at", "publication"):
        if not isinstance(payload.get(field), str):
            raise ValueError("Missing string field: " + field)
    if not canonical(payload["url"]):
        raise ValueError("Expected an HTTPS article URL")
    observed = datetime.fromisoformat(payload["observed_at"].replace("Z", "+00:00"))
    if observed.tzinfo is None or not -60 <= (datetime.now(timezone.utc) - observed).total_seconds() <= 900:
        raise ValueError("Capture timestamp is not fresh")
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    key = digest(raw)
    target = root / key
    files = {"payload.json": raw, "body.html": payload["html"].encode("utf-8"),
             "body.txt": payload["text"].encode("utf-8")}
    receipt = {"capture_id": key, "status": "captured-awaiting-review", "url": payload["url"],
               "transport": "loopback-browser-form", "observed_at": payload["observed_at"],
               "received_at": datetime.now(timezone.utc).isoformat(), "files": {}}
    for name, data in files.items():
        path = target / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError("Immutable capture collision")
        if not path.exists():
            write(path, data)
        persisted = path.read_bytes()
        if persisted != data:
            raise ValueError("Capture persistence parity mismatch")
        receipt["files"][name] = {"path": str(path), "bytes": len(persisted), "sha256": digest(persisted)}
    # Last write is the receipt: missing receipt means inspect files, not recapture.
    if (target / "receipt.json").exists():
        return json.loads((target / "receipt.json").read_text(encoding="utf-8"))
    write(target / "receipt.json", receipt)
    return receipt


def make_server(root, port=0):
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, code, message):
            body = ("<!doctype html><meta charset=utf-8><title>Newsletter capture receiver</title>"
                    "<h1>Newsletter capture receiver</h1><pre>" + escape(message) + "</pre>"
                    '<form method="post"><label for="payload">Capture payload</label>'
                    '<textarea id="payload" name="payload"></textarea>'
                    '<button type="submit">Save capture</button></form>').encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'none'; form-action 'self'; frame-ancestors 'none'")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)

        def allowed(self):
            return self.path == "/" + token and self.headers.get("Host") == self.server.address

        def do_GET(self):
            self.respond(200 if self.allowed() else 403, "Ready" if self.allowed() else "Forbidden")

        def do_POST(self):
            origin = self.headers.get("Origin")
            # The in-app browser sends an opaque Origin for this local form.
            # Accept it only with browser-supplied same-origin fetch metadata;
            # retain the unguessable session path and exact Host checks.
            same_origin = origin == "http://" + self.server.address or (
                origin == "null" and self.headers.get("Sec-Fetch-Site") == "same-origin")
            if not self.allowed() or not same_origin:
                self.respond(403, "Forbidden")
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= MAX_BYTES or self.headers.get("Content-Type", "").split(";")[0] != "application/x-www-form-urlencoded":
                    raise ValueError("Unsupported or oversized submission")
                form = parse_qs(self.rfile.read(size).decode("utf-8"), strict_parsing=True)
                if set(form) != {"payload"} or len(form["payload"]) != 1:
                    raise ValueError("Expected one payload")
                receipt = persist(root, json.loads(form["payload"][0]))
                self.respond(200, json.dumps(receipt, ensure_ascii=False, indent=2))
            except (ValueError, OSError) as error:
                self.respond(400, type(error).__name__ + ": capture rejected")

    server = HTTPServer(("127.0.0.1", port), Handler)
    server.address = "127.0.0.1:" + str(server.server_port)
    server.bridge_url = "http://" + server.address + "/" + token
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temp-root", required=True, type=Path)
    args = parser.parse_args()
    root = require_private_path(args.temp_root, label="Capture temporary root", repo_root=Path(__file__).resolve().parents[1])
    if not root.is_dir():
        parser.error("Run session-preflight against an existing private temporary root first")
    server = make_server(root)
    print(json.dumps({"status": "listening", "url": server.bridge_url, "root": str(root)}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print('{"status":"stopped"}', flush=True)


if __name__ == "__main__":
    main()
