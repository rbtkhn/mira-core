"""Private, retryable newsletter capture. No implicit source or memory admission."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from portable_paths import state_path, require_private_path

REPO = Path(__file__).resolve().parents[1]
SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
MAILBOX = "mira@grace-mar.com"
SEEDS = {
    "mate": "https://www.aaronmate.net", "parsi": "https://tritaparsi.substack.com",
    "johnson": "https://larrycjohnson.substack.com", "crooke": "https://conflictsforum.substack.com",
    "pape": "https://escalationtrap.substack.com", "innermost-loop": "https://theinnermostloop.substack.com",
    "krainer": "https://alexkrainer.substack.com", "ritter": "https://scottritter.substack.com",
    "blumenthal": "https://thegrayzone.substack.com", "macgregor": "https://macgregorwarrior.substack.com",
    "diesen": "https://glenndiesen.substack.com",
}
AUTHORS = {"mate": "Aaron Maté", "parsi": "Trita Parsi", "johnson": "Larry Johnson",
           "crooke": "Alastair Crooke", "pape": "Robert Pape", "innermost-loop": "Alex Wissner-Gross",
           "krainer": "Alex Krainer", "ritter": "Scott Ritter", "blumenthal": "Max Blumenthal",
           "macgregor": "Douglas Macgregor", "diesen": "Glenn Diesen"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc)


def canonical(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        return ""
    return urlunsplit(("https", parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Store:
    def __init__(self, repo=REPO, root=None):
        self.repo = Path(repo)
        self.path = state_path("newsletters/" + digest(str(self.repo.resolve()).encode())[:16], root=root, repo_root=self.repo)

    def read(self, name, default):
        path = self.path / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

    def save(self, name, value):
        write(self.path / name, value)

    @contextmanager
    def lock(self):
        self.path.mkdir(parents=True, exist_ok=True)
        path = self.path / "capture.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise ValueError("Capture is locked; inspect the recorded process before recovering a stale lock") from None
        try:
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            yield
        finally:
            path.unlink()


class ArticleHTML(HTMLParser):
    """Extract only the reviewed article container; never fetch resources."""
    def __init__(self, article_class):
        super().__init__(convert_charrefs=True)
        self.article_class = article_class
        self.depth = 0
        self.found = 0
        self.parts = []
        self.links = []
        self.suppressed = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href") and (self.depth or "post-title" in attrs.get("class", "").split()):
            self.links.append(attrs["href"])
        if self.depth:
            if tag not in {"br", "img", "hr", "input", "meta", "link"}:
                self.depth += 1
        elif self.article_class in attrs.get("class", "").split():
            self.depth = 1
            self.found += 1
        if self.depth:
            if tag in {"script", "style"}:
                self.suppressed += 1
            if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "blockquote"}:
                self.parts.append("\n")
            if tag == "a" and attrs.get("href"):
                self.parts.append(" [" + attrs["href"] + "] ")

    def handle_endtag(self, tag):
        if self.depth:
            if tag in {"script", "style"} and self.suppressed:
                self.suppressed -= 1
            if tag in {"p", "div", "li", "h1", "h2", "h3", "blockquote"}:
                self.parts.append("\n")
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and not self.suppressed:
            self.parts.append(data)


def parse(raw, route):
    message = BytesParser(policy=policy.default).parsebytes(raw)
    sender = parseaddr(str(message.get("From", "")))[1].lower()
    result = {"sender": sender, "message_id": str(message.get("Message-ID", "")),
              "list_id": str(message.get("List-ID", "")), "title": str(message.get("Subject", "")),
              "author": parseaddr(str(message.get("From", "")))[0], "extraction_version": 1,
              "status": "review-needed", "body": "", "url": "", "publication_date": ""}
    try:
        result["publication_date"] = parsedate_to_datetime(str(message["Date"])).date().isoformat()
    except (ValueError, TypeError, KeyError):
        pass
    html = message.get_body(preferencelist=("html",))
    text = message.get_body(preferencelist=("plain",))
    html_body = html.get_content() if html else ""
    plain = text.get_content() if text else ""
    parser = ArticleHTML(route.get("article_class", "body"))
    parser.feed(html_body)
    urls = [canonical(link) for link in parser.links + re.findall(r'https://[^\s<>"\)]+', plain)]
    candidates = sorted({url for url in urls if url and urlsplit(url).hostname == urlsplit(route["url"]).hostname and "/p/" in urlsplit(url).path})
    result["candidate_urls"] = candidates
    if len(candidates) == 1:
        result["url"] = candidates[0]
    body = "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())
    result["body"] = body
    result["body_sha256"] = digest(body.encode())
    combined = (result["title"] + "\n" + plain + "\n" + html_body).lower()
    if re.search(r"^(welcome|confirm your|verify your|your subscription|subscription confirmed)", result["title"], re.I):
        result["status"] = "excluded"
    elif any(term in combined for term in ("this post is for paid subscribers", "subscribe to keep reading", "upgrade to continue", "continue reading with a", "paid episode", "preview of", "you're reading a preview", "you’re reading a preview")):
        result["status"] = "acquisition-pending"
    elif any(term in combined for term in ("watch now", "listen now", "new video", "new episode")):
        result["status"] = "acquisition-pending"
    elif re.search(r"^(special offer|upgrade|discount|sale|gift a subscription)", result["title"], re.I):
        result["status"] = "excluded"
    elif route.get("validated") and sender == route.get("sender") and result["list_id"] == route.get("list_id") and parser.found == 1 and len(body.split()) >= 100 and result["url"] and result["publication_date"] and result["author"].casefold() == route.get("author", "").casefold():
        result["status"] = "intake-pending" if route.get("lane") == "geopolitics" else "singularity-pending"
    result["completeness"] = "complete-by-reviewed-template" if result["status"] in {"intake-pending", "singularity-pending"} else "unconfirmed"
    return result


class Gmail:
    def __init__(self, credentials):
        path = require_private_path(credentials, label="Gmail credentials")
        value = json.loads(path.read_text(encoding="utf-8"))
        if set(value.get("scopes", [])) != {SCOPE}:
            raise ValueError("Credentials must declare only gmail.readonly")
        data = urlencode({"client_id": value["client_id"], "client_secret": value["client_secret"],
                          "refresh_token": value["refresh_token"], "grant_type": "refresh_token"}).encode()
        try:
            with urlopen(Request("https://oauth2.googleapis.com/token", data=data), timeout=30) as response:
                token = json.load(response)
        except HTTPError:
            raise ValueError("Gmail authorization refresh failed; reconnect the dedicated mailbox") from None
        if token.get("scope") and set(token["scope"].split()) != {SCOPE}:
            raise ValueError("Gmail token grants unexpected scopes")
        self.token = token["access_token"]

    def get(self, resource, **params):
        url = "https://gmail.googleapis.com/gmail/v1/users/me/" + resource + "?" + urlencode(params, doseq=True)
        with urlopen(Request(url, headers={"Authorization": "Bearer " + self.token}), timeout=30) as response:
            return json.load(response)

    def pages(self, resource, **params):
        while True:
            page = self.get(resource, **params)
            yield page
            if not page.get("nextPageToken"):
                break
            params["pageToken"] = page["nextPageToken"]


def fetch(store, gmail, publication=None, since=None, until=None):
    profile = gmail.get("profile")
    if profile.get("emailAddress", "").lower() != MAILBOX:
        raise ValueError("Gmail account is not the dedicated Mira mailbox")
    checkpoint = store.read("checkpoint.json", {})
    routes = store.read("routes.json", {})
    selected = {k: v for k, v in routes.items() if v.get("validated") and (not publication or k == publication)}
    if not selected:
        raise ValueError("No validated publication routes; run the supervised seed review")
    run_start = now()
    ids = set()
    incremental = bool(checkpoint.get("history_id")) and not (publication or since or until)
    if incremental:
        try:
            for page in gmail.pages("history", startHistoryId=checkpoint["history_id"], historyTypes="messageAdded"):
                ids.update(item["message"]["id"] for event in page.get("history", []) for item in event.get("messagesAdded", []))
        except HTTPError as error:
            if error.code != 404:
                raise
            incremental = False
    if not incremental:
        lower = datetime.fromisoformat(since).replace(tzinfo=timezone.utc) if since else datetime.fromisoformat(checkpoint["retrieved_at"]) - timedelta(hours=48) if checkpoint else run_start - timedelta(days=7)
        query = "after:" + str(int(lower.timestamp()))
        if until:
            query += " before:" + str(int(datetime.fromisoformat(until).replace(tzinfo=timezone.utc).timestamp()))
        query += " {" + " ".join("from:" + route["sender"] for route in selected.values()) + "}"
        for page in gmail.pages("messages", q=query):
            ids.update(row["id"] for row in page.get("messages", []))
    records = store.read("records.json", {})
    captured = 0
    for identifier in sorted(ids):
        if identifier in records:
            continue
        metadata = gmail.get("messages/" + identifier, format="metadata", metadataHeaders=["From", "List-ID"])
        headers = {item["name"].lower(): item["value"] for item in metadata.get("payload", {}).get("headers", [])}
        header_sender = parseaddr(headers.get("from", ""))[1].lower()
        if not any(route["sender"] == header_sender and route.get("list_id") == headers.get("list-id", "") for route in selected.values()):
            continue
        response = gmail.get("messages/" + identifier, format="raw")
        raw = base64.urlsafe_b64decode(response["raw"] + "===")
        message = BytesParser(policy=policy.default).parsebytes(raw)
        sender = parseaddr(str(message.get("From", "")))[1].lower()
        matches = [(key, route) for key, route in selected.items() if route["sender"] == sender and route.get("list_id") == str(message.get("List-ID", ""))]
        if len(matches) != 1:
            continue
        key, route = matches[0]
        file_key = digest(identifier.encode())
        store.save("originals/" + file_key + ".eml", raw)
        records[identifier] = {"publication": key, "original": "originals/" + file_key + ".eml", "raw_sha256": digest(raw), "received_at": datetime.fromtimestamp(int(response["internalDate"]) / 1000, timezone.utc).isoformat(), "status": "captured"}
        store.save("records.json", records)
        captured += 1
    if not (publication or since or until):
        store.save("checkpoint.json", {"history_id": profile["historyId"], "retrieved_at": run_start.isoformat()})
    return {"status": "retrieved", "captured": captured, "scanned": len(ids)}


def approve_route(store, publication, sample, article_class):
    if not publication or not article_class or not re.fullmatch(r"[A-Za-z0-9_-]+", article_class):
        raise ValueError("Publication and reviewed article class are required")
    sample = require_private_path(sample, label="Review email", repo_root=store.repo)
    raw = sample.read_bytes()
    message = BytesParser(policy=policy.default).parsebytes(raw)
    sender = parseaddr(str(message.get("From", "")))[1].lower()
    list_id = str(message.get("List-ID", ""))
    if not re.fullmatch(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+", sender) or not list_id:
        raise ValueError("A concrete sender and List-ID are required")
    route = {"url": SEEDS[publication], "sender": sender, "list_id": list_id,
             "article_class": article_class, "voice": publication, "author": AUTHORS[publication],
             "lane": "singularity" if publication == "innermost-loop" else "geopolitics",
             "validated": True, "sample_sha256": digest(raw), "reviewed_at": now().isoformat()}
    result = parse(raw, route)
    if result["status"] not in {"intake-pending", "singularity-pending"}:
        raise ValueError("Sample is not a complete, attributable article under this template")
    routes = store.read("routes.json", {})
    routes[publication] = route
    store.save("routes.json", routes)
    store.save("review-samples/" + digest(raw) + ".eml", raw)
    # A new route changes coverage; rescan the initial window next time.
    store.save("checkpoint.json", {})
    store.save("pilot.json", {"passed": False, "reason": "Route changed; supervised pilot required"})
    return {"status": "route-reviewed", "publication": publication}


def drafts(store, publication=None, since=None, until=None):
    records = store.read("records.json", {})
    routes = store.read("routes.json", {})
    manifest = json.loads((store.repo / "archive/sources/geopolitics/source-manifest.json").read_text(encoding="utf-8-sig"))
    archived = {canonical(row.get("source_url", "")): row for row in manifest["sources"] if row.get("source_url")}
    seen = {}
    for identifier, record in records.items():
        if publication and record["publication"] != publication:
            continue
        day = record["received_at"][:10]
        if (since and day < since) or (until and day >= until):
            continue
        raw = (store.path / record["original"]).read_bytes()
        if digest(raw) != record["raw_sha256"]:
            raise ValueError("Original integrity mismatch")
        try:
            result = parse(raw, routes[record["publication"]])
        except (ValueError, KeyError, LookupError, TypeError):
            record["status"] = "processing-failed"
            record.pop("intake_arguments", None)
            continue
        body = result.pop("body")
        record.update(result)
        url = result["url"]
        if url in archived:
            row = archived[url]
            rel = Path(row["local_path"])
            target = (store.repo / rel).resolve()
            if rel.is_absolute() or not target.is_relative_to(store.repo.resolve()) or not target.exists():
                record["status"] = "blocked"
            else:
                # Intake preserves source text; exact inclusion permits crash recovery.
                record["status"] = "already-landed" if body and body in target.read_text(encoding="utf-8-sig") else "repair-needed"
                record["archive_path"] = rel.as_posix()
        elif url and url in seen:
            record["status"] = "duplicate" if seen[url] == result["body_sha256"] else "repair-needed"
        elif url:
            seen[url] = result["body_sha256"]
        if record["status"] == "intake-pending":
            body_path = store.path / "bodies" / (digest(identifier.encode()) + ".txt")
            write(body_path, body.encode())
            route = routes[record["publication"]]
            record["intake_arguments"] = ["--pub-date", result["publication_date"], "--ingest-date", now().date().isoformat(), "--url", url, "--title", result["title"], "--body-file", str(body_path), "--voice-slug", route["voice"], "--host-slug", record["publication"], "--source-form", "newsletter", "--modality", "newsletter", "--kind", "source-text", "--source-class", "authored newsletter", "--trim-opening", "none", "--asr-repair", "none", "--sectioning", "none"]
        else:
            record.pop("intake_arguments", None)
    store.save("records.json", records)
    return status(store)


def status(store):
    records = store.read("records.json", {})
    counts = {}
    items = []
    for key, record in records.items():
        counts[record["status"]] = counts.get(record["status"], 0) + 1
        items.append({"capture_id": key, **{k: v for k, v in record.items() if k not in {"sender", "message_id", "list_id", "original"}}})
    return {"status": "available" if (store.path / "routes.json").exists() else "not-configured", "routine_enabled": store.read("pilot.json", {}).get("passed", False), "counts": counts, "items": items, "last_retrieval": store.read("checkpoint.json", {}).get("retrieved_at"), "gap": store.read("failure.json", {}).get("reason")}


def land_ready(store, publication=None, since=None, until=None, pilot=False, run=subprocess.run):
    if not pilot and not store.read("pilot.json", {}).get("passed"):
        raise ValueError("Routine admission disabled until supervised pilot passes; use --pilot only for supervised work")
    drafts(store, publication, since, until)
    records = store.read("records.json", {})
    landed, failures = [], []
    for identifier, record in records.items():
        day = record["received_at"][:10]
        if (publication and record["publication"] != publication) or (since and day < since) or (until and day >= until):
            continue
        if record["status"] != "intake-pending":
            continue
        command = [sys.executable, str(store.repo / "scripts/land_best_intake.py"), *record["intake_arguments"]]
        preview = run(command + ["--dry-run"], cwd=store.repo, capture_output=True, text=True, encoding="utf-8")
        if preview.returncode:
            failures.append({"capture_id": identifier, "phase": "dry-run", "exit_code": preview.returncode})
            continue
        # Retain the dry-run for supervised inspection; source metadata is explicit.
        store.save("intake-receipts/" + digest(identifier.encode()) + "-preview.txt", preview.stdout.encode())
        result = run(command, cwd=store.repo, capture_output=True, text=True, encoding="utf-8")
        store.save("intake-receipts/" + digest(identifier.encode()) + "-result.txt", (result.stdout + result.stderr).encode())
        drafts(store)
        current = store.read("records.json", {})[identifier]
        if current["status"] != "already-landed":
            failures.append({"capture_id": identifier, "phase": "manifest-verification", "exit_code": result.returncode})
            # A parity failure stops the shared manifest writer.
            break
        landed.append(identifier)
    return {"status": "partial" if failures else "landed", "landed": landed, "failures": failures}


def accept_pilot(store, notebook_ref):
    relative = Path(notebook_ref)
    target = (store.repo / relative).resolve()
    if relative.is_absolute() or not target.is_relative_to(store.repo.resolve()):
        raise ValueError("Pilot requires a repository-relative Tower contribution")
    import tower
    contribution = next((row for row in tower.contributions(store.repo) if row["path"] == relative.as_posix()), None)
    if not contribution or contribution.get("disposition_only"):
        raise ValueError("Pilot requires a valid substantive Tower contribution")
    records = store.read("records.json", {})
    matched = []
    for row in records.values():
        if row.get("status") != "already-landed":
            continue
        source = store.repo / row["archive_path"]
        if any(item["path"] == row["archive_path"] and item["version"] == digest(source.read_bytes()) and item["status"] == "considered" for item in contribution.get("source_dispositions", [])):
            matched.append(row["archive_path"])
    if not matched:
        raise ValueError("Pilot contribution has no considered newsletter with a matching source version")
    store.save("pilot.json", {"passed": True, "accepted_at": now().isoformat(), "contribution": relative.as_posix(), "contribution_sha256": digest(target.read_bytes()), "sources": matched})
    return {"status": "pilot-accepted", "sources": matched}


def tower_refresh(store, credentials, **filters):
    """Called only after direct-owner context has been consumed, never by status."""
    if not store.read("pilot.json", {}).get("passed"):
        return {"status": "pilot-required", "capture": status(store)}
    with store.lock():
        try:
            fetched = fetch(store, Gmail(credentials), **filters)
            store.save("failure.json", {})
        except (OSError, ValueError, KeyError, TypeError):
            store.save("failure.json", {"reason": "Mailbox refresh unavailable; newsletter coverage incomplete", "at": now().isoformat()})
            fetched = {"status": "unavailable"}
        admitted = land_ready(store, **filters)
        return {"retrieval": fetched, "admission": admitted, "capture": status(store)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["status", "fetch", "intake-draft", "seed-review", "approve-route", "land-ready", "accept-pilot", "tower-refresh"])
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--credentials", type=Path)
    parser.add_argument("--publication", choices=sorted(SEEDS))
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--sample", type=Path)
    parser.add_argument("--article-class")
    parser.add_argument("--notebook-ref")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    store = Store(root=args.state_root)
    try:
        if args.command == "status":
            result = status(store)
        elif args.command == "seed-review":
            result = {"status": "review-required", "candidates": SEEDS, "instructions": "Inspect a real email per publication; configure private routes.json using the authentication reference. No inferred sender is enabled."}
        elif args.command == "tower-refresh":
            result = tower_refresh(store, args.credentials, publication=args.publication, since=args.since, until=args.until)
        else:
            with store.lock():
                if args.command == "fetch":
                    if not args.credentials:
                        raise ValueError("Gmail credentials unavailable; see newsletter-capture authentication reference")
                    result = fetch(store, Gmail(args.credentials), args.publication, args.since, args.until)
                    store.save("failure.json", {})
                elif args.command == "approve-route":
                    if not args.sample:
                        raise ValueError("--sample is required")
                    result = approve_route(store, args.publication, args.sample, args.article_class)
                elif args.command == "land-ready":
                    result = land_ready(store, args.publication, args.since, args.until, args.pilot)
                elif args.command == "accept-pilot":
                    if not args.notebook_ref:
                        raise ValueError("--notebook-ref is required")
                    result = accept_pilot(store, args.notebook_ref)
                else:
                    result = drafts(store, args.publication, args.since, args.until)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        # Never print HTTP bodies, tokens, message contents, or credential values.
        reason = "Gmail request failed" if isinstance(error, HTTPError) else str(error)
        parser.exit(1, "newsletter-capture: " + reason + "\n")


if __name__ == "__main__":
    main()
