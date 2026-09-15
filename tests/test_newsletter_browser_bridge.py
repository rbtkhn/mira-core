import json
import threading
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

import pytest
import newsletter_browser_bridge as bridge
from newsletter_capture import now, digest


def payload():
    return dict(url="https://example.org/p/one", title="Rodríguez — test", html="<p>α &amp; β</p>",
                text="α & β\n\nexact ", publication="example", observed_at=now().isoformat())


def test_exact_utf8_and_idempotent_receipt(tmp_path):
    value = payload()
    receipt = bridge.persist(tmp_path, value)
    for name, expected in {"body.txt": value["text"], "body.html": value["html"]}.items():
        data = (tmp_path / receipt["capture_id"] / name).read_bytes()
        assert data == expected.encode("utf-8")
        assert receipt["files"][name]["sha256"] == digest(data)
    assert bridge.persist(tmp_path, value) == receipt
    (tmp_path / receipt["capture_id"] / "body.txt").write_text("corrupt")
    with pytest.raises(ValueError, match="collision"):
        bridge.persist(tmp_path, value)


def test_stale_payload_rejected(tmp_path):
    with pytest.raises(ValueError, match="fresh"):
        bridge.persist(tmp_path, {**payload(), "observed_at": "2020-01-01T00:00:00Z"})
    assert not list(tmp_path.iterdir())


def test_real_form_round_trip_and_cross_origin_rejection(tmp_path):
    server = bridge.make_server(tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        body = urlencode({"payload": json.dumps(payload())}).encode()
        def submit(origin, site):
            return urlopen(Request(server.bridge_url, data=body, headers={
                "Origin": origin, "Sec-Fetch-Site": site,
                "Content-Type": "application/x-www-form-urlencoded"}), timeout=5)
        for origin, site in [("https://evil.example", "cross-site"), ("null", "cross-site")]:
            with pytest.raises(HTTPError) as error:
                submit(origin, site)
            assert error.value.code == 403
        assert not list(tmp_path.iterdir())
        with submit("null", "same-origin") as response:
            assert b"captured-awaiting-review" in response.read()
        assert len(list(tmp_path.glob("*/receipt.json"))) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
