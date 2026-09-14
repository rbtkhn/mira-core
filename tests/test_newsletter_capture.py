import base64
from email.message import EmailMessage
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest
import newsletter_capture as nc


def email(subject="A strategic essay", extra="", body=None, sender="Glenn Diesen <writer@example.org>"):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = nc.MAILBOX
    message["List-ID"] = "<diesen.example.org>"
    message["Message-ID"] = "<one@example.org>"
    message["Date"] = "Mon, 14 Sep 2026 08:00:00 +0000"
    message["Subject"] = subject
    words = body or "A qualified mechanism with an uncertain outcome. " * 20
    message.set_content("Read online https://glenndiesen.substack.com/p/test " + extra)
    message.add_alternative('<div class="body"><h2>Argument</h2><p>' + words + '</p><a href="https://glenndiesen.substack.com/p/test?utm_source=email">Read online</a>' + extra + '</div><footer>Upgrade to paid</footer>', subtype="html")
    return message.as_bytes()


@pytest.fixture
def store(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "archive/sources/geopolitics/source-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"sources": []}')
    store = nc.Store(repo, tmp_path / "state")
    sample = tmp_path / "sample.eml"
    sample.write_bytes(email())
    nc.approve_route(store, "diesen", sample, "body")
    return store


def route(store):
    return store.read("routes.json", {})["diesen"]


class Gmail:
    def __init__(self, raw=None, expire=False, fail=False):
        self.raw = raw or email()
        self.expire = expire
        self.fail = fail
        self.calls = []

    def get(self, resource, **params):
        self.calls.append((resource, params))
        if resource == "profile":
            return {"emailAddress": nc.MAILBOX, "historyId": "100"}
        if self.fail:
            raise OSError("interrupted")
        if params.get("format") == "metadata":
            return {"payload": {"headers": [{"name": "From", "value": "Glenn Diesen <writer@example.org>"}, {"name": "List-ID", "value": "<diesen.example.org>"}]}}
        return {"raw": base64.urlsafe_b64encode(self.raw).decode(), "internalDate": "1789372800000"}

    def pages(self, resource, **params):
        self.calls.append((resource, params))
        if resource == "history":
            if self.expire:
                raise HTTPError("", 404, "expired", {}, None)
            yield {"history": [{"messagesAdded": [{"message": {"id": "one"}}]}]}
        else:
            yield {"messages": [{"id": "one"}]}


def test_complete_preserves_text_and_links(store):
    result = nc.parse(email(), route(store))
    assert result["status"] == "intake-pending"
    assert "Argument\nA qualified mechanism" in result["body"]
    assert "https://glenndiesen.substack.com/p/test?utm_source=email" in result["body"]
    assert "Upgrade to paid" not in result["body"]
    assert result["publication_date"] == "2026-09-14"


@pytest.mark.parametrize("subject,extra,expected", [
    ("Welcome to the newsletter", "", "excluded"),
    ("Special offer", "", "excluded"),
    ("Essay", "Subscribe to keep reading", "acquisition-pending"),
    ("New video", "", "acquisition-pending"),
    ("Essay", "This post is for paid subscribers", "acquisition-pending"),
])
def test_message_classes(store, subject, extra, expected):
    assert nc.parse(email(subject, extra), route(store))["status"] == expected


def test_unknown_sender_or_template_holds(store):
    assert nc.parse(email(sender="Other <other@example.org>"), route(store))["status"] == "review-needed"
    assert nc.parse(email(), {**route(store), "article_class": "missing"})["status"] == "review-needed"


def test_singularity_never_geo(store):
    assert nc.parse(email(), {**route(store), "lane": "singularity"})["status"] == "singularity-pending"


def test_fetch_retry_and_incremental(store):
    gmail = Gmail()
    assert nc.fetch(store, gmail)["captured"] == 1
    assert nc.fetch(store, gmail)["captured"] == 0
    assert any(call[0] == "history" for call in gmail.calls)
    assert len(list((store.path / "originals").glob("*.eml"))) == 1
    assert nc.drafts(store)["counts"] == {"intake-pending": 1}


def test_expired_cursor_and_bounded_run(store):
    nc.fetch(store, Gmail())
    before = store.read("checkpoint.json", {})
    gmail = Gmail(expire=True)
    nc.fetch(store, gmail)
    assert any(call[0] == "messages" for call in gmail.calls)
    bounded = store.read("checkpoint.json", {})
    nc.fetch(store, Gmail(), publication="diesen", since="2026-09-01")
    assert store.read("checkpoint.json", {}) == bounded
    assert before["history_id"] == bounded["history_id"]


def test_interruption_does_not_advance(store):
    with pytest.raises(OSError):
        nc.fetch(store, Gmail(fail=True))
    assert store.read("checkpoint.json", {}) == {}


def test_original_saved_before_processing_failure(store, monkeypatch):
    nc.fetch(store, Gmail())
    monkeypatch.setattr(nc, "parse", lambda *args: (_ for _ in ()).throw(ValueError("bad template")))
    assert nc.drafts(store)["counts"] == {"processing-failed": 1}
    assert store.read("records.json", {})["one"]["status"] == "processing-failed"
    assert len(list((store.path / "originals").glob("*.eml"))) == 1


def archive(store, body):
    rel = "archive/sources/geopolitics/sources/test.md"
    target = store.repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n---\n" + body, encoding="utf-8")
    (store.repo / "archive/sources/geopolitics/source-manifest.json").write_text(json.dumps({"sources": [{"source_url": "https://glenndiesen.substack.com/p/test", "local_path": rel}]}))


def test_duplicate_and_revision(store):
    nc.fetch(store, Gmail())
    archive(store, nc.parse(email(), route(store))["body"])
    assert nc.drafts(store)["counts"] == {"already-landed": 1}
    archive(store, "Earlier version")
    assert nc.drafts(store)["counts"] == {"repair-needed": 1}


def test_land_checks_manifest_and_recovers_retry(store):
    nc.fetch(store, Gmail())
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        if "--dry-run" not in command:
            archive(store, nc.parse(email(), route(store))["body"])
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")
    assert nc.land_ready(store, pilot=True, run=run)["landed"] == ["one"]
    assert len(calls) == 2
    assert nc.land_ready(store, pilot=True, run=run)["landed"] == []
    assert len(calls) == 2


def test_false_landing_success_stops(store):
    nc.fetch(store, Gmail())
    result = nc.land_ready(store, pilot=True, run=lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""))
    assert result["status"] == "partial"
    assert result["failures"][0]["phase"] == "manifest-verification"


