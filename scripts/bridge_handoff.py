"""Private, workspace-bound Bridge inbox. Prompt text is advisory, never executable."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid

from portable_paths import PortablePathError, state_path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 65536


class BridgeError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def workspace(repo):
    return os.path.normcase(str(Path(repo).resolve()))


def inbox(repo=REPO_ROOT, root=None):
    return state_path(f"state/bridge/{digest(workspace(repo))}.json", root=root, repo_root=Path(repo))


def git_state(repo):
    def git(*args):
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
        return result.stdout
    try:
        return {"head": git("rev-parse", "HEAD").decode().strip(),
                "status_digest": hashlib.sha256(git("status", "--porcelain=v1", "-z", "--untracked-files=all")).hexdigest()}
    except (OSError, subprocess.CalledProcessError):
        return {"head": None, "status_digest": None}


def snapshot(repo, refs):
    repo = Path(repo).resolve()
    paths = {}
    for ref in refs:
        path = (repo / ref).resolve()
        if Path(ref).is_absolute() or not path.is_relative_to(repo) or ".git" in Path(ref).parts:
            raise BridgeError("Bridge references must stay inside the workspace and outside .git")
        paths[ref] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {**git_state(repo), "artifacts": paths}


def load(repo=REPO_ROOT, root=None):
    path = inbox(repo, root)
    if not path.exists():
        return None
    if path.stat().st_size > MAX_BYTES:
        raise BridgeError("Bridge record exceeds size limit")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        payload = record["payload"]
        if (record["digest"] != digest(payload) or payload["workspace"] != workspace(repo)
                or payload["schema_version"] != 1 or record["status"] not in {"pending", "resumed"}
                or not isinstance(payload["prompt"], str) or not payload["prompt"].strip()
                or not isinstance(payload["snapshot"]["artifacts"], dict)
                or not {"head", "status_digest", "artifacts"}.issubset(payload["snapshot"])
                or len(payload["snapshot"]["artifacts"]) > 32
                or payload["authority_effect"] != "advisory-only"):
            raise BridgeError("Bridge record integrity or workspace mismatch")
        datetime.fromisoformat(payload["created_at"])
        return record
    except (KeyError, TypeError, ValueError, UnicodeError) as error:
        raise BridgeError("Bridge record is invalid; ordinary Coffee remains available") from error


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise BridgeError("Bridge inbox is busy; no state changed") from error
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def write_record(path, record):
    raw = json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise BridgeError("Bridge record exceeds size limit")
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".bridge-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save(prompt, *, repo=REPO_ROOT, root=None, refs=(), replace_digest=None):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode()) > 32768:
        raise BridgeError("Bridge prompt must contain 1–32768 UTF-8 bytes")
    if len(refs) > 32:
        raise BridgeError("Bridge accepts at most 32 artifact references")
    payload = {"schema_version": 1, "id": uuid.uuid4().hex, "workspace": workspace(repo),
               "created_at": datetime.now(timezone.utc).isoformat(), "prompt": prompt,
               "snapshot": snapshot(repo, refs), "authority_effect": "advisory-only"}
    missing = [ref for ref, value in payload["snapshot"]["artifacts"].items() if value is None]
    if missing:
        raise BridgeError(f"Bridge save references must be existing files: {', '.join(missing)}")
    record = {"payload": payload, "digest": digest(payload), "status": "pending"}
    path = inbox(repo, root)
    with locked(path):
        prior = load(repo, root)
        if prior and prior["status"] == "pending" and prior["digest"] != replace_digest:
            raise BridgeError("Pending Bridge exists; replacement requires its exact digest")
        if replace_digest and (not prior or prior["digest"] != replace_digest):
            raise BridgeError("Bridge changed before replacement; no state changed")
        write_record(path, record)
    return {"status": "pending", "digest": record["digest"], "path": str(path), "authority_effect": "advisory-only"}


def comparison(before, after):
    """Explain snapshot consistency without claiming tests or whole-tree parity."""
    def state(old, new):
        return "unavailable" if old is None or new is None else "match" if old == new else "changed"

    return {
        "head": state(before["head"], after["head"]),
        "status_digest": state(before["status_digest"], after["status_digest"]),
        "status_command": "git status --porcelain=v1 -z --untracked-files=all",
        "artifacts": {
            ref: "missing" if after["artifacts"][ref] is None
            else state(old, after["artifacts"][ref])
            for ref, old in before["artifacts"].items()
        },
        "limits": [
            "Status expands untracked files; counts from default Git status may differ.",
            "Git status is not a content hash of every working-tree file.",
            "Only declared artifact contents are hashed.",
            "Tests, remote state, and claims in the prompt are not verified.",
        ],
    }


def summary(record, repo, *, current_snapshot=None):
    before = record["payload"]["snapshot"]
    after = current_snapshot if current_snapshot is not None else snapshot(repo, before["artifacts"])
    missing = any(value is None for value in after["artifacts"].values())
    freshness = "unavailable" if after["head"] is None else "stale" if missing or before != after else "current"
    return {"status": "pending", "digest": record["digest"], "freshness": freshness,
            "created_at": record["payload"]["created_at"]}


def peek(*, repo=REPO_ROOT, root=None):
    """Bounded metadata only; never copies prompt text to Coffee or its receipts."""
    try:
        record = load(repo, root)
        if not record or record["status"] == "resumed":
            return {"status": "missing"}
        return summary(record, repo)
    except (BridgeError, PortablePathError, OSError):
        return {"status": "unavailable"}


def read(expected_digest, *, repo=REPO_ROOT, root=None):
    record = load(repo, root)
    if not record or record["status"] != "pending" or record["digest"] != expected_digest:
        raise BridgeError("Selected Bridge is no longer pending at that digest; rerun Coffee")
    before = record["payload"]["snapshot"]
    after = snapshot(repo, before["artifacts"])
    return {**summary(record, repo, current_snapshot=after), "prompt": record["payload"]["prompt"],
            "comparison": comparison(before, after),
            "captured_snapshot": record["payload"]["snapshot"], "authority_effect": "advisory-only"}


def acknowledge(expected_digest, *, repo=REPO_ROOT, root=None):
    path = inbox(repo, root)
    with locked(path):
        record = load(repo, root)
        if not record or record["digest"] != expected_digest:
            raise BridgeError("Bridge changed before acknowledgement; no state changed")
        if record["status"] == "pending":
            record["status"] = "resumed"
            record["resumed_at"] = datetime.now(timezone.utc).isoformat()
            write_record(path, record)
    return {"status": "resumed", "digest": expected_digest, "authority_effect": "handoff-receipt-only"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    saving = commands.add_parser("save")
    saving.add_argument("--prompt-file", type=Path, required=True)
    saving.add_argument("--ref", action="append", default=[])
    saving.add_argument("--replace-digest")
    commands.add_parser("peek")
    for name in ("read", "ack"):
        commands.add_parser(name).add_argument("--digest", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "save":
            if args.prompt_file.stat().st_size > 32768:
                raise BridgeError("Bridge prompt file exceeds size limit")
            result = save(args.prompt_file.read_text(encoding="utf-8-sig"), root=args.state_root,
                          refs=args.ref, replace_digest=args.replace_digest)
        elif args.command == "peek":
            result = peek(root=args.state_root)
        else:
            operation = read if args.command == "read" else acknowledge
            result = operation(args.digest, root=args.state_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (BridgeError, PortablePathError, OSError) as error:
        print(json.dumps({"status": "unavailable", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
