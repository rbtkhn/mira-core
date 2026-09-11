"""Mira YouTube front door with youtube-capture compatibility forwarding."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import youtube_capture

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


TERMINAL_STATES = {
    "seeded", "browser-verified", "capture-complete", "transcript-ready",
    "account-action-complete", "blocked", "handoff-ready",
}
RECEIPT_SCHEMA_VERSION = 2
REQUIRED_CANDIDATE_FIELDS = ("video_url", "channel_url", "title", "channel", "date", "format", "duration_seconds")
SURFACES = {"Subscriptions", "Videos", "Live", "Search", "Watch", "Playlist", "History", "Studio"}
EXCLUDED_FORMATS = {"short", "shorts", "clip"}


def load_json_object(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
        raise ValueError(f"not a YouTube URL: {url}")
    if parsed.netloc == "youtu.be":
        value = parsed.path.strip("/")
    else:
        value = parse_qs(parsed.query).get("v", [""])[0]
    if not value:
        raise ValueError(f"URL has no canonical video id: {url}")
    return value


def validate_candidate(candidate: dict, *, min_duration: int = 600) -> list[str]:
    errors = [field for field in REQUIRED_CANDIDATE_FIELDS if field not in candidate]
    if errors:
        return [f"missing candidate fields: {', '.join(errors)}"]
    if not isinstance(candidate["duration_seconds"], int) or candidate["duration_seconds"] < 0:
        return ["duration_seconds must be a nonnegative integer"]
    fmt = str(candidate["format"]).lower()
    reasons: list[str] = []
    if fmt in EXCLUDED_FORMATS:
        reasons.append("short-or-clip")
    if candidate.get("scheduled") or candidate.get("future"):
        reasons.append("scheduled-or-future")
    if candidate.get("duplicate") or candidate.get("already_landed"):
        reasons.append("duplicate-or-already-landed")
    if candidate["duration_seconds"] < min_duration:
        reasons.append("below-minimum-duration")
    return reasons


def validate_research_receipt(payload: dict) -> None:
    state = payload.get("terminal_state")
    if state not in TERMINAL_STATES:
        raise ValueError(f"invalid terminal_state: {state!r}")
    if payload.get("account_identifier") or payload.get("credentials") or payload.get("cookies") or payload.get("tokens"):
        raise ValueError("receipt contains prohibited account data")
    surfaces = payload.get("observed_surfaces", [])
    if not isinstance(surfaces, list) or any(surface not in SURFACES for surface in surfaces):
        raise ValueError("observed_surfaces must contain known surface names")
    access = payload.get("account_access", {})
    if access and (not isinstance(access, dict) or any(not isinstance(access.get(key), bool) for key in ("account_visible", "eligible", "fresh_session_recheck"))):
        raise ValueError("account_access needs boolean account_visible, eligible, and fresh_session_recheck")
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("each candidate must be an object")
        video_id(candidate["video_url"])
        if state == "browser-verified" and validate_candidate(candidate):
            raise ValueError("browser-verified candidates cannot have exclusion or missing evidence")
    coverage = payload.get("coverage", {})
    if state == "browser-verified":
        if not surfaces or not coverage.get("complete"):
            raise ValueError("browser-verified receipt needs complete coverage and observed surfaces")
        if not access or not all(access.get(key) is True for key in ("account_visible", "eligible", "fresh_session_recheck")):
            raise ValueError("browser-verified receipt needs eligible fresh-session account evidence")


def receipt_validate(path: Path) -> int:
    payload = load_json_object(path)
    # Version 1 remains readable, but only version 2 can claim complete evidence.
    if payload.get("schema_version", 1) == 1:
        if payload.get("terminal_state") == "browser-verified":
            raise ValueError("schema v1 receipts cannot claim browser-verified; migrate to schema v2")
        validate_research_receipt({**payload, "observed_surfaces": payload.get("observed_surfaces", [])})
    else:
        if payload.get("schema_version") != RECEIPT_SCHEMA_VERSION:
            raise ValueError("unsupported receipt schema version")
        validate_research_receipt(payload)
    print("MIRA_YOUTUBE_RECEIPT=valid")
    print(f"TERMINAL_STATE={payload.get('terminal_state')}")
    return 0


def comment_capability_validate(path: Path) -> int:
    """Validate a read-only browser capability probe; never posts or edits YouTube."""
    payload = load_json_object(path)
    required = ("account_visible", "watch_page_rendered", "comments_rendered", "composer_present", "submit_control_present")
    missing = [key for key in required if not isinstance(payload.get(key), bool)]
    if missing:
        raise ValueError(f"capability probe needs boolean fields: {', '.join(missing)}")
    if payload.get("posted") is True or payload.get("submitted") is True:
        raise ValueError("capability probe must be read-only")
    status = "ready" if all(payload[key] for key in required) else "unconfirmed"
    print(f"MIRA_YOUTUBE_COMMENT_CAPABILITY={status}")
    for key in required:
        print(f"{key.upper()}={str(payload[key]).lower()}")
    return 0


def triage_command(path: Path, min_duration: int) -> int:
    payload = load_json_object(path)
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    rows = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("each candidate must be an object")
        reasons = validate_candidate(candidate, min_duration=min_duration)
        disposition = "skip" if reasons else candidate.get("disposition", "possible")
        row = dict(candidate)
        row["exclusion_reason"] = ";".join(reasons)
        row["disposition"] = disposition
        row["canonical_url"] = f"https://www.youtube.com/watch?v={video_id(candidate['video_url'])}"
        rows.append(row)
    print(json.dumps({"mode": "triage", "min_duration_seconds": min_duration, "candidates": rows}, indent=2, ensure_ascii=False))
    return 0


def transcript_bundle_preflight(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        raise ValueError("transcript bundle must contain a non-empty items list")
    seen: set[str] = set()
    planned = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each transcript item must be an object")
        url = item.get("video_url", "")
        attachment = Path(item.get("attachment_path", ""))
        ident = video_id(url)
        if ident in seen:
            raise ValueError(f"duplicate transcript video: {ident}")
        seen.add(ident)
        if not attachment.is_file():
            raise ValueError(f"missing transcript attachment: {attachment}")
        if not item.get("title") or not item.get("route"):
            raise ValueError("each transcript item needs title and route")
        planned.append({"video_id": ident, "video_url": f"https://www.youtube.com/watch?v={ident}", "title": item["title"], "route": item["route"], "status": "ready"})
    print(json.dumps({"mode": "transcript-bundle-preflight", "atomic": True, "items": planned}, indent=2, ensure_ascii=False))
    return 0


def mode_command(command: str, path: Path, min_duration: int) -> int:
    if command == "triage":
        return triage_command(path, min_duration)
    payload = load_json_object(path)
    if command in {"discover", "verify", "monitor", "handoff"}:
        if command == "verify":
            validate_research_receipt(payload)
        print(json.dumps({"mode": command, "terminal_state": payload.get("terminal_state", "seeded"), "authority": "browser-evidence-only"}, indent=2))
        return 0
    raise ValueError(f"unsupported mode: {command}")


def main(argv: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    modes = {"discover", "verify", "capture", "triage", "monitor", "handoff", "organize", "creator-ops", "transcript-bundle-preflight"}
    if not values or (values[0] not in {"receipt-validate", "comment-capability-validate", "help"} and values[0] not in modes):
        return youtube_capture.main(values)
    parser = argparse.ArgumentParser(prog="mira-youtube")
    sub = parser.add_subparsers(dest="command")
    validate = sub.add_parser("receipt-validate")
    validate.add_argument("path", type=Path)
    capability = sub.add_parser("comment-capability-validate")
    capability.add_argument("path", type=Path)
    for mode in ("discover", "verify", "triage", "monitor", "handoff"):
        mode_parser = sub.add_parser(mode)
        mode_parser.add_argument("path", type=Path)
        mode_parser.add_argument("--min-duration-seconds", type=int, default=600)
    bundle = sub.add_parser("transcript-bundle-preflight")
    bundle.add_argument("path", type=Path)
    sub.add_parser("capture").add_argument("legacy", nargs=argparse.REMAINDER)
    sub.add_parser("organize")
    sub.add_parser("creator-ops")
    sub.add_parser("help")
    args, legacy = parser.parse_known_args(values)
    if args.command == "receipt-validate":
        try:
            return receipt_validate(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"mira-youtube receipt error: {error}", file=sys.stderr)
            return 1
    if args.command == "comment-capability-validate":
        try:
            return comment_capability_validate(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"mira-youtube capability error: {error}", file=sys.stderr)
            return 1
    if args.command in {"organize", "creator-ops"}:
        print(f"MIRA_YOUTUBE_{args.command.upper().replace('-', '_')}=blocked")
        print("REASON=browser action adapter and action-time confirmation are required")
        return 1
    if args.command == "capture":
        return youtube_capture.main(args.legacy)
    if args.command == "transcript-bundle-preflight":
        try:
            return transcript_bundle_preflight(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"mira-youtube transcript bundle error: {error}", file=sys.stderr)
            return 1
    if args.command in {"discover", "verify", "triage", "monitor", "handoff"}:
        try:
            return mode_command(args.command, args.path, args.min_duration_seconds)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"mira-youtube {args.command} error: {error}", file=sys.stderr)
            return 1
    if args.command == "help":
        parser.print_help()
        print("All other commands forward to youtube-capture.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