def test_routine_gate_and_lock(store):
    assert nc.tower_refresh(store, None)["status"] == "pilot-required"
    with pytest.raises(ValueError, match="disabled"):
        nc.land_ready(store)
    with store.lock():
        with pytest.raises(ValueError, match="locked"):
            with store.lock():
                pass


def test_unavailable_access_keeps_coverage_gap(store):
    store.save("pilot.json", {"passed": True})
    result = nc.tower_refresh(store, None)
    assert result["retrieval"]["status"] == "unavailable"
    assert result["capture"]["gap"]


def test_status_is_read_only_and_private_root_enforced(tmp_path):
    store = nc.Store(tmp_path / "repo", tmp_path / "state")
    assert nc.status(store)["status"] == "not-configured"
    assert not store.path.exists()
    with pytest.raises(ValueError):
        nc.Store(tmp_path, tmp_path / "inside")


def test_integrity_and_wrong_mailbox(store):
    gmail = Gmail()
    gmail.get = lambda *a, **k: {"emailAddress": "other@example.org"}
    with pytest.raises(ValueError, match="dedicated"):
        nc.fetch(store, gmail)
    nc.fetch(store, Gmail())
    original = next((store.path / "originals").glob("*.eml"))
    original.write_bytes(b"changed")
    with pytest.raises(ValueError, match="integrity"):
        nc.drafts(store)


def test_ambiguous_authorship_held(store):
    result = nc.parse(email(sender="The Publication <writer@example.org>"), route(store))
    assert result["status"] == "review-needed"


def test_unapproved_message_body_not_retrieved(store):
    gmail = Gmail()
    original_get = gmail.get
    def get(resource, **params):
        if params.get("format") == "metadata":
            return {"payload": {"headers": [{"name": "From", "value": "private@example.org"}]}}
        return original_get(resource, **params)
    gmail.get = get
    assert nc.fetch(store, gmail)["captured"] == 0
    assert not any(params.get("format") == "raw" for _, params in gmail.calls)


def test_pilot_needs_real_matching_contribution(store, monkeypatch):
    import tower
    nc.fetch(store, Gmail())
    archive(store, nc.parse(email(), route(store))["body"])
    nc.drafts(store)
    source = store.read("records.json", {})["one"]["archive_path"]
    relative = "geopolitics/work/strategy-notebook/contributions/pilot.json"
    target = store.repo / relative
    target.parent.mkdir(parents=True)
    target.write_text('{}')
    contribution = {"path": relative, "source_dispositions": [{"path": source, "version": "wrong", "status": "considered"}]}
    monkeypatch.setattr(tower, "contributions", lambda repo: [contribution])
    with pytest.raises(ValueError, match="matching source"):
        nc.accept_pilot(store, relative)
    contribution["source_dispositions"][0]["version"] = nc.digest((store.repo / source).read_bytes())
    assert nc.accept_pilot(store, relative)["status"] == "pilot-accepted"
    assert nc.status(store)["routine_enabled"]


def test_capture_does_not_write_interpretive_carriers(store):
    nc.fetch(store, Gmail())
    nc.drafts(store)
    assert sorted(path.relative_to(store.repo).as_posix() for path in store.repo.rglob("*") if path.is_file()) == ["archive/sources/geopolitics/source-manifest.json"]
    assert not any(name in path.parts for path in store.path.rglob("*") for name in ("journal", "continuity", "notes", "recursive-learning"))
