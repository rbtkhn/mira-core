from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any
from urllib.parse import urlsplit

from session_preflight import is_within, probe_temp_root


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "2.0"
TEMP_ROOT_ENV = "MIRA_CORE_SESSION_TEMP_ROOT"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VALIDATION_NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
BRANCH_REF = re.compile(r"^refs/heads/(?![./])(?!.*(?:\.\.|//|@\{|\\|\s|[~^:?*\[]))(?!.*[./]$)[A-Za-z0-9._/-]+$")


class PushError(RuntimeError):
    def __init__(self, message: str, *, remote_state_changed: bool | str = False):
        super().__init__(message)
        self.remote_state_changed = remote_state_changed


def run_git(
    repo: Path, *arguments: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def resolve_repo(raw: str | Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise PushError("--repo must be an absolute path")
    candidate = candidate.resolve(strict=True)
    result = run_git(candidate, "rev-parse", "--show-toplevel")
    resolved = Path(result.stdout.strip()).resolve(strict=True)
    if resolved != candidate:
        raise PushError("--repo must name the exact Git repository root")
    return resolved


def validate_source(repo: Path, raw: str) -> str:
    if not FULL_SHA.fullmatch(raw):
        raise PushError("source SHA must be a full 40-character lowercase commit SHA")
    value = raw
    result = run_git(repo, "rev-parse", "--verify", f"{value}^{{commit}}")
    resolved = result.stdout.strip().lower()
    if resolved != value:
        raise PushError("source SHA does not resolve to the exact supplied commit")
    return resolved


def validate_target_ref(raw: str) -> str:
    if not BRANCH_REF.fullmatch(raw) or raw.endswith(".lock"):
        raise PushError("target must be one full safe refs/heads/<branch> ref")
    return raw


def remote_url(repo: Path, remote: str) -> str:
    if not remote or remote.startswith("-") or any(char.isspace() for char in remote):
        raise PushError("remote name is unsafe")
    result = run_git(repo, "remote", "get-url", remote)
    value = result.stdout.strip()
    if not value:
        raise PushError("remote URL is unavailable")
    return value


def sanitize_remote(value: str) -> str:
    if "://" in value:
        parsed = urlsplit(value)
        host = parsed.hostname or "remote"
        leaf = Path(parsed.path.rstrip("/")).name or "repository"
        return f"{host}/{leaf}"
    if re.match(r"^[^/@:]+@[^:]+:", value):
        host, path = value.split(":", 1)
        leaf = Path(path.rstrip("/")).name or "repository"
        return f"{host.split('@', 1)[1]}/{leaf}"
    return f"local/{Path(value).name or 'repository'}"


def advertised_sha(repo: Path, remote: str, target_ref: str) -> str:
    result = run_git(repo, "ls-remote", "--heads", remote, target_ref, check=False)
    if result.returncode != 0:
        raise PushError("remote target state is inaccessible")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return "absent"
    if len(lines) != 1:
        raise PushError("remote target lookup returned multiple refs")
    sha, ref = lines[0].split(maxsplit=1)
    if ref != target_ref or not FULL_SHA.fullmatch(sha.lower()):
        raise PushError("remote target lookup returned malformed evidence")
    return sha.lower()


def fetch_and_classify(
    repo: Path, remote: str, target_ref: str, source_sha: str, observed: str
) -> str:
    if observed == "absent":
        return "new-branch"
    result = run_git(repo, "fetch", "--no-tags", remote, target_ref, check=False)
    if result.returncode != 0:
        raise PushError("exact-target fetch failed; remote freshness is unavailable")
    fetched = run_git(repo, "rev-parse", "FETCH_HEAD").stdout.strip().lower()
    if fetched != observed:
        raise PushError("fetched target does not match advertised remote SHA")
    ancestor = run_git(
        repo, "merge-base", "--is-ancestor", observed, source_sha, check=False
    )
    if ancestor.returncode != 0:
        raise PushError("source commit is not a fast-forward of the remote target")
    return "fast-forward"


def authentication_status(repo: Path, url: str) -> str:
    identity = sanitize_remote(url).lower()
    if not identity.startswith("github.com/"):
        return "not-applicable"
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            cwd=repo,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return "unavailable"
    return "passed" if result.returncode == 0 else "unavailable"


def lfs_status(repo: Path) -> str:
    hook_path = run_git(repo, "config", "--get", "core.hookspath", check=False)
    candidates = []
    if hook_path.returncode == 0 and hook_path.stdout.strip():
        candidates.append((repo / hook_path.stdout.strip() / "pre-push").resolve())
    git_dir = Path(run_git(repo, "rev-parse", "--git-dir").stdout.strip())
    if not git_dir.is_absolute():
        git_dir = repo / git_dir
    candidates.append(git_dir.resolve() / "hooks" / "pre-push")
    requires_lfs = any(
        path.is_file() and "git lfs" in path.read_text(encoding="utf-8", errors="ignore").lower()
        for path in candidates
    )
    if not requires_lfs:
        return "not-required"
    result = subprocess.run(
        ["git", "lfs", "version"],
        cwd=repo,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return "passed" if result.returncode == 0 else "unavailable"


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def receipt_digest(receipt: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def resolve_temp_root(raw: str | Path | None, *, repo: Path) -> Path:
    value = raw or os.environ.get(TEMP_ROOT_ENV)
    if not value:
        raise PushError(f"{TEMP_ROOT_ENV} or --temp-root is required")
    root = Path(value)
    report = probe_temp_root(root, repo_root=repo)
    if not report["writable"] or not report["probe_removed"]:
        raise PushError(str(report["failure"] or "temporary root preflight failed"))
    return Path(report["resolved_root"])


def write_receipt(receipt: dict[str, Any], temp_root: Path) -> Path:
    directory = temp_root / "validated-push"
    directory.mkdir(parents=True, exist_ok=True)
    name = f"check-{receipt['source_sha'][:12]}-{receipt['receipt_digest'][:12]}.json"
    target = directory / name
    descriptor, temporary = tempfile.mkstemp(prefix=".receipt-", suffix=".json", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
        Path(temporary).replace(target)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise
    return target


def validation_evidence(
    *,
    profile: str,
    result: str,
    required_gate: str,
    required_gate_result: str,
    exception_authorized: bool = False,
    exception_basis: str | None = None,
    failure_fingerprint: str | None = None,
    authority_context_digest: str | None = None,
) -> dict[str, Any]:
    for label, value in (("validation profile", profile), ("required gate", required_gate)):
        if not isinstance(value, str) or not VALIDATION_NAME.fullmatch(value):
            raise PushError(f"{label} must be a lowercase safe name")
    if not isinstance(result, str) or not isinstance(required_gate_result, str):
        raise PushError("validation results must be strings")
    if type(exception_authorized) is not bool:
        raise PushError("exception authorization must be boolean")
    for label, value in (
        ("exception basis", exception_basis),
        ("failure fingerprint", failure_fingerprint),
        ("authority context digest", authority_context_digest),
    ):
        if value is not None and not isinstance(value, str):
            raise PushError(f"{label} must be a string when present")
    if result != "passed":
        raise PushError("the recorded validation profile must have passed")
    if required_gate_result not in {"passed", "failed"}:
        raise PushError("required gate result must be passed or failed")
    if profile == required_gate and result != required_gate_result:
        raise PushError("one validation gate cannot have contradictory results")

    basis = exception_basis.strip() if exception_basis else None
    if required_gate_result == "passed":
        if exception_authorized or any(
            value is not None
            for value in (basis, failure_fingerprint, authority_context_digest)
        ):
            raise PushError("a passing required gate must not carry an exception")
    else:
        if not exception_authorized:
            raise PushError("a failed required gate requires an authorized exception")
        if not basis:
            raise PushError("a validation exception requires a non-empty basis")
        if not failure_fingerprint or not SHA256.fullmatch(failure_fingerprint):
            raise PushError("a validation exception requires a lowercase SHA-256 failure fingerprint")
        if not authority_context_digest or not SHA256.fullmatch(authority_context_digest):
            raise PushError("a validation exception requires a lowercase SHA-256 authority context digest")

    return {
        "profile": profile,
        "result": result,
        "required_gate": required_gate,
        "required_gate_result": required_gate_result,
        "exception_authorized": exception_authorized,
        "exception_basis": basis,
        "failure_fingerprint": failure_fingerprint,
        "authority_context_digest": authority_context_digest,
    }


def build_check_receipt(
    *, repo: Path, remote: str, source_sha: str, target_ref: str,
    validation_profile: str, validation_result: str, required_gate: str,
    required_gate_result: str, temp_root: Path,
    exception_authorized: bool = False, exception_basis: str | None = None,
    failure_fingerprint: str | None = None,
    authority_context_digest: str | None = None,
) -> tuple[dict[str, Any], Path]:
    validation = validation_evidence(
        profile=validation_profile,
        result=validation_result,
        required_gate=required_gate,
        required_gate_result=required_gate_result,
        exception_authorized=exception_authorized,
        exception_basis=exception_basis,
        failure_fingerprint=failure_fingerprint,
        authority_context_digest=authority_context_digest,
    )
    source = validate_source(repo, source_sha)
    target = validate_target_ref(target_ref)
    url = remote_url(repo, remote)
    authentication = authentication_status(repo, url)
    lfs = lfs_status(repo)
    if authentication == "unavailable":
        raise PushError("GitHub authentication is unavailable")
    if lfs == "unavailable":
        raise PushError("required Git LFS support is unavailable")
    observed = advertised_sha(repo, remote, target)
    update_kind = fetch_and_classify(repo, remote, target, source, observed)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "validated-push-check",
        "repository": str(repo),
        "remote": remote,
        "remote_identity": sanitize_remote(url),
        "source_sha": source,
        "target_ref": target,
        "observed_remote_sha": observed,
        "update_kind": update_kind,
        "authentication": authentication,
        "freshness": "passed",
        "lfs": lfs,
        "validation": validation,
        "authority_effect": "none",
    }
    receipt["receipt_digest"] = receipt_digest(receipt)
    path = write_receipt(receipt, temp_root)
    return receipt, path


def load_receipt(path: Path, *, temp_root: Path, repo_root: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    if not is_within(resolved, temp_root.resolve(strict=True)):
        raise PushError("receipt is outside the approved external temporary root")
    if is_within(resolved, repo_root.resolve(strict=True)):
        raise PushError("receipt must not be stored inside the repository")
    try:
        receipt = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PushError(f"receipt is unreadable: {error}") from error
    if not isinstance(receipt, dict) or receipt.get("kind") != "validated-push-check":
        raise PushError("receipt kind is invalid")
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise PushError("receipt schema version is invalid")
    if receipt.get("receipt_digest") != receipt_digest(receipt):
        raise PushError("receipt digest mismatch")
    return receipt


def execute_push(receipt: dict[str, Any]) -> dict[str, Any]:
    required = {
        "repository", "remote", "source_sha", "target_ref", "observed_remote_sha",
        "schema_version", "validation", "freshness", "authentication", "lfs",
    }
    if not required <= set(receipt):
        raise PushError("receipt is missing required fields")
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise PushError("receipt schema version is invalid")
    raw_validation = receipt["validation"]
    if not isinstance(raw_validation, dict):
        raise PushError("receipt validation evidence is invalid")
    try:
        validation_evidence(
            profile=raw_validation["profile"],
            result=raw_validation["result"],
            required_gate=raw_validation["required_gate"],
            required_gate_result=raw_validation["required_gate_result"],
            exception_authorized=raw_validation["exception_authorized"],
            exception_basis=raw_validation["exception_basis"],
            failure_fingerprint=raw_validation["failure_fingerprint"],
            authority_context_digest=raw_validation["authority_context_digest"],
        )
    except (KeyError, TypeError) as error:
        raise PushError("receipt validation evidence is incomplete") from error
    if receipt["freshness"] != "passed":
        raise PushError("receipt does not prove freshness")
    repo = resolve_repo(receipt["repository"])
    source = validate_source(repo, receipt["source_sha"])
    target = validate_target_ref(receipt["target_ref"])
    url = remote_url(repo, receipt["remote"])
    if sanitize_remote(url) != receipt.get("remote_identity"):
        raise PushError("remote identity changed after check")
    observed = advertised_sha(repo, receipt["remote"], target)
    if observed != receipt["observed_remote_sha"]:
        raise PushError("remote target changed after check; push not attempted")
    fetch_and_classify(repo, receipt["remote"], target, source, observed)
    result = run_git(
        repo, "push", receipt["remote"], f"{source}:{target}", check=False
    )
    if result.returncode != 0:
        raise PushError(
            "exact-refspec push failed; remote success is unproven",
            remote_state_changed="unknown",
        )
    verified = advertised_sha(repo, receipt["remote"], target)
    if verified != source:
        raise PushError(
            "post-push remote SHA does not equal the intended source SHA",
            remote_state_changed="unknown",
        )
    return {
        "status": "pushed-and-verified",
        "repository": str(repo),
        "remote": receipt["remote"],
        "remote_identity": receipt["remote_identity"],
        "source_sha": source,
        "target_ref": target,
        "verified_remote_sha": verified,
        "authority_effect": "none-beyond-exact-push",
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Check and execute one exact verified Git push.")
    commands = value.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--repo", required=True)
    check.add_argument("--remote", required=True)
    check.add_argument("--source-sha", required=True)
    check.add_argument("--target-ref", required=True)
    check.add_argument("--validation-profile", required=True)
    check.add_argument("--validation-result", required=True, choices=("passed", "failed"))
    check.add_argument("--required-gate", required=True)
    check.add_argument("--required-gate-result", required=True, choices=("passed", "failed"))
    check.add_argument("--exception-authorized", action="store_true")
    check.add_argument("--exception-basis")
    check.add_argument("--failure-fingerprint")
    check.add_argument("--authority-context-digest")
    check.add_argument("--temp-root")
    check.add_argument("--json", action="store_true")
    push = commands.add_parser("push")
    push.add_argument("--receipt", required=True, type=Path)
    push.add_argument("--temp-root")
    push.add_argument("--json", action="store_true")
    return value


def failure_payload(error: Exception) -> dict[str, Any]:
    return {
        "status": "blocked",
        "blocker": str(error),
        "remote_state_changed": getattr(error, "remote_state_changed", False),
        "authority_effect": "none",
    }


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        if args.command == "check":
            repo = resolve_repo(args.repo)
            temp_root = resolve_temp_root(args.temp_root, repo=repo)
            receipt, path = build_check_receipt(
                repo=repo,
                remote=args.remote,
                source_sha=args.source_sha,
                target_ref=args.target_ref,
                validation_profile=args.validation_profile,
                validation_result=args.validation_result,
                required_gate=args.required_gate,
                required_gate_result=args.required_gate_result,
                temp_root=temp_root,
                exception_authorized=args.exception_authorized,
                exception_basis=args.exception_basis,
                failure_fingerprint=args.failure_fingerprint,
                authority_context_digest=args.authority_context_digest,
            )
            payload = {**receipt, "receipt_path": str(path)}
        else:
            raw = json.loads(args.receipt.resolve(strict=True).read_text(encoding="utf-8"))
            repo = resolve_repo(raw.get("repository", ""))
            temp_root = resolve_temp_root(args.temp_root, repo=repo)
            receipt = load_receipt(args.receipt, temp_root=temp_root, repo_root=repo)
            payload = execute_push(receipt)
        print(json.dumps(payload, indent=2))
        return 0
    except (OSError, subprocess.SubprocessError, PushError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps(failure_payload(error), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
