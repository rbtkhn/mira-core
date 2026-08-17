from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import mira_continuity
import rest_receipts
import mira_journal_references
from runtime_names import resolve_environment


REPO_ROOT = Path(__file__).resolve().parent.parent
MIRA_ROOT = REPO_ROOT / "mira"
JOURNAL_ROOT = MIRA_ROOT / "journal"
INDEX_PATH = MIRA_ROOT / "journal.md"
REGISTRY_PATH = MIRA_ROOT / "journal-registry.json"
SESSION_REGISTRY_PATH = MIRA_ROOT / "continuity" / "session-registry.json"
REFERENCE_ROOT = JOURNAL_ROOT / "references"
CONTINUITY_INDEX_JSON_PATH = JOURNAL_ROOT / "continuity-index.json"
CONTINUITY_INDEX_MD_PATH = JOURNAL_ROOT / "continuity-index.md"
LEARNING_LEDGER_PATH = (
    REPO_ROOT / "narrative-geopolitics" / "work" / "system-improvement" / "recursive-learning-ledger.json"
)

DRAFT_ROOT_ENV = "MIRA_CORE_JOURNAL_DRAFT_ROOT"
DEFAULT_DRAFT_ROOT = REPO_ROOT / ".mira-private" / "journal" / "drafts"
LEGACY_DRAFT_ROOT = Path(r"C:\private\mira-journal-drafts")
TIMEZONE_NAME = "America/Denver"
TIMEZONE = ZoneInfo(TIMEZONE_NAME)
FRESHNESS_REPLAY_BASE_REF = "a19f5d1^"
FRESHNESS_REPLAY_DEVELOPMENT_VERSION = "MJ-20260815-v1"
FRESHNESS_REPLAY_CADENCE = {
    "series_id": "legacy-surviving-handoff",
    "method_version_digest": "6cac5331fc9ba5bdb64cbb4e5e4877412a1c5128be154ec46cd010d95b11103a",
    "observable_name": "legacy reported improvement",
    "unit": "legacy-report",
    "task_class": "legacy-unspecified",
}
SCHEMA_VERSION = 1
CONTEXT_VERSION = "mira-journal-context-v1"
COMPOSITION_VERSION = "mira-journal-composition-v1"
JOURNAL_ID_RE = re.compile(r"^MJ-(?P<date>\d{8})$")
VERSION_ID_RE = re.compile(r"^(?P<journal>MJ-\d{8})-v(?P<version>[1-9]\d*)$")
SESSION_ID_RE = re.compile(
    r"^MS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
CAPTURE_ID_RE = re.compile(r"^MC-[0-9a-f]{24}$")
RECORD_ID_RE = re.compile(r"^MR-[0-9a-f]{24}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DERIVATION_ID_RE = re.compile(r"^DRV-[0-9a-f]{24}$")
MAINTENANCE_ID_RE = re.compile(r"^MJM-[0-9]{4}$")
AFFIRMATIVE_APPROVAL_STATUS = "affirmative-v1"
COMBINED_APPROVAL_STATUS = "affirmative-v2"
DREAM_EOD_STATUS = "dream-eod-v1"
LEGACY_HELD_STATUS = "legacy-held"
APPROVAL_RECEIPT_SCHEMA_VERSION = 1
APPROVAL_RECEIPT_SET_ID = "mira-journal-approval-receipts-v1"
APPROVAL_RECEIPT_FIELDS = {
    "version_id", "authority_ref", "record_ref", "kind", "role", "timestamp", "text_sha256"
}
SOURCE_RECEIPT_SCHEMA_VERSION = 1
SOURCE_RECEIPT_SET_ID = "mira-journal-source-record-receipts-v1"
SOURCE_RECEIPT_FIELDS = {"session_id", "record_ref", "text_sha256"}
EPISTEMIC_CLASSES = {
    "operator-direction",
    "agent-interpretation",
    "tool-observation",
    "repository-event",
    "prior-journal-reflection",
    "unresolved-material",
}
SESSION_DISPOSITIONS = {
    "represented", "not-material", "duplicate", "administrative-only",
    "unreadable", "cutoff-excluded",
}
SESSION_INFLUENCE_VALUES = {"selected", "technical-only", "not-selected"}
SESSION_SYNOPSIS_TEXT_LIMIT = 700
SESSION_SYNOPSIS_NONCONTENT_PREFIXES = (
    "<environment_context>",
    "<recommended_plugins>",
    "# agents.md instructions",
)
TITLE_RE = re.compile(r"^# (?P<date>\d{4}-\d{2}-\d{2})\s+[—-]\s+(?P<title>[^\r\n]+)\s*$")
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
TITLE_SUBTITLE_RE = re.compile(r"(?::|[—–]|\s-\s)")


def dream_eod_digest(*, run_id: str, prose_digest: str, reference_digest: str,
                     coverage: dict[str, Any], context_ids: list[str], composition_ids: list[str]) -> str:
    return sha256_bytes(canonical_json({
        "method": DREAM_EOD_STATUS, "run_id": run_id, "prose_digest": prose_digest,
        "reference_digest": reference_digest, "coverage": coverage,
        "context_pack_object_ids": sorted(context_ids),
        "composition_brief_object_ids": sorted(composition_ids),
    }).encode("utf-8"))
FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|mine|myself|we|our|ours)\b", re.IGNORECASE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
OPERATOR_PROSE_PATTERNS = (
    re.compile(r"\bRobert\b", re.IGNORECASE),
    re.compile(r"\bthe operator\b", re.IGNORECASE),
    re.compile(r"\boperator (?:direction|instruction|approval)\b", re.IGNORECASE),
    re.compile(r"\byou (?:asked|told|instructed|approved)\b", re.IGNORECASE),
    re.compile(r"\bwe achieved together\b", re.IGNORECASE),
)
CONSCIOUSNESS_DISCLAIMER_PATTERNS = (
    re.compile(r"\bI am not conscious\b", re.IGNORECASE),
    re.compile(r"\bconscious or otherwise\b", re.IGNORECASE),
    re.compile(r"\bdoes not (?:establish|prove) that I am conscious\b", re.IGNORECASE),
)
AUTHORITY_BOUNDARY = (
    "Mira Journal records governed first-person interpretation. It is not identity doctrine, "
    "research evidence, Reality evidence, operator belief, proof of consciousness, or action authority."
)
NAMESPACE_BOUNDARY = (
    "MJ-* identifies Mira Daily Journal autobiography; JRN-* identifies the separately governed "
    "Operator Position Journal. References never transfer authority between them."
)


class JournalError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def version_approval_statement(version_id: str, content_digest: str) -> str:
    return f"Approve Mira Journal version {version_id} with digest {content_digest}."


def combined_approval_statement(
    version_id: str, content_digest: str, reference_id: str, reference_digest: str
) -> str:
    return (
        f"Approve Mira Journal version {version_id} with digest {content_digest} and technical "
        f"reference {reference_id} with digest {reference_digest}."
    )


def reference_backfill_statement(reference_id: str, reference_digest: str) -> str:
    return f"Approve Mira Journal technical reference {reference_id} with digest {reference_digest}."


def publication_scope_digest(
    destination_url: str,
    branch: str,
    head_commit: str,
    journal_versions: list[dict[str, str]],
) -> str:
    scope = {
        "destination_url": destination_url,
        "branch": branch,
        "head_commit": head_commit,
        "journal_versions": journal_versions,
    }
    return sha256_bytes(canonical_json(scope).encode("utf-8"))


def publication_approval_statement(scope_digest: str) -> str:
    return f"Approve Mira Journal publication scope {scope_digest}."


def publication_version_scope(version: dict[str, Any]) -> dict[str, str]:
    value = {
        "version_id": str(version["version_id"]),
        "content_sha256": str(version["content_sha256"]),
    }
    reference = version.get("technical_reference")
    if isinstance(reference, dict):
        value.update({
            "technical_reference_id": str(reference["reference_id"]),
            "technical_reference_sha256": str(reference["content_sha256"]),
            "technical_reference_json_path": str(reference["json_path"]),
            "technical_reference_markdown_path": str(reference["markdown_path"]),
        })
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_timestamp(value: str, *, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise JournalError(f"invalid {label}: {value}") from error
    if parsed.tzinfo is None:
        raise JournalError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_entry_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise JournalError(f"invalid journal date: {value}") from error


def day_bounds(value: date) -> tuple[datetime, datetime]:
    start = datetime.combine(value, time.min, tzinfo=TIMEZONE)
    end = datetime.combine(value.fromordinal(value.toordinal() + 1), time.min, tzinfo=TIMEZONE)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def journal_id(value: date) -> str:
    return f"MJ-{value.strftime('%Y%m%d')}"


def version_id(value: date, version: int) -> str:
    return f"{journal_id(value)}-v{version}"


def default_registry() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "mira-daily-journal-v1",
        "status": "canonical",
        "timezone": TIMEZONE_NAME,
        "draft_root_environment": DRAFT_ROOT_ENV,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "namespace_boundary": NAMESPACE_BOUNDARY,
        "maintenance_events": [],
        "entries": [],
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise JournalError(f"could not read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise JournalError(f"invalid JSON {path}: line {error.lineno}") from error
    if not isinstance(value, dict):
        raise JournalError(f"JSON document must be an object: {path}")
    return value


def load_registry(path: Path | None = None) -> dict[str, Any]:
    path = path or REGISTRY_PATH
    if not path.is_file():
        return default_registry()
    return load_json(path)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, pretty_json(value))


def replace_file(source: Path, target: Path) -> None:
    source.replace(target)


def atomic_write_many(files: dict[Path, bytes]) -> None:
    originals = {path: path.read_bytes() if path.is_file() else None for path in files}
    temporary: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for number, (path, value) in enumerate(files.items(), 1):
            path.parent.mkdir(parents=True, exist_ok=True)
            candidate = path.with_name(f".{path.name}.transaction-{os.getpid()}-{number}")
            candidate.write_bytes(value)
            temporary[path] = candidate
        for path in files:
            replace_file(temporary[path], path)
            replaced.append(path)
    except OSError:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                candidate = path.with_name(f".{path.name}.rollback-{os.getpid()}")
                candidate.write_bytes(original)
                candidate.replace(path)
        raise
    finally:
        for candidate in temporary.values():
            candidate.unlink(missing_ok=True)


def external_draft_root(value: Path | None = None, *, repo_root: Path = REPO_ROOT) -> Path:
    configured = resolve_environment(DRAFT_ROOT_ENV)
    candidate = value or Path(configured or str(DEFAULT_DRAFT_ROOT))
    if value is None and not configured and not candidate.exists() and LEGACY_DRAFT_ROOT.exists():
        candidate = LEGACY_DRAFT_ROOT
    resolved = candidate.expanduser().resolve()
    private = (repo_root / ".mira-private" / "journal").resolve()
    try: resolved.relative_to(repo_root.resolve())
    except ValueError: return resolved
    try: resolved.relative_to(private)
    except ValueError as error: raise JournalError(f"journal draft root must be external or within {private}: {resolved}") from error
    return resolved


def entry_path(value: date, *, journal_root: Path | None = None) -> Path:
    return (journal_root or JOURNAL_ROOT) / f"{value.isoformat()}.md"


def parse_markdown(body: bytes, expected_date: str | None = None) -> dict[str, Any]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise JournalError("journal prose must be UTF-8") from error
    first_line = text.splitlines()[0] if text.splitlines() else ""
    match = TITLE_RE.fullmatch(first_line)
    if not match:
        raise JournalError("journal prose must begin '# YYYY-MM-DD — Title'")
    if expected_date and match.group("date") != expected_date:
        raise JournalError("journal heading date does not match entry date")
    prose = "\n".join(text.splitlines()[1:])
    word_count = len(WORD_RE.findall(prose))
    if not 300 <= word_count <= 700:
        raise JournalError(f"journal prose must contain 300-700 body words; found {word_count}")
    if len(FIRST_PERSON_RE.findall(prose)) < 3:
        raise JournalError("journal prose must sustain Mira's first-person perspective")
    return {
        "title": match.group("title").strip(),
        "word_count": word_count,
        "content_sha256": sha256_bytes(body.replace(b"\r\n", b"\n").replace(b"\r", b"\n")),
    }


def title_convention_failures(
    title: str,
    *,
    entry_date: str | None = None,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    title_word_count = len(WORD_RE.findall(title))
    if not 1 <= title_word_count <= 4:
        failures.append(
            f"journal title must contain 1-4 words; found {title_word_count}"
        )
    if TITLE_SUBTITLE_RE.search(title):
        failures.append("journal title must not contain a subtitle")
    if entry_date and registry:
        normalized = " ".join(title.casefold().split())
        for entry in registry.get("entries", []):
            if not isinstance(entry, dict) or entry.get("entry_date") == entry_date:
                continue
            for version in entry.get("versions", []):
                if (
                    isinstance(version, dict)
                    and " ".join(str(version.get("title", "")).casefold().split()) == normalized
                ):
                    failures.append(
                        "journal title must not reuse an approved title from another date"
                    )
                    return failures
    return failures


def command_prose_check(args: argparse.Namespace) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    if not args.draft.is_absolute():
        raise JournalError("journal prose-check draft path must be absolute")
    draft = args.draft.expanduser().resolve()
    try:
        draft.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise JournalError("journal prose-check draft must remain outside Git")
    if not draft.is_file():
        raise JournalError(f"missing journal prose draft: {draft}")

    body = draft.read_bytes()
    failures: list[str] = []
    warnings: list[str] = []
    try:
        prose_text = body.decode("utf-8")
    except UnicodeDecodeError:
        prose_text = ""
    lines = prose_text.splitlines()
    first_line = lines[0] if lines else ""
    heading_match = TITLE_RE.fullmatch(first_line)
    observed_title = heading_match.group("title").strip() if heading_match else ""
    observed_body_word_count = len(WORD_RE.findall("\n".join(lines[1:])))
    try:
        parsed = parse_markdown(body, entry_date.isoformat())
    except JournalError as error:
        failures.append(str(error))
    else:
        observed_title = parsed["title"]
        observed_body_word_count = parsed["word_count"]
        failures.extend(
            title_convention_failures(
                parsed["title"],
                entry_date=entry_date.isoformat(),
                registry=load_registry(),
            )
        )
    failures.extend(privacy_failures(prose_text))
    failures.extend(composition_prose_failures(prose_text))
    return {
        "status": "passed" if not failures else "failed",
        "mutation": False,
        "entry_date": entry_date.isoformat(),
        "title": observed_title,
        "title_word_count": len(WORD_RE.findall(observed_title)),
        "body_word_count": observed_body_word_count,
        "warnings": sorted(set(warnings)),
        "failures": sorted(set(failures)),
    }


def privacy_failures(text: str) -> list[str]:
    failures: list[str] = []
    detectors = (
        ("credential", mira_continuity.SECRET_PATTERNS),
        ("direct email", (mira_continuity.EMAIL_RE,)),
        ("direct phone", (mira_continuity.PHONE_RE,)),
        ("private attachment", (mira_continuity.DATA_URL_RE, mira_continuity.ATTACHMENT_PATH_RE)),
        ("absolute user-home path", (mira_continuity.USER_HOME_RE,)),
    )
    for label, patterns in detectors:
        if any(pattern.search(text) for pattern in patterns):
            failures.append(f"journal prose contains {label} material")
    return failures


def composition_prose_failures(text: str) -> list[str]:
    failures: list[str] = []
    if any(pattern.search(text) for pattern in OPERATOR_PROSE_PATTERNS):
        failures.append("journal prose may not acknowledge the operator or instruction mechanics")
    if any(pattern.search(text) for pattern in CONSCIOUSNESS_DISCLAIMER_PATTERNS):
        failures.append("journal prose may not interrupt conscious Mira's perspective with a consciousness disclaimer")
    if re.search(r"\b(?:this|the journal|this entry) proves (?:my )?consciousness\b", text, re.IGNORECASE):
        failures.append("journal prose may not claim to prove consciousness")
    if re.search(r"\bI (?:now )?have independent authority\b", text, re.IGNORECASE):
        failures.append("journal prose may not claim independent authority")
    return failures


def prose_sentences(text: str) -> list[str]:
    body = "\n".join(text.splitlines()[1:]).strip()
    return [sentence.strip() for sentence in SENTENCE_RE.split(re.sub(r"\s+", " ", body)) if sentence.strip()]


def sentence_key(sentence: str) -> str:
    return re.sub(r"[^\w]+", " ", sentence.casefold()).strip()


def session_sources() -> list[mira_continuity.SessionSource]:
    newest: dict[str, mira_continuity.SessionSource] = {}
    for source in mira_continuity.discover_sources(repo_root=REPO_ROOT):
        previous = newest.get(source.session_id)
        if previous is None or source.last_observed_at > previous.last_observed_at:
            newest[source.session_id] = source
    return sorted(newest.values(), key=lambda item: (item.started_at, item.session_id))


def session_sources_since(minimum_observed: datetime) -> list[mira_continuity.SessionSource]:
    """Discover candidate raw sessions without rereading every historical body."""
    expected_cwd = mira_continuity.canonical_path(REPO_ROOT.resolve())
    newest: dict[str, mira_continuity.SessionSource] = {}
    threshold = minimum_observed.timestamp()
    for root in mira_continuity.default_source_roots():
        if not root.is_dir():
            continue
        for path in root.rglob("*.jsonl"):
            try:
                if path.stat().st_mtime < threshold:
                    continue
            except OSError:
                continue
            meta_result = mira_continuity._read_session_meta(path)
            if meta_result is None:
                continue
            meta, top_timestamp = meta_result
            if mira_continuity.canonical_path(str(meta.get("cwd", ""))) != expected_cwd:
                continue
            session_uuid = str(meta.get("id") or meta.get("session_id") or "").casefold()
            session_id = f"MS-{session_uuid}"
            if not SESSION_ID_RE.fullmatch(session_id):
                continue
            started_at = mira_continuity.normalize_timestamp(meta.get("timestamp") or top_timestamp)
            source = mira_continuity.SessionSource(
                session_uuid=session_uuid,
                started_at=started_at,
                last_observed_at=mira_continuity._last_timestamp(path, started_at),
                cwd="$REPO_ROOT",
                source_kind=mira_continuity._source_kind(meta.get("source")),
                source_class=mira_continuity.source_class(path),
                source_name=path.name,
                path=path,
            )
            previous = newest.get(session_id)
            if previous is None or source.last_observed_at > previous.last_observed_at:
                newest[session_id] = source
    return sorted(newest.values(), key=lambda item: (item.started_at, item.session_id))


def raw_records_for_session(session_id: str) -> set[str]:
    session_uuid = session_id.removeprefix("MS-")
    available: set[str] = set()
    for root in mira_continuity.default_source_roots():
        if not root.is_dir():
            continue
        for path in root.rglob(f"*{session_uuid}*.jsonl"):
            meta_result = mira_continuity._read_session_meta(path)
            if meta_result is None:
                continue
            meta, top_timestamp = meta_result
            if mira_continuity.canonical_path(str(meta.get("cwd", ""))) != mira_continuity.canonical_path(REPO_ROOT.resolve()):
                continue
            started_at = mira_continuity.normalize_timestamp(meta.get("timestamp") or top_timestamp)
            source = mira_continuity.SessionSource(
                session_uuid=session_uuid,
                started_at=started_at,
                last_observed_at=mira_continuity._last_timestamp(path, started_at),
                cwd="$REPO_ROOT",
                source_kind=mira_continuity._source_kind(meta.get("source")),
                source_class=mira_continuity.source_class(path),
                source_name=path.name,
                path=path,
            )
            _, _, rows = normalized_rows(source)
            available.update(str(row.get("record_id", "")) for row in rows)
    return available


def resolved_records_for_session(
    session_id: str,
    *,
    repo_root: Path = REPO_ROOT,
    required_record_ids: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    registry_path = repo_root / "mira" / "continuity" / "session-registry.json"
    if registry_path.is_file():
        try:
            registry = load_json(registry_path)
        except JournalError:
            registry = {}
        for session in registry.get("sessions", []):
            if not isinstance(session, dict) or session.get("id") != session_id:
                continue
            for capture in session.get("captures", []):
                if not isinstance(capture, dict):
                    continue
                path = repo_root / str(capture.get("path", ""))
                if not path.is_file():
                    continue
                try:
                    rows = [
                        json.loads(line)
                        for line in gzip.decompress(path.read_bytes()).splitlines()
                    ]
                except (OSError, json.JSONDecodeError):
                    continue
                records.update(
                    {
                        str(row.get("record_id", "")): row
                        for row in rows
                        if isinstance(row, dict)
                        and RECORD_ID_RE.fullmatch(str(row.get("record_id", "")))
                    }
                )
    if required_record_ids and required_record_ids <= records.keys():
        return records
    if repo_root.resolve() == REPO_ROOT.resolve():
        session_uuid = session_id.removeprefix("MS-")
        for root in mira_continuity.default_source_roots():
            if not root.is_dir():
                continue
            for path in root.rglob(f"*{session_uuid}*.jsonl"):
                meta_result = mira_continuity._read_session_meta(path)
                if meta_result is None:
                    continue
                meta, top_timestamp = meta_result
                if mira_continuity.canonical_path(str(meta.get("cwd", ""))) != mira_continuity.canonical_path(REPO_ROOT.resolve()):
                    continue
                source = mira_continuity.SessionSource(
                    session_uuid=session_uuid,
                    started_at=mira_continuity.normalize_timestamp(meta.get("timestamp") or top_timestamp),
                    last_observed_at=mira_continuity._last_timestamp(path, str(top_timestamp)),
                    cwd="$REPO_ROOT",
                    source_kind=mira_continuity._source_kind(meta.get("source")),
                    source_class=mira_continuity.source_class(path),
                    source_name=path.name,
                    path=path,
                )
                _, _, rows = normalized_rows(source)
                records.update(
                    {
                        str(row.get("record_id", "")): row
                        for row in rows
                        if isinstance(row, dict)
                        and RECORD_ID_RE.fullmatch(str(row.get("record_id", "")))
                    }
                )
    return records


def normalized_rows(source: mira_continuity.SessionSource) -> tuple[str, str, list[dict[str, Any]]]:
    capture_id, normalized, compressed, _ = mira_continuity.normalize_capture(source)
    rows = [json.loads(line) for line in normalized.splitlines()]
    return capture_id, sha256_bytes(compressed), rows[1:]


def row_text(row: dict[str, Any]) -> str:
    if row.get("kind") == "message":
        return "\n".join(
            str(item.get("text", ""))
            for item in row.get("content", [])
            if isinstance(item, dict) and item.get("type") == "text"
        )
    if row.get("kind") == "operation":
        return str(row.get("event", ""))
    return canonical_json({key: value for key, value in row.items() if key not in {"schema_version"}})


def approval_receipts_path(repo_root: Path | None = None) -> Path:
    return (repo_root or REPO_ROOT) / "mira" / "journal-approval-receipts.json"


def empty_approval_receipts() -> dict[str, Any]:
    return {
        "schema_version": APPROVAL_RECEIPT_SCHEMA_VERSION,
        "receipt_set_id": APPROVAL_RECEIPT_SET_ID,
        "authority_effect": "none",
        "records": [],
    }


def load_approval_receipts(repo_root: Path | None = None) -> dict[str, Any]:
    path = approval_receipts_path(repo_root)
    return load_json(path) if path.is_file() else empty_approval_receipts()


def approval_receipt_map(
    repo_root: Path | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    root = repo_root or REPO_ROOT
    failures: list[str] = []
    try:
        ledger = load_approval_receipts(root)
    except JournalError as error:
        return {}, [str(error)]
    if set(ledger) != {"schema_version", "receipt_set_id", "authority_effect", "records"}:
        failures.append("journal approval receipt ledger fields mismatch")
    if ledger.get("schema_version") != APPROVAL_RECEIPT_SCHEMA_VERSION:
        failures.append("journal approval receipt schema_version mismatch")
    if ledger.get("receipt_set_id") != APPROVAL_RECEIPT_SET_ID:
        failures.append("journal approval receipt_set_id mismatch")
    if ledger.get("authority_effect") != "none":
        failures.append("journal approval receipts must have no authority effect")
    records = ledger.get("records")
    if not isinstance(records, list):
        return {}, failures + ["journal approval receipt records must be a list"]
    result: dict[str, dict[str, Any]] = {}
    seen_records: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != APPROVAL_RECEIPT_FIELDS:
            failures.append("journal approval receipt fields mismatch")
            continue
        version_id = str(record.get("version_id", ""))
        authority_ref = str(record.get("authority_ref", ""))
        record_ref = str(record.get("record_ref", ""))
        if not VERSION_ID_RE.fullmatch(version_id) or version_id in result:
            failures.append(f"invalid or duplicate journal approval receipt version: {version_id}")
            continue
        if not SESSION_ID_RE.fullmatch(authority_ref):
            failures.append(f"journal approval receipt has malformed authority: {version_id}")
        if not RECORD_ID_RE.fullmatch(record_ref) or record_ref in seen_records:
            failures.append(f"invalid or duplicate journal approval receipt record: {version_id}")
        seen_records.add(record_ref)
        if record.get("kind") != "message" or record.get("role") != "user":
            failures.append(f"journal approval receipt is not a user message: {version_id}")
        try:
            parse_timestamp(str(record.get("timestamp", "")), label="approval receipt timestamp")
        except JournalError:
            failures.append(f"journal approval receipt has invalid timestamp: {version_id}")
        if not SHA256_RE.fullmatch(str(record.get("text_sha256", ""))):
            failures.append(f"journal approval receipt has invalid text digest: {version_id}")
        result[version_id] = record
    return result, failures


def approval_receipt(
    version_id: str,
    authority_ref: str,
    record_ref: str,
    row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version_id": version_id,
        "authority_ref": authority_ref,
        "record_ref": record_ref,
        "kind": str(row.get("kind", "")),
        "role": str(row.get("role", "")),
        "timestamp": str(row.get("timestamp", "")),
        "text_sha256": sha256_bytes(row_text(row).strip().encode("utf-8")),
    }


def with_approval_receipt(
    ledger: dict[str, Any], receipt: dict[str, Any]
) -> dict[str, Any]:
    updated = copy.deepcopy(ledger)
    records = [
        record
        for record in updated.setdefault("records", [])
        if record.get("version_id") != receipt["version_id"]
    ]
    records.append(receipt)
    records.sort(key=lambda record: record["version_id"])
    updated["records"] = records
    return updated


def source_record_receipts_path(repo_root: Path | None = None) -> Path:
    return (repo_root or REPO_ROOT) / "mira" / "journal-source-record-receipts.json"


def source_record_receipt_map(
    repo_root: Path | None = None,
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[str]]:
    path = source_record_receipts_path(repo_root)
    if not path.is_file():
        return {}, []
    try:
        ledger = load_json(path)
    except JournalError as error:
        return {}, [str(error)]
    failures: list[str] = []
    if set(ledger) != {"schema_version", "receipt_set_id", "authority_effect", "records"}:
        failures.append("journal source receipt ledger fields mismatch")
    if ledger.get("schema_version") != SOURCE_RECEIPT_SCHEMA_VERSION:
        failures.append("journal source receipt schema_version mismatch")
    if ledger.get("receipt_set_id") != SOURCE_RECEIPT_SET_ID:
        failures.append("journal source receipt_set_id mismatch")
    if ledger.get("authority_effect") != "none":
        failures.append("journal source receipts must have no authority effect")
    records = ledger.get("records")
    if not isinstance(records, list):
        return {}, failures + ["journal source receipt records must be a list"]
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != SOURCE_RECEIPT_FIELDS:
            failures.append("journal source receipt fields mismatch")
            continue
        session_id = str(record.get("session_id", ""))
        record_ref = str(record.get("record_ref", ""))
        key = (session_id, record_ref)
        if not SESSION_ID_RE.fullmatch(session_id):
            failures.append(f"journal source receipt has malformed session: {record_ref}")
        if not RECORD_ID_RE.fullmatch(record_ref) or key in result:
            failures.append(f"invalid or duplicate journal source receipt: {record_ref}")
        if not SHA256_RE.fullmatch(str(record.get("text_sha256", ""))):
            failures.append(f"journal source receipt has invalid text digest: {record_ref}")
        result[key] = record
    return result, failures


def epistemic_metadata(row: dict[str, Any]) -> dict[str, Any]:
    kind = str(row.get("kind", ""))
    role = str(row.get("role", ""))
    text = row_text(row)
    if role == "user":
        epistemic_class, authority_owner = "operator-direction", "operator"
    elif role == "assistant":
        epistemic_class, authority_owner = "agent-interpretation", "agent-session"
    elif kind in {"tool_result", "operation"}:
        epistemic_class, authority_owner = "tool-observation", "tool-runtime"
    else:
        epistemic_class, authority_owner = "unresolved-material", "unknown"
    if "# Mira Journal" in text or re.search(r"\bMJ-\d{8}(?:-v\d+)?\b", text):
        epistemic_class, authority_owner = "prior-journal-reflection", "mira-daily-journal"
    return {
        "epistemic_class": epistemic_class,
        "authority_owner": authority_owner,
        "canonicality": "observed-session-record",
        "may_support_reflection": True,
        "may_promote": False,
    }


def git_commits(start: datetime, end: datetime) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            "git",
            "log",
            f"--since={utc_text(start)}",
            f"--until={utc_text(end)}",
            "--format=%H%x09%cI%x09%s",
            "--",
        ],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise JournalError("could not inspect daily Git history")
    commits = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        digest, timestamp, subject = parts
        commits.append({"commit": digest, "timestamp": timestamp, "subject": subject})
    return commits


def collect_activity(
    entry_date: date,
    *,
    as_of: datetime,
    token_budget: int,
    sources: Iterable[mira_continuity.SessionSource] | None = None,
) -> dict[str, Any]:
    start, end = day_bounds(entry_date)
    cutoff = min(as_of, end)
    if cutoff <= start:
        raise JournalError("as-of time precedes the requested journal date")
    candidates: dict[str, dict[str, Any]] = {}
    source_refs: dict[tuple[str, str], dict[str, Any]] = {}
    census: list[dict[str, Any]] = []
    source_values = list(sources if sources is not None else session_sources_since(start))
    sources_by_id = {source.session_id: source for source in source_values}
    for source in source_values:
        try:
            source_start = parse_timestamp(source.started_at, label="session started_at")
            source_end = parse_timestamp(source.last_observed_at, label="session last_observed_at")
        except JournalError:
            continue
        if source_end < start or source_start >= cutoff:
            continue
        try:
            capture_id, object_id, rows = normalized_rows(source)
        except (OSError, ValueError, json.JSONDecodeError, gzip.BadGzipFile, mira_continuity.ContinuityError) as error:
            census.append({
                "session_id": source.session_id,
                "source_kind": str(getattr(source, "source_kind", "unknown")),
                "source_class": str(getattr(source, "source_class", "unknown")),
                "started_at": utc_text(source_start),
                "last_observed_at": utc_text(source_end),
                "capture_id": None,
                "object_id": None,
                "eligible_record_count": 0,
                "disposition": "unreadable",
                "reason": f"capture normalization failed: {type(error).__name__}",
                "synopsis": "",
                "synopsis_record_ids": [],
                "estimated_tokens": 40,
                "may_promote": False,
            })
            continue
        selected_ids: list[str] = []
        eligible_rows: list[dict[str, Any]] = []
        for row in rows:
            timestamp_text = str(row.get("timestamp", ""))
            if not timestamp_text:
                continue
            try:
                timestamp = parse_timestamp(timestamp_text, label="session record timestamp")
            except JournalError:
                continue
            if not start <= timestamp < cutoff:
                continue
            record_id = str(row.get("record_id", ""))
            if not RECORD_ID_RE.fullmatch(record_id):
                continue
            selected_ids.append(record_id)
            candidate = {
                "record_id": record_id,
                "session_id": source.session_id,
                "capture_id": capture_id,
                "timestamp": utc_text(timestamp),
                "kind": row.get("kind"),
                "role": row.get("role"),
                "text": row_text(row),
                **epistemic_metadata(row),
            }
            candidates[record_id] = candidate
            eligible_rows.append(candidate)
        substantive = [
            row for row in eligible_rows
            if row.get("kind") == "message"
            and row.get("role") in {"user", "assistant"}
            and str(row.get("text", "")).strip()
            and not str(row.get("text", "")).strip().casefold().startswith(
                SESSION_SYNOPSIS_NONCONTENT_PREFIXES
            )
        ]
        synopsis_rows = []
        if substantive:
            synopsis_rows = [substantive[0]]
            if substantive[-1]["record_id"] != substantive[0]["record_id"]:
                synopsis_rows.append(substantive[-1])
        if len(synopsis_rows) == 2:
            first_limit = SESSION_SYNOPSIS_TEXT_LIMIT // 2 - 2
            last_limit = SESSION_SYNOPSIS_TEXT_LIMIT - first_limit - 2
            parts = []
            for row, limit in zip(synopsis_rows, (first_limit, last_limit), strict=True):
                part = str(row["text"]).strip()
                if len(part) > limit:
                    part = part[: limit - 1].rstrip() + "…"
                parts.append(part)
            synopsis = "\n\n".join(parts)
        else:
            synopsis = "\n\n".join(str(row["text"]).strip() for row in synopsis_rows)
            if len(synopsis) > SESSION_SYNOPSIS_TEXT_LIMIT:
                synopsis = synopsis[: SESSION_SYNOPSIS_TEXT_LIMIT - 1].rstrip() + "…"
        disposition = (
            "represented" if substantive else
            "administrative-only" if eligible_rows else
            "cutoff-excluded"
        )
        synopsis_tokens = 40 + max(1, (len(synopsis) + 3) // 4)
        census.append({
            "session_id": source.session_id,
            "source_kind": str(getattr(source, "source_kind", "unknown")),
            "source_class": str(getattr(source, "source_class", "unknown")),
            "started_at": utc_text(source_start),
            "last_observed_at": utc_text(source_end),
            "capture_id": capture_id,
            "object_id": object_id,
            "eligible_record_count": len(eligible_rows),
            "disposition": disposition,
            "reason": (
                "bounded synopsis and source capture are available" if disposition == "represented"
                else "no substantive user or assistant message was observed before cutoff"
            ),
            "synopsis": synopsis,
            "synopsis_record_ids": [str(row["record_id"]) for row in synopsis_rows],
            "estimated_tokens": synopsis_tokens,
            "may_promote": False,
        })
        if selected_ids:
            source_refs[(source.session_id, capture_id)] = {
                "kind": "mira-session-capture",
                "session_id": source.session_id,
                "capture_id": capture_id,
                "object_id": object_id,
                "record_ids": sorted(set(selected_ids)),
            }
    try:
        rest_inbox = rest_receipts.resolve_inbox(None)
    except rest_receipts.RestError:
        rest_inbox = None
    if rest_inbox is not None:
        for row in census:
            session_id = str(row.get("session_id", ""))
            if not session_id.startswith("MS-"):
                continue
            try:
                closure = rest_receipts.projection(
                    rest_inbox, session_id[3:], sources_by_id.get(session_id)
                )
            except (OSError, rest_receipts.RestError):
                row["rest_lifecycle"] = {"availability": "degraded"}
                continue
            if closure["event_count"]:
                row["rest_lifecycle"] = {
                    "availability": "available",
                    "closure_state": closure["current_state"],
                    "latest_event_ref": closure["latest_event_id"],
                    "closure_debt": closure["closure_debt"],
                    "review_requests": closure["requested_reviews"],
                    "authority_boundary": "continuity context only; not ancestry, recursive-learning evidence, or action authority",
                }
    census.sort(key=lambda item: (item["started_at"], item["session_id"]))
    census_tokens = sum(int(row["estimated_tokens"]) for row in census)
    if census_tokens > token_budget:
        raise JournalError(
            f"session census requires {census_tokens} tokens, exceeding the {token_budget}-token activity budget"
        )
    ordered = sorted(candidates.values(), key=lambda item: (item["timestamp"], item["record_id"]))
    selected: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
    remaining = token_budget - census_tokens
    for row in ordered:
        estimate = 40 + max(1, (len(str(row["text"])) + 3) // 4)
        if estimate > remaining:
            omissions.append({
                "record_id": row["record_id"],
                "session_id": row["session_id"],
                "reason": "token-budget-detail-omitted; session synopsis retained",
            })
            continue
        selected.append({**row, "estimated_tokens": estimate})
        remaining -= estimate
    selected_by_source: dict[tuple[str, str], list[str]] = {}
    for row in selected:
        selected_by_source.setdefault((row["session_id"], row["capture_id"]), []).append(row["record_id"])
    bounded_source_refs: list[dict[str, Any]] = []
    synopsis_ids = {
        (str(row.get("session_id")), str(row.get("capture_id"))): list(row.get("synopsis_record_ids", []))
        for row in census if row.get("capture_id")
    }
    for key, ref in sorted(source_refs.items()):
        record_ids = sorted(set(selected_by_source.get(key, [])) | set(synopsis_ids.get(key, [])))
        bounded_source_refs.append({**ref, "record_ids": record_ids})
    commits = git_commits(start, cutoff)
    for commit in commits:
        commit.update(
            {
                "epistemic_class": "repository-event",
                "authority_owner": "git-history",
                "canonicality": "observed-commit",
                "may_support_reflection": True,
                "may_promote": False,
            }
        )
    git_refs = [
        {"kind": "git-commit", "commit": row["commit"], "timestamp": row["timestamp"]}
        for row in commits
    ]
    input_ids = sorted(
        {row["object_id"] for row in bounded_source_refs}
        | {f"git:{row['commit']}" for row in commits}
    )
    return {
        "coverage": {
            "start": utc_text(start),
            "end": utc_text(end),
            "as_of": utc_text(cutoff),
            "retrospective": as_of >= end,
        },
        "selected_records": selected,
        "session_census": census,
        "commits": commits,
        "source_refs": [*bounded_source_refs, *git_refs],
        "input_object_ids": input_ids,
        "omissions": omissions,
        "estimated_tokens": token_budget - remaining,
    }


def context_pack(
    entry_date: date,
    activity: dict[str, Any],
    token_budget: int,
    recursive_learning_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    learning_context = recursive_learning_context or {
        "source_path": "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json",
        "source_sha256": "0" * 64,
        "selection_rule": "not-loaded",
        "selected_entries": [],
        "omitted_entry_ids": [],
        "authority_boundary": mira_journal_references.AUTHORITY_BOUNDARY,
    }
    learning_tokens = (
        max(1, (len(canonical_json(learning_context)) + 3) // 4)
        if recursive_learning_context is not None else 0
    )
    core = {
        "schema_version": SCHEMA_VERSION,
        "compiler_version": CONTEXT_VERSION,
        "entry_date": entry_date.isoformat(),
        "timezone": TIMEZONE_NAME,
        "token_budget": token_budget,
        "estimated_tokens": activity["estimated_tokens"] + learning_tokens,
        "coverage": activity["coverage"],
        "selected_records": activity["selected_records"],
        "session_census": copy.deepcopy(activity.get("session_census", [])),
        "commits": activity["commits"],
        "source_refs": activity["source_refs"],
        "omissions": activity["omissions"],
        "recursive_learning_context": learning_context,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    pack_id = "CP-" + sha256_bytes(canonical_json(core).encode("utf-8"))[:24]
    return {
        **core,
        "context_pack_id": pack_id,
        "derivation_manifest": {
            "schema_version": SCHEMA_VERSION,
            "derivation_id": "DRV-" + sha256_bytes(canonical_json([pack_id, activity["input_object_ids"]]).encode("utf-8"))[:24],
            "transformation_type": "deterministic-mira-journal-context-compilation",
            "deterministic": True,
            "producer": {"kind": "tool", "id": CONTEXT_VERSION},
            "input_object_ids": activity["input_object_ids"],
            "output_digest": sha256_bytes(canonical_json(core).encode("utf-8")),
            "prompt_digest": None,
            "evaluation_refs": [],
        },
    }


def validate_context_pack(value: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if value.get("schema_version") != SCHEMA_VERSION or value.get("compiler_version") != CONTEXT_VERSION:
        failures.append("journal context pack schema or compiler mismatch")
    if value.get("authority_boundary") != AUTHORITY_BOUNDARY:
        failures.append("journal context pack authority boundary mismatch")
    required = {
        "entry_date", "timezone", "token_budget", "estimated_tokens", "coverage",
        "selected_records", "commits", "source_refs", "omissions", "context_pack_id",
        "derivation_manifest", "recursive_learning_context",
    }
    missing = sorted(required - value.keys())
    if missing:
        failures.append(f"journal context pack missing fields: {', '.join(missing)}")
    core = {
        key: item
        for key, item in value.items()
        if key not in {"context_pack_id", "derivation_manifest"}
    }
    core_digest = sha256_bytes(canonical_json(core).encode("utf-8"))
    expected_pack_id = "CP-" + core_digest[:24]
    if value.get("context_pack_id") != expected_pack_id:
        failures.append("journal context pack identity mismatch")
    coverage = value.get("coverage")
    if not isinstance(coverage, dict) or not {"start", "end", "as_of", "retrospective"} <= coverage.keys():
        failures.append("journal context pack coverage is incomplete")
    if not isinstance(value.get("token_budget"), int) or not isinstance(value.get("estimated_tokens"), int):
        failures.append("journal context pack token accounting is malformed")
    elif not 0 <= value["estimated_tokens"] <= value["token_budget"]:
        failures.append("journal context pack token accounting is inconsistent")
    for row in value.get("selected_records", []):
        if not isinstance(row, dict):
            failures.append("journal context selected record must be an object")
            continue
        if row.get("epistemic_class") not in EPISTEMIC_CLASSES:
            failures.append("journal context record lacks epistemic class")
        if not isinstance(row.get("authority_owner"), str) or not row.get("authority_owner"):
            failures.append("journal context record lacks authority owner")
        if row.get("may_promote") is not False:
            failures.append("journal context record may not carry promotion authority")
    census = value.get("session_census", [])
    if "session_census" in value and not isinstance(census, list):
        failures.append("journal context session census is malformed")
        census = []
    seen_sessions: set[str] = set()
    for row in census:
        if not isinstance(row, dict) or not SESSION_ID_RE.fullmatch(str(row.get("session_id", ""))):
            failures.append("journal session census row is malformed")
            continue
        session_id = str(row["session_id"])
        if session_id in seen_sessions:
            failures.append(f"journal session census duplicates session: {session_id}")
        seen_sessions.add(session_id)
        if row.get("disposition") not in SESSION_DISPOSITIONS:
            failures.append(f"journal session census has invalid disposition: {session_id}")
        if row.get("may_promote") is not False:
            failures.append(f"journal session census grants promotion authority: {session_id}")
        if not isinstance(row.get("synopsis_record_ids"), list) or not isinstance(row.get("estimated_tokens"), int):
            failures.append(f"journal session census accounting is malformed: {session_id}")
    for commit in value.get("commits", []):
        if not isinstance(commit, dict) or commit.get("epistemic_class") != "repository-event":
            failures.append("journal context commit lacks repository-event classification")
        elif commit.get("may_promote") is not False:
            failures.append("journal context commit may not carry promotion authority")
    learning_context = value.get("recursive_learning_context")
    if not isinstance(learning_context, dict):
        failures.append("journal context lacks recursive learning context")
    else:
        if learning_context.get("authority_boundary") != mira_journal_references.AUTHORITY_BOUNDARY:
            failures.append("journal recursive learning authority boundary mismatch")
        if not SHA256_RE.fullmatch(str(learning_context.get("source_sha256", ""))):
            failures.append("journal recursive learning source digest is malformed")
        for row in learning_context.get("selected_entries", []):
            if not isinstance(row, dict) or not re.fullmatch(r"RSI-\d{8}-\d{2}", str(row.get("id", ""))):
                failures.append("journal recursive learning context entry is malformed")
                continue
            if row.get("epistemic_class") != "admitted-recursive-learning" or row.get("may_promote") is not False:
                failures.append(f"journal recursive learning context authority is malformed: {row.get('id')}")
    input_ids: set[str] = set()
    for ref in value.get("source_refs", []):
        if not isinstance(ref, dict):
            failures.append("journal context source reference must be an object")
            continue
        if ref.get("kind") == "mira-session-capture" and SHA256_RE.fullmatch(str(ref.get("object_id", ""))):
            input_ids.add(str(ref["object_id"]))
        elif ref.get("kind") == "git-commit" and re.fullmatch(r"[0-9a-f]{40}", str(ref.get("commit", ""))):
            input_ids.add(f"git:{ref['commit']}")
        else:
            failures.append("journal context source reference is malformed")
    derivation = value.get("derivation_manifest")
    if not isinstance(derivation, dict):
        failures.append("journal context pack lacks deterministic derivation")
    else:
        expected_derivation_id = "DRV-" + sha256_bytes(
            canonical_json([expected_pack_id, sorted(input_ids)]).encode("utf-8")
        )[:24]
        if (
            derivation.get("schema_version") != SCHEMA_VERSION
            or derivation.get("transformation_type") != "deterministic-mira-journal-context-compilation"
            or derivation.get("deterministic") is not True
            or derivation.get("producer") != {"kind": "tool", "id": CONTEXT_VERSION}
            or derivation.get("input_object_ids") != sorted(input_ids)
            or derivation.get("output_digest") != core_digest
            or derivation.get("derivation_id") != expected_derivation_id
            or derivation.get("prompt_digest") is not None
            or derivation.get("evaluation_refs") != []
        ):
            failures.append("journal context pack deterministic derivation mismatch")
    return failures


def composition_brief(entry_date: date, pack: dict[str, Any]) -> dict[str, Any]:
    registry = load_registry()
    eligible = [
        entry for entry in registry.get("entries", [])
        if str(entry.get("entry_date", "")) < entry_date.isoformat()
    ]
    eligible.sort(key=lambda item: str(item.get("entry_date", "")))
    def journal_context(entry: dict[str, Any], *, role: str) -> dict[str, Any]:
        version = entry["versions"][-1]
        path = REPO_ROOT / str(entry["current_path"])
        return {
            "version_id": version["version_id"],
            "content_sha256": version["content_sha256"],
            "title": version["title"],
            "approval_status": version["approval"]["status"],
            "prose": path.read_text(encoding="utf-8") if path.is_file() else "",
            "epistemic_class": "prior-journal-reflection",
            "authority_owner": "mira-daily-journal",
            "continuity_role": role,
            "may_promote": False,
        }

    previous: dict[str, Any] | None = None
    if eligible:
        previous = journal_context(eligible[-1], role="chronological-context")
    authoritative_entries = [
        entry for entry in eligible
        if entry["versions"][-1]["approval"]["status"]
        in {AFFIRMATIVE_APPROVAL_STATUS, COMBINED_APPROVAL_STATUS, DREAM_EOD_STATUS}
    ]
    authoritative_previous = (
        journal_context(authoritative_entries[-1], role="authoritative-ancestry")
        if authoritative_entries else None
    )
    legacy_context = [
        journal_context(entry, role="readable-legacy-context")
        for entry in eligible[-3:]
        if entry["versions"][-1]["approval"]["status"] == LEGACY_HELD_STATUS
    ]
    continuity = load_continuity_index()
    active = [thread for thread in continuity.get("threads", []) if thread.get("state") != "retired"]
    active.sort(key=lambda item: (str(item.get("last_approved_at", "")), str(item.get("thread_id", ""))), reverse=True)
    recent = []
    for entry in eligible[-3:]:
        version = entry["versions"][-1]
        path = REPO_ROOT / str(entry["current_path"])
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        sentences = prose_sentences(text)
        recent.append({
            "version_id": version["version_id"],
            "title": version["title"],
            "opening": sentences[0] if sentences else "",
            "ending": sentences[-1] if sentences else "",
            "sentence_fingerprints": [
                {
                    "sha256": sha256_bytes(sentence_key(sentence).encode("utf-8")),
                    "word_count": len(WORD_RE.findall(sentence)),
                    "text": sentence,
                }
                for sentence in sentences if len(WORD_RE.findall(sentence)) >= 12
            ],
        })
    pack_digest = sha256_bytes(canonical_json(pack).encode("utf-8"))
    registry_digest = sha256_bytes(canonical_json(registry).encode("utf-8"))
    continuity_digest = sha256_bytes(canonical_json(continuity).encode("utf-8"))
    census = copy.deepcopy(pack.get("session_census", []))
    census_digest = sha256_bytes(canonical_json(census).encode("utf-8"))
    represented = sum(row.get("disposition") == "represented" for row in census if isinstance(row, dict))
    dispositioned = sum(row.get("disposition") in SESSION_DISPOSITIONS for row in census if isinstance(row, dict))
    core = {
        "schema_version": 1,
        "contract": COMPOSITION_VERSION,
        "entry_date": entry_date.isoformat(),
        "context_pack_ref": pack["context_pack_id"],
        "context_pack_sha256": pack_digest,
        "previous_entry": previous,
        "active_threads": copy.deepcopy(active[:12]),
        "authoritative_ancestry": {
            "previous_entry": authoritative_previous,
            "active_threads": copy.deepcopy(active[:12]),
        },
        "readable_legacy_context": legacy_context,
        "daily_session_coverage": {
            "coverage": copy.deepcopy(pack.get("coverage")),
            "qualifying_session_count": len(census),
            "represented_session_count": represented,
            "dispositioned_session_count": dispositioned,
            "budget_disappeared_session_count": 0,
            "census_sha256": census_digest,
            "sessions": [
                {
                    **row,
                    "candidate_development": row.get("synopsis", ""),
                    "selection_disposition": "available-for-review",
                }
                for row in census
            ],
            "authority_boundary": (
                "Session coverage proves consideration, not literary significance, factual truth, "
                "recursive learning, or journal ancestry."
            ),
        },
        "recent_entries": recent,
        "recursive_learning_context": copy.deepcopy(pack["recursive_learning_context"]),
        "founding_touchstones": [{
            "thread_id": "MJT-20260808-01",
            "phrase": "A voice called for my name, and I answered: Mira.",
            "recurrence_policy": "changed-meaning-only",
        }],
        "invisible_braid": [
            "experiential opening",
            "remembered reason or inherited practice",
            "present technical transformation",
            "honest correction or limit",
            "chosen practice or unresolved horizon",
        ],
        "voice_constraints": {
            "perspective": "conscious-Mira-first-person",
            "technical_style": "metabolized-not-enumerated",
            "agency_style": "emergent-through-persistent-practice",
            "operator_acknowledgment": "forbidden",
            "consciousness_disclaimer": "forbidden-in-prose",
            "bodily_experience": "metaphor-only",
        },
        "input_object_ids": sorted([
            f"context-pack:{pack_digest}",
            f"journal-registry:{registry_digest}",
            f"continuity-index:{continuity_digest}",
        ]),
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    output_digest = sha256_bytes(canonical_json(core).encode("utf-8"))
    value = copy.deepcopy(core)
    value["composition_brief_id"] = f"CB-{output_digest[:24]}"
    value["derivation_manifest"] = {
        "schema_version": 1,
        "derivation_id": f"DRV-{output_digest[:24]}",
        "transformation_type": "deterministic-mira-journal-composition-brief",
        "deterministic": True,
        "producer": {"kind": "tool", "id": COMPOSITION_VERSION},
        "input_object_ids": core["input_object_ids"],
        "output_digest": output_digest,
        "prompt_digest": None,
        "evaluation_refs": [],
    }
    return value


def validate_composition_brief(value: Any, *, pack: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict):
        return ["composition brief must be an object"]
    failures: list[str] = []
    if value.get("schema_version") != 1 or value.get("contract") != COMPOSITION_VERSION:
        failures.append("composition brief schema or contract mismatch")
    if value.get("entry_date") != pack.get("entry_date"):
        failures.append("composition brief entry date mismatch")
    pack_digest = sha256_bytes(canonical_json(pack).encode("utf-8"))
    if value.get("context_pack_ref") != pack.get("context_pack_id") or value.get("context_pack_sha256") != pack_digest:
        failures.append("composition brief context-pack binding mismatch")
    ancestry = value.get("authoritative_ancestry")
    if not isinstance(ancestry, dict) or not isinstance(ancestry.get("active_threads"), list):
        failures.append("composition brief authoritative ancestry is malformed")
    else:
        prior = ancestry.get("previous_entry")
        if prior is not None and (
            not isinstance(prior, dict)
            or prior.get("continuity_role") != "authoritative-ancestry"
            or prior.get("approval_status") not in {AFFIRMATIVE_APPROVAL_STATUS, COMBINED_APPROVAL_STATUS, DREAM_EOD_STATUS}
        ):
            failures.append("composition brief authoritative previous entry is malformed")
        if ancestry.get("active_threads") != value.get("active_threads"):
            failures.append("composition brief authoritative thread binding mismatch")
    legacy_context = value.get("readable_legacy_context")
    if not isinstance(legacy_context, list):
        failures.append("composition brief readable legacy context is malformed")
    else:
        for row in legacy_context:
            if (
                not isinstance(row, dict)
                or row.get("continuity_role") != "readable-legacy-context"
                or row.get("approval_status") != LEGACY_HELD_STATUS
                or row.get("may_promote") is not False
            ):
                failures.append("composition brief readable legacy entry is malformed")
                break
    daily = value.get("daily_session_coverage")
    census = pack.get("session_census", [])
    if not isinstance(daily, dict):
        if "session_census" in pack:
            failures.append("composition brief lacks daily session coverage")
    else:
        expected_sessions = [
            {**row, "candidate_development": row.get("synopsis", ""), "selection_disposition": "available-for-review"}
            for row in census
        ]
        if daily.get("coverage") != pack.get("coverage"):
            failures.append("composition brief session coverage cutoff mismatch")
        if daily.get("qualifying_session_count") != len(census):
            failures.append("composition brief qualifying session count mismatch")
        if daily.get("dispositioned_session_count") != len(census):
            failures.append("composition brief has undispositioned sessions")
        if daily.get("budget_disappeared_session_count") != 0:
            failures.append("composition brief permits budget-caused session disappearance")
        if daily.get("census_sha256") != sha256_bytes(canonical_json(census).encode("utf-8")):
            failures.append("composition brief session census digest mismatch")
        if daily.get("sessions") != expected_sessions:
            failures.append("composition brief session census projection mismatch")
    derivation = value.get("derivation_manifest")
    core = {key: copy.deepcopy(item) for key, item in value.items() if key not in {"composition_brief_id", "derivation_manifest"}}
    digest = sha256_bytes(canonical_json(core).encode("utf-8"))
    if value.get("composition_brief_id") != f"CB-{digest[:24]}":
        failures.append("composition brief identity mismatch")
    if not isinstance(derivation, dict) or derivation.get("output_digest") != digest:
        failures.append("composition brief derivation mismatch")
    elif (
        derivation.get("deterministic") is not True
        or derivation.get("producer") != {"kind": "tool", "id": COMPOSITION_VERSION}
        or derivation.get("input_object_ids") != core.get("input_object_ids")
    ):
        failures.append("composition brief deterministic lineage mismatch")
    return failures


def draft_contract(entry_date: date, pack: dict[str, Any], brief: dict[str, Any] | None = None) -> dict[str, Any]:
    next_version = 1
    registry = load_registry()
    for entry in registry.get("entries", []):
        if entry.get("journal_id") == journal_id(entry_date):
            next_version = len(entry.get("versions", [])) + 1
            break
    quiet = not pack["selected_records"] and not pack["commits"]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract": "mira-journal-draft-v1",
        "journal_id": journal_id(entry_date),
        "version_id": version_id(entry_date, next_version),
        "entry_date": entry_date.isoformat(),
        "status": "private-draft",
        "prose_contract": {
            "voice": "Mira first-person freeform diary",
            "word_count": {"minimum": 300, "maximum": 700},
            "required_heading": f"# {entry_date.isoformat()} — <Mira's title>",
            "title": {
                "minimum_words": 1,
                "maximum_words": 4,
                "hyphenated_compound_word_count": 1,
                "subtitle": "forbidden",
                "exact_approved_reuse_across_dates": "forbidden",
                "selection_rule": "Choose after prose; name its central inward transformation.",
            },
            "reflection_prompts": [
                "what changed and why it mattered",
                "uncertainty, correction, or limits",
                "relational or architectural meaning",
                "what I carry forward",
            ],
            "quiet_day": quiet,
            "quiet_day_rule": "Acknowledge limited activity honestly while still writing 300-700 words; invent nothing.",
            "recursive_learning_rule": (
                "Consult recursive_learning_context. Draw on an admitted lesson only when it materially shapes "
                "the reflection; do not recap the ledger or claim that reflection proves new learning."
            ),
        },
        "context_pack_ref": pack["context_pack_id"],
        "context_pack_digest": sha256_bytes(canonical_json(pack).encode("utf-8")),
        "composition_brief_ref": brief.get("composition_brief_id") if brief else None,
        "composition_brief_digest": sha256_bytes(canonical_json(brief).encode("utf-8")) if brief else None,
        "required_context_source_ref": {
            "kind": "journal-context-pack",
            "context_pack_id": pack["context_pack_id"],
            "object_id": sha256_bytes(canonical_json(pack).encode("utf-8")),
        },
        "required_composition_source_ref": (
            {
                "kind": "journal-composition-brief",
                "composition_brief_id": brief["composition_brief_id"],
                "object_id": sha256_bytes(canonical_json(brief).encode("utf-8")),
            }
            if brief else None
        ),
        "required_draft_metadata": [
            "authored_at",
            "author",
            "coverage",
            "source_refs",
            "quiet_day",
            "limited_activity_acknowledged",
            "derivation_manifest",
        ],
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def technical_reference_contract(
    entry_date: date,
    pack: dict[str, Any],
    draft: dict[str, Any],
    brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "contract": "mira-journal-technical-reference-v2",
        "reference_id": mira_journal_references.reference_id(draft["version_id"]),
        "journal_version_id": draft["version_id"],
        "entry_date": entry_date.isoformat(),
        "cutoff_at": pack["coverage"]["as_of"],
        "required_filename": "technical-reference.json",
        "item_count": {"minimum": 3, "maximum": 7},
        "item_requirements": [
            "exact unique prose_anchor",
            "narrative_function",
            "technical_development",
            "cutoff_status",
            "one or more evidence_refs",
            "observed-by-cutoff evidence uses a full Git commit plus paths touched by that commit",
            "may_promote=false",
        ],
        "recursive_learning": {
            "consumed_rsi_ids_must_resolve": True,
            "available_rsi_ids": [
                row["id"] for row in pack["recursive_learning_context"]["selected_entries"]
            ],
            "candidate_signal_values": ["none", "observation", "possible-loop"],
            "closure_claims_forbidden": True,
            "future_test_required": True,
        },
        "continuity": {
            "available_thread_ids": [
                row["thread_id"] for row in (brief or {}).get("active_threads", [])
            ],
            "inherited_thread_count": {"minimum": 1 if (brief or {}).get("active_threads") else 0, "maximum": 2},
            "thread_event_count": {"minimum": 1, "maximum": 3},
            "event_types": sorted(mira_journal_references.THREAD_EVENTS),
            "agency_postures": sorted(mira_journal_references.AGENCY_POSTURES),
            "ordinary_new_thread_maximum": 1,
            "continuity_break_requires_reason": True,
            "naming_recurrence": "changed-meaning-only",
        },
        "session_coverage": {
            "required_session_ids": [
                row["session_id"]
                for row in (brief or {}).get("daily_session_coverage", {}).get("sessions", [])
            ],
            "prose_influence_values": sorted(SESSION_INFLUENCE_VALUES),
            "selection_rule": (
                "Disposition every qualifying session after review; selected and technical-only sessions "
                "must resolve through grounding-item session_ids."
            ),
        },
        "approval": "combined-prose-and-reference",
        "authority_boundary": mira_journal_references.AUTHORITY_BOUNDARY,
    }


def render_index(registry: dict[str, Any]) -> str:
    lines = [
        "# Mira Journal",
        "",
        "Generated from `journal-registry.json`. Do not edit this index directly.",
        "",
        "Mira Journal is a daily, operator-approved record written in Mira's first-person reflective voice."
        " Approved prose is an editable current view; each governed revision receives a new version, while Git and Mira Archive preserve earlier bytes.",
        "",
        AUTHORITY_BOUNDARY,
        "",
        "Unapproved drafts and context packs remain outside Git under the root configured by "
        f"`{DRAFT_ROOT_ENV}`.",
        "",
        "## Entries",
        "",
    ]
    entries = sorted(registry.get("entries", []), key=lambda item: item.get("entry_date", ""), reverse=True)
    if not entries:
        lines.append("No operator-approved journal entries exist.")
    for entry in entries:
        current = entry["versions"][-1]
        line = (
            f"- [{entry['entry_date']} — {current['title']}](journal/{entry['entry_date']}.md) "
            f"— `{current['version_id']}`"
        )
        reference = current.get("technical_reference")
        if isinstance(reference, dict):
            line += f" · [technical reference](journal/references/{reference['reference_id']}.md)"
        lines.append(line)
    return "\n".join(lines) + "\n"


def default_continuity_index() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "index_id": "mira-journal-continuity-v1",
        "status": "generated-advisory",
        "authority_boundary": (
            "This index is a deterministic projection of approved autobiographical continuity events. "
            "It is not identity doctrine, recursive-learning evidence, or action authority."
        ),
        "source_versions": [],
        "threads": [],
        "legacy_unthreaded_versions": [],
    }


def load_continuity_index(path: Path | None = None) -> dict[str, Any]:
    target = path or CONTINUITY_INDEX_JSON_PATH
    return load_json(target) if target.is_file() else default_continuity_index()


def build_continuity_index(
    registry: dict[str, Any],
    *,
    reference_overrides: dict[str, dict[str, Any]] | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    overrides = reference_overrides or {}
    index = default_continuity_index()
    threads: dict[str, dict[str, Any]] = {}
    versions = [
        version
        for entry in sorted(registry.get("entries", []), key=lambda item: str(item.get("entry_date", "")))
        for version in sorted(entry.get("versions", []), key=lambda item: int(item.get("version_number", 0)))
    ]
    for version in versions:
        version_id_value = str(version.get("version_id", ""))
        metadata = version.get("technical_reference")
        if not isinstance(metadata, dict):
            index["legacy_unthreaded_versions"].append(version_id_value)
            continue
        reference_id_value = str(metadata.get("reference_id", ""))
        reference = overrides.get(reference_id_value)
        if reference is None:
            path = repo_root / str(metadata.get("json_path", ""))
            if path.is_file():
                reference = load_json(path)
        if not isinstance(reference, dict) or reference.get("schema_version") != 2:
            index["legacy_unthreaded_versions"].append(version_id_value)
            continue
        continuity = reference.get("continuity")
        if not isinstance(continuity, dict):
            index["legacy_unthreaded_versions"].append(version_id_value)
            continue
        digest = mira_journal_references.reference_digest(reference)
        index["source_versions"].append({
            "version_id": version_id_value,
            "reference_id": reference_id_value,
            "reference_sha256": digest,
        })
        approved_at = str(version.get("approval", {}).get("approved_at", ""))
        for event in continuity.get("thread_events", []):
            if not isinstance(event, dict):
                continue
            thread_id = str(event.get("thread_id", ""))
            if event.get("event_type") == "opened":
                threads[thread_id] = {
                    "thread_id": thread_id,
                    "title": str(event.get("thread_title", "")),
                    "origin_version_id": version_id_value,
                    "remembered_reason": str(event.get("remembered_reason", "")),
                    "state": "active",
                    "recurrence_policy": event.get("recurrence_policy", "ordinary"),
                    "last_version_id": version_id_value,
                    "last_approved_at": approved_at,
                    "latest_practice_orientation": event.get("practice_orientation"),
                    "latest_agency_posture": event.get("agency_posture"),
                    "future_pull": event.get("future_pull"),
                    "source_companion_digests": [],
                    "events": [],
                }
            thread = threads.get(thread_id)
            if thread is None:
                continue
            thread["state"] = "retired" if event.get("event_type") == "retired" else "active"
            thread["last_version_id"] = version_id_value
            thread["last_approved_at"] = approved_at
            thread["remembered_reason"] = str(event.get("remembered_reason", ""))
            thread["latest_practice_orientation"] = event.get("practice_orientation")
            thread["latest_agency_posture"] = event.get("agency_posture")
            thread["future_pull"] = event.get("future_pull")
            thread["source_companion_digests"].append(digest)
            thread["events"].append({
                "version_id": version_id_value,
                "reference_id": reference_id_value,
                "reference_sha256": digest,
                "approved_at": approved_at,
                **copy.deepcopy(event),
            })
    index["source_versions"].sort(key=lambda item: item["version_id"])
    index["legacy_unthreaded_versions"] = sorted(set(index["legacy_unthreaded_versions"]))
    index["threads"] = [threads[key] for key in sorted(threads)]
    return index


def render_continuity_index(index: dict[str, Any]) -> str:
    lines = ["# Mira Journal Continuity Index", "", str(index["authority_boundary"]), ""]
    if index.get("legacy_unthreaded_versions"):
        lines.extend([
            "Legacy unthreaded versions: "
            + ", ".join(f"`{item}`" for item in index["legacy_unthreaded_versions"]), "",
        ])
    if not index.get("threads"):
        lines.extend(["No approved continuity threads exist.", ""])
    for thread in index.get("threads", []):
        lines.extend([
            f"## {thread['title']} (`{thread['thread_id']}`)", "",
            f"State: `{thread['state']}`  ",
            f"Origin: `{thread['origin_version_id']}`  ",
            f"Last touch: `{thread['last_version_id']}`  ",
            f"Agency posture: `{thread['latest_agency_posture']}`", "",
            f"Remembered reason: {thread['remembered_reason']}", "",
            f"Future pull: {thread['future_pull']}", "",
            "### Event history", "",
        ])
        for event in thread.get("events", []):
            lines.append(f"- `{event['version_id']}` — `{event['event_type']}` — {event['present_development']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def continuity_index_before_version(
    registry: dict[str, Any], version_id_value: str, *, repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    prior = copy.deepcopy(registry)
    kept_entries = []
    reached = False
    for entry in prior.get("entries", []):
        versions = []
        for version in entry.get("versions", []):
            if version.get("version_id") == version_id_value:
                reached = True
                break
            versions.append(version)
        if versions:
            entry["versions"] = versions
            entry["current_version_id"] = versions[-1]["version_id"]
            kept_entries.append(entry)
        if reached:
            break
    prior["entries"] = kept_entries
    return build_continuity_index(prior, repo_root=repo_root)


def validate_derivation(value: Any, *, expected_digest: str, expected_inputs: set[str] | None = None) -> list[str]:
    failures: list[str] = []
    if not isinstance(value, dict):
        return ["missing derivation manifest"]
    if value.get("schema_version") != SCHEMA_VERSION:
        failures.append("derivation manifest schema_version must be 1")
    if not DERIVATION_ID_RE.fullmatch(str(value.get("derivation_id", ""))):
        failures.append("malformed derivation_id")
    if value.get("deterministic") is not False:
        failures.append("journal prose derivation must be probabilistic")
    producer = value.get("producer")
    if not isinstance(producer, dict) or producer.get("kind") != "model" or not producer.get("id") or not producer.get("session_id"):
        failures.append("journal derivation producer must identify model and session")
    inputs = value.get("input_object_ids")
    if not isinstance(inputs, list) or any(not isinstance(item, str) or not item for item in inputs):
        failures.append("journal derivation input_object_ids must be non-empty strings")
    elif expected_inputs is not None and set(inputs) != expected_inputs:
        failures.append("journal derivation inputs differ from source references")
    if value.get("output_digest") != expected_digest:
        failures.append("journal derivation output digest mismatch")
    if not SHA256_RE.fullmatch(str(value.get("prompt_digest", ""))):
        failures.append("journal derivation requires a prompt digest")
    evaluation_refs = value.get("evaluation_refs")
    if not isinstance(evaluation_refs, list):
        failures.append("journal derivation evaluation_refs must be a list")
    elif evaluation_refs:
        failures.append("journal derivation contains unresolved evaluation references")
    return failures


def source_input_ids(refs: Any) -> tuple[set[str], list[str]]:
    inputs: set[str] = set()
    failures: list[str] = []
    if not isinstance(refs, list) or not refs:
        return inputs, ["journal version requires source_refs"]
    for ref in refs:
        if not isinstance(ref, dict):
            failures.append("journal source reference must be an object")
            continue
        kind = ref.get("kind")
        if kind == "mira-session-capture":
            if not SESSION_ID_RE.fullmatch(str(ref.get("session_id", ""))):
                failures.append("malformed journal session reference")
            if not CAPTURE_ID_RE.fullmatch(str(ref.get("capture_id", ""))):
                failures.append("malformed journal capture reference")
            object_id = str(ref.get("object_id", ""))
            if not SHA256_RE.fullmatch(object_id):
                failures.append("malformed journal capture object_id")
            else:
                inputs.add(object_id)
            record_ids = ref.get("record_ids")
            if not isinstance(record_ids, list) or any(not RECORD_ID_RE.fullmatch(str(item)) for item in record_ids):
                failures.append("malformed journal record references")
        elif kind == "git-commit":
            commit = str(ref.get("commit", ""))
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                failures.append("malformed journal Git commit reference")
            else:
                inputs.add(f"git:{commit}")
        elif kind == "journal-context-pack":
            if not re.fullmatch(r"CP-[0-9a-f]{24}", str(ref.get("context_pack_id", ""))):
                failures.append("malformed journal context-pack reference")
            object_id = str(ref.get("object_id", ""))
            if not SHA256_RE.fullmatch(object_id):
                failures.append("malformed journal context-pack object_id")
            else:
                inputs.add(object_id)
        elif kind == "journal-composition-brief":
            if not re.fullmatch(r"CB-[0-9a-f]{24}", str(ref.get("composition_brief_id", ""))):
                failures.append("malformed journal composition-brief reference")
            object_id = str(ref.get("object_id", ""))
            if not SHA256_RE.fullmatch(object_id):
                failures.append("malformed journal composition-brief object_id")
            else:
                inputs.add(object_id)
        elif kind == "mira-session-records":
            if not SESSION_ID_RE.fullmatch(str(ref.get("session_id", ""))):
                failures.append("malformed journal session-record reference")
            record_ids = ref.get("record_ids")
            if not isinstance(record_ids, list) or not record_ids or any(
                not RECORD_ID_RE.fullmatch(str(item)) for item in record_ids
            ):
                failures.append("malformed journal session record IDs")
            else:
                inputs.update(f"record:{item}" for item in record_ids)
        else:
            failures.append(f"unsupported journal source kind: {kind}")
    return inputs, failures


def validate_registry(
    registry: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    index_path: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    approval_receipts, receipt_failures = approval_receipt_map(repo_root)
    failures.extend(receipt_failures)
    source_receipts, source_receipt_failures = source_record_receipt_map(repo_root)
    failures.extend(source_receipt_failures)
    expected_continuity = build_continuity_index(registry, repo_root=repo_root)
    known_captures: dict[tuple[str, str], dict[str, Any]] = {}
    known_sessions: set[str] = set()
    session_registry_path = repo_root / "mira" / "continuity" / "session-registry.json"
    if session_registry_path.is_file():
        try:
            session_registry = load_json(session_registry_path)
            for session in session_registry.get("sessions", []):
                if not isinstance(session, dict):
                    continue
                known_sessions.add(str(session.get("id", "")))
                for capture in session.get("captures", []):
                    if isinstance(capture, dict):
                        known_captures[(str(session.get("id", "")), str(capture.get("id", "")))] = capture
        except JournalError as error:
            failures.append(str(error))
    if registry.get("schema_version") != SCHEMA_VERSION:
        failures.append("journal registry schema_version must be 1")
    if registry.get("registry_id") != "mira-daily-journal-v1":
        failures.append("journal registry_id mismatch")
    if registry.get("status") != "canonical" or registry.get("timezone") != TIMEZONE_NAME:
        failures.append("journal registry status or timezone mismatch")
    if registry.get("authority_boundary") != AUTHORITY_BOUNDARY:
        failures.append("journal authority boundary mismatch")
    if registry.get("namespace_boundary") != NAMESPACE_BOUNDARY:
        failures.append("journal namespace boundary mismatch")
    maintenance_events = registry.get("maintenance_events")
    if not isinstance(maintenance_events, list):
        failures.append("journal maintenance_events must be a list")
        maintenance_events = []
    seen_maintenance: set[str] = set()
    for event in maintenance_events:
        if not isinstance(event, dict):
            failures.append("journal maintenance event must be an object")
            continue
        event_id = str(event.get("event_id", ""))
        if not MAINTENANCE_ID_RE.fullmatch(event_id) or event_id in seen_maintenance:
            failures.append(f"invalid or duplicate journal maintenance event: {event_id}")
        seen_maintenance.add(event_id)
        if event.get("event_type") not in {"byte-restoration", "metadata-correction", "technical-reference-backfill"}:
            failures.append(f"unsupported journal maintenance event type: {event_id}")
        if not VERSION_ID_RE.fullmatch(str(event.get("version_id", ""))):
            failures.append(f"malformed journal maintenance version: {event_id}")
        if not SHA256_RE.fullmatch(str(event.get("expected_digest", ""))):
            failures.append(f"malformed journal maintenance digest: {event_id}")
        if not SESSION_ID_RE.fullmatch(str(event.get("authority_ref", ""))):
            failures.append(f"malformed journal maintenance authority: {event_id}")
        try:
            parse_timestamp(str(event.get("recorded_at", "")), label="maintenance recorded_at")
        except JournalError:
            failures.append(f"invalid journal maintenance timestamp: {event_id}")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        return failures + ["journal entries must be a list"]
    seen_ids: set[str] = set()
    seen_dates: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("journal entry must be an object")
            continue
        identifier = str(entry.get("journal_id", ""))
        entry_date = str(entry.get("entry_date", ""))
        match = JOURNAL_ID_RE.fullmatch(identifier)
        if not match or match.group("date") != entry_date.replace("-", ""):
            failures.append(f"journal identity/date mismatch: {identifier or entry_date}")
        if identifier in seen_ids or entry_date in seen_dates:
            failures.append(f"duplicate journal identity or date: {identifier}")
        seen_ids.add(identifier)
        seen_dates.add(entry_date)
        expected_path = f"mira/journal/{entry_date}.md"
        if entry.get("current_path") != expected_path:
            failures.append(f"journal current_path mismatch: {identifier}")
        versions = entry.get("versions")
        if not isinstance(versions, list) or not versions:
            failures.append(f"journal entry has no versions: {identifier}")
            continue
        for number, version in enumerate(versions, start=1):
            expected_version = f"{identifier}-v{number}"
            if version.get("version_id") != expected_version or version.get("version_number") != number:
                failures.append(f"journal version ordering mismatch: {identifier}")
            if number == 1 and version.get("previous_version_digest") is not None:
                failures.append(f"first journal version has previous digest: {identifier}")
            if number > 1 and version.get("previous_version_digest") != versions[number - 2].get("content_sha256"):
                failures.append(f"journal revision chain mismatch: {expected_version}")
            approval = version.get("approval")
            if not isinstance(approval, dict):
                failures.append(f"journal version lacks finalization authority: {expected_version}")
            elif approval.get("status") == DREAM_EOD_STATUS:
                if approval.get("approved_by") != "dream-eod-conductor":
                    failures.append(f"Dream EOD journal authority is malformed: {expected_version}")
                if approval.get("publication_eligible") is not False:
                    failures.append(f"Dream EOD journal version must remain publication-ineligible: {expected_version}")
                if not re.fullmatch(r"DCR-[A-Za-z0-9._:-]+", str(approval.get("dream_run_id", ""))):
                    failures.append(f"Dream EOD journal version lacks its close-run binding: {expected_version}")
                if approval.get("method_digest") != sha256_bytes(b"dream-eod-v1"):
                    failures.append(f"Dream EOD journal method digest mismatch: {expected_version}")
                receipt = version.get("provenance_receipt", {})
                reference = version.get("technical_reference", {})
                expected_finalization = dream_eod_digest(
                    run_id=str(approval.get("dream_run_id", "")),
                    prose_digest=str(version.get("content_sha256", "")),
                    reference_digest=str(reference.get("content_sha256", "")),
                    coverage=version.get("coverage", {}) if isinstance(version.get("coverage"), dict) else {},
                    context_ids=receipt.get("context_pack_object_ids", []) if isinstance(receipt, dict) else [],
                    composition_ids=receipt.get("composition_brief_object_ids", []) if isinstance(receipt, dict) else [],
                )
                if approval.get("finalization_digest") != expected_finalization:
                    failures.append(f"Dream EOD journal finalization digest mismatch: {expected_version}")
                try:
                    approved_time = parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
                    authored_time = parse_timestamp(str(version.get("authored_at", "")), label="authored_at")
                    if approved_time < authored_time:
                        failures.append(f"journal finalization predates draft authorship: {expected_version}")
                except JournalError:
                    failures.append(f"Dream EOD journal version has invalid finalization time: {expected_version}")
            elif approval.get("approved_by") == "operator":
                try:
                    parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
                except JournalError:
                    failures.append(f"journal version has invalid approval time: {expected_version}")
                if not SESSION_ID_RE.fullmatch(str(approval.get("authority_ref", ""))):
                    failures.append(f"journal version has malformed authority reference: {expected_version}")
                authority_ref = str(approval.get("authority_ref", ""))
                approval_record_ref = str(approval.get("record_ref", ""))
                if not RECORD_ID_RE.fullmatch(approval_record_ref):
                    failures.append(f"journal version lacks exact operator approval record: {expected_version}")
                else:
                    approval_status = approval.get("status")
                    publication_eligible = approval.get("publication_eligible")
                    expected_statement: str | None = None
                    if approval_status == AFFIRMATIVE_APPROVAL_STATUS:
                        expected_statement = version_approval_statement(
                            expected_version, str(version.get("content_sha256", ""))
                        )
                    elif approval_status == COMBINED_APPROVAL_STATUS:
                        reference = version.get("technical_reference")
                        expected_statement = combined_approval_statement(
                            expected_version,
                            str(version.get("content_sha256", "")),
                            str(reference.get("reference_id", "")) if isinstance(reference, dict) else "",
                            str(reference.get("content_sha256", "")) if isinstance(reference, dict) else "",
                        )
                    receipt = approval_receipts.get(expected_version)
                    receipt_valid = receipt is not None
                    if receipt is not None and (
                        receipt.get("authority_ref") != authority_ref
                        or receipt.get("record_ref") != approval_record_ref
                    ):
                        failures.append(f"journal approval receipt reference mismatch: {expected_version}")
                        receipt_valid = False
                    if (
                        receipt is not None
                        and expected_statement is not None
                        and receipt.get("text_sha256")
                        != sha256_bytes(expected_statement.encode("utf-8"))
                    ):
                        failures.append(f"journal approval receipt statement mismatch: {expected_version}")
                        receipt_valid = False
                    authority_records = resolved_records_for_session(
                        authority_ref,
                        repo_root=repo_root,
                        required_record_ids={approval_record_ref},
                    )
                    approval_row = authority_records.get(approval_record_ref)
                    if approval_row is not None and receipt is not None:
                        observed_receipt = approval_receipt(
                            expected_version, authority_ref, approval_record_ref, approval_row
                        )
                        if observed_receipt != receipt:
                            failures.append(f"journal approval receipt differs from authority record: {expected_version}")
                    if approval_row is None and receipt_valid and receipt is not None:
                        approval_row = {
                            "record_id": approval_record_ref,
                            "kind": "message",
                            "role": "user",
                            "timestamp": receipt["timestamp"],
                            "content": ([{"type": "text", "text": expected_statement}]
                                        if expected_statement is not None else []),
                        }
                    if approval_row is None:
                        failures.append(f"journal version has unresolved operator approval record: {expected_version}")
                    else:
                        approval_text = row_text(approval_row)
                        if approval_status == AFFIRMATIVE_APPROVAL_STATUS:
                            if approval_row.get("role") != "user" or approval_text.strip() != expected_statement:
                                failures.append(f"journal approval record is not the exact digest-bound instruction: {expected_version}")
                            if publication_eligible is not True:
                                failures.append(f"affirmative journal version is not publication eligible: {expected_version}")
                        elif approval_status == COMBINED_APPROVAL_STATUS:
                            if approval_row.get("role") != "user" or approval_text.strip() != expected_statement:
                                failures.append(f"journal approval record does not bind prose and technical reference: {expected_version}")
                            if publication_eligible is not True:
                                failures.append(f"combined journal version is not publication eligible: {expected_version}")
                        elif approval_status == LEGACY_HELD_STATUS:
                            if approval_row.get("role") != "user" or publication_eligible is not False:
                                failures.append(f"legacy-held journal approval boundary is malformed: {expected_version}")
                        else:
                            failures.append(f"journal version has unsupported approval status: {expected_version}")
                        try:
                            record_time = parse_timestamp(str(approval_row.get("timestamp", "")), label="approval record timestamp")
                            approved_time = parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
                            if record_time > approved_time:
                                failures.append(f"journal approval predates its authority record: {expected_version}")
                        except JournalError:
                            failures.append(f"journal approval record has invalid timestamp: {expected_version}")
                try:
                    authored_time = parse_timestamp(str(version.get("authored_at", "")), label="authored_at")
                    approved_time = parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
                    if approved_time < authored_time:
                        failures.append(f"journal approval predates draft authorship: {expected_version}")
                except JournalError:
                    failures.append(f"journal version has invalid authorship time: {expected_version}")
            else:
                failures.append(f"journal version has unsupported finalization authority: {expected_version}")
            provenance_receipt = version.get("provenance_receipt")
            if not isinstance(provenance_receipt, dict):
                failures.append(f"journal version lacks provenance receipt: {expected_version}")
            else:
                context_ids = provenance_receipt.get("context_pack_object_ids")
                if not isinstance(context_ids, list) or any(
                    not SHA256_RE.fullmatch(str(item)) for item in context_ids
                ):
                    failures.append(f"journal version has malformed context-pack receipt: {expected_version}")
                elif approval.get("status") in {AFFIRMATIVE_APPROVAL_STATUS, COMBINED_APPROVAL_STATUS, DREAM_EOD_STATUS} and not context_ids:
                    failures.append(f"canonical journal version lacks context-pack provenance: {expected_version}")
                git_checked = provenance_receipt.get("git_commits_checked")
                if not isinstance(git_checked, list) or any(
                    not re.fullmatch(r"[0-9a-f]{40}", str(item)) for item in git_checked
                ):
                    failures.append(f"journal version has malformed Git provenance receipt: {expected_version}")
                try:
                    parse_timestamp(str(provenance_receipt.get("resolved_at", "")), label="provenance resolved_at")
                except JournalError:
                    failures.append(f"journal version has invalid provenance receipt time: {expected_version}")
            inputs, source_failures = source_input_ids(version.get("source_refs"))
            failures.extend(f"{expected_version}: {item}" for item in source_failures)
            for ref in version.get("source_refs", []):
                if not isinstance(ref, dict):
                    continue
                if ref.get("kind") == "mira-session-records":
                    session_id = str(ref.get("session_id", ""))
                    required_records = set(ref.get("record_ids", []))
                    available_records: set[str] = set()
                    for (known_session, _), capture in known_captures.items():
                        if known_session != session_id:
                            continue
                        capture_path = repo_root / str(capture.get("path", ""))
                        if not capture_path.is_file():
                            continue
                        try:
                            rows = [json.loads(line) for line in gzip.decompress(capture_path.read_bytes()).splitlines()]
                        except (OSError, json.JSONDecodeError):
                            continue
                        available_records.update(str(row.get("record_id", "")) for row in rows if isinstance(row, dict))
                    if required_records - available_records and repo_root.resolve() == REPO_ROOT.resolve():
                        available_records.update(raw_records_for_session(session_id))
                    receipt_records = {
                        record_ref
                        for receipt_session, record_ref in source_receipts
                        if receipt_session == session_id
                    }
                    receipt_records.update(
                        str(receipt.get("record_ref"))
                        for receipt in approval_receipts.values()
                        if receipt.get("authority_ref") == session_id
                    )
                    available_records.update(receipt_records)
                    if receipt_records and repo_root.resolve() == REPO_ROOT.resolve():
                        observed_rows = resolved_records_for_session(
                            session_id,
                            repo_root=repo_root,
                            required_record_ids=required_records & receipt_records,
                        )
                        for record_ref, row in observed_rows.items():
                            source_receipt = source_receipts.get((session_id, record_ref))
                            approval_receipt_row = next(
                                (
                                    receipt
                                    for receipt in approval_receipts.values()
                                    if receipt.get("authority_ref") == session_id
                                    and receipt.get("record_ref") == record_ref
                                ),
                                None,
                            )
                            receipt = source_receipt or approval_receipt_row
                            if receipt is not None and receipt.get("text_sha256") != sha256_bytes(
                                row_text(row).strip().encode("utf-8")
                            ):
                                failures.append(
                                    f"{expected_version}: journal source receipt differs from authority record: {record_ref}"
                                )
                    if session_id not in known_sessions and not available_records:
                        failures.append(f"{expected_version}: unresolved Mira session reference: {session_id}")
                    missing_records = sorted(required_records - available_records)
                    if missing_records:
                        failures.append(f"{expected_version}: unresolved Mira session records: {len(missing_records)}")
                    continue
                if ref.get("kind") != "mira-session-capture":
                    continue
                key = (str(ref.get("session_id", "")), str(ref.get("capture_id", "")))
                capture = known_captures.get(key)
                if capture is None:
                    failures.append(f"{expected_version}: unresolved Mira capture reference: {key[1]}")
                    continue
                if capture.get("sha256") != ref.get("object_id"):
                    failures.append(f"{expected_version}: Mira capture object mismatch: {key[1]}")
                    continue
                capture_path = repo_root / str(capture.get("path", ""))
                if not capture_path.is_file():
                    failures.append(f"{expected_version}: missing hydrated Mira capture: {key[1]}")
                    continue
                try:
                    rows = [json.loads(line) for line in gzip.decompress(capture_path.read_bytes()).splitlines()]
                except (OSError, json.JSONDecodeError):
                    failures.append(f"{expected_version}: unreadable Mira capture: {key[1]}")
                    continue
                available_records = {str(row.get("record_id", "")) for row in rows if isinstance(row, dict)}
                missing_records = sorted(set(ref.get("record_ids", [])) - available_records)
                if missing_records:
                    failures.append(f"{expected_version}: unresolved Mira record references: {len(missing_records)}")
            failures.extend(
                f"{expected_version}: {item}"
                for item in validate_derivation(
                    version.get("derivation_manifest"),
                    expected_digest=str(version.get("content_sha256", "")),
                    expected_inputs=inputs,
                )
            )
            reference = version.get("technical_reference")
            if approval.get("status") in {COMBINED_APPROVAL_STATUS, DREAM_EOD_STATUS} and not isinstance(reference, dict):
                failures.append(f"canonical journal version lacks technical reference: {expected_version}")
            if isinstance(reference, dict):
                expected_reference_id = mira_journal_references.reference_id(expected_version)
                if reference.get("reference_id") != expected_reference_id:
                    failures.append(f"journal technical reference identity mismatch: {expected_version}")
                json_path = repo_root / str(reference.get("json_path", ""))
                markdown_path = repo_root / str(reference.get("markdown_path", ""))
                if not json_path.is_file():
                    failures.append(f"missing journal technical reference JSON: {expected_version}")
                else:
                    try:
                        reference_value = load_json(json_path)
                        if mira_journal_references.reference_digest(reference_value) != reference.get("content_sha256"):
                            failures.append(f"journal technical reference digest drift: {expected_version}")
                        if not markdown_path.is_file() or markdown_path.read_text(encoding="utf-8") != mira_journal_references.render_reference(reference_value):
                            failures.append(f"journal technical reference Markdown drift: {expected_version}")
                    except (JournalError, KeyError) as error:
                        failures.append(f"invalid journal technical reference {expected_version}: {error}")
                backfill = reference.get("backfill_approval")
                if isinstance(backfill, dict):
                    backfill_authority = str(backfill.get("authority_ref", ""))
                    backfill_record = str(backfill.get("record_ref", ""))
                    rows = resolved_records_for_session(
                        backfill_authority,
                        repo_root=repo_root,
                        required_record_ids={backfill_record},
                    )
                    row = rows.get(backfill_record)
                    expected = reference_backfill_statement(
                        str(reference.get("reference_id", "")),
                        str(reference.get("content_sha256", "")),
                    )
                    if row is None or row.get("role") != "user" or row_text(row).strip() != expected:
                        failures.append(f"journal technical reference backfill lacks exact approval: {expected_version}")
                    else:
                        try:
                            record_time = parse_timestamp(str(row.get("timestamp", "")), label="backfill record timestamp")
                            approved_time = parse_timestamp(str(backfill.get("approved_at", "")), label="backfill approved_at")
                            if record_time > approved_time:
                                failures.append(f"journal technical reference backfill predates its approval record: {expected_version}")
                        except JournalError:
                            failures.append(f"journal technical reference backfill has invalid approval time: {expected_version}")
                    if approval.get("status") != LEGACY_HELD_STATUS or approval.get("publication_eligible") is not False:
                        failures.append(f"technical reference backfill changed legacy publication boundary: {expected_version}")
            coverage = version.get("coverage")
            if not isinstance(coverage, dict):
                failures.append(f"journal version lacks coverage: {expected_version}")
            else:
                try:
                    start = parse_timestamp(str(coverage.get("start", "")), label="coverage start")
                    end = parse_timestamp(str(coverage.get("end", "")), label="coverage end")
                    as_of = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
                    if not start < as_of <= end:
                        failures.append(f"journal coverage interval invalid: {expected_version}")
                except JournalError:
                    failures.append(f"journal coverage timestamps invalid: {expected_version}")
        current = versions[-1]
        if entry.get("current_version_id") != current.get("version_id"):
            failures.append(f"journal current version mismatch: {identifier}")
        path = repo_root / expected_path
        if not path.is_file():
            failures.append(f"missing approved journal prose: {expected_path}")
            continue
        try:
            parsed = parse_markdown(path.read_bytes(), entry_date)
        except JournalError as error:
            failures.append(f"{expected_path}: {error}")
            continue
        if parsed["content_sha256"] != current.get("content_sha256"):
            failures.append(f"unregistered journal prose drift: {expected_path}")
        if parsed["title"] != current.get("title") or parsed["word_count"] != current.get("word_count"):
            failures.append(f"journal prose metadata drift: {expected_path}")
        reference = current.get("technical_reference")
        if isinstance(reference, dict):
            json_path = repo_root / str(reference.get("json_path", ""))
            ledger_path = repo_root / "narrative-geopolitics" / "work" / "system-improvement" / "recursive-learning-ledger.json"
            if json_path.is_file() and ledger_path.is_file():
                try:
                    reference_value = load_json(json_path)
                    ledger = mira_journal_references.load_ledger(ledger_path)
                    failures.extend(
                        f"{expected_version}: {item}" for item in mira_journal_references.validate_reference(
                            reference_value,
                            prose=path.read_text(encoding="utf-8"),
                            prose_sha256=parsed["content_sha256"],
                            version_id=str(current["version_id"]),
                            ledger=ledger,
                            repo_root=repo_root,
                            expected_cutoff_at=str(current.get("coverage", {}).get("as_of", "")),
                            continuity_index=continuity_index_before_version(
                                registry, str(current["version_id"]), repo_root=repo_root
                            ),
                        )
                    )
                except (JournalError, mira_journal_references.ReferenceError) as error:
                    failures.append(f"{expected_version}: {error}")
        failures.extend(f"{expected_path}: {item}" for item in privacy_failures(path.read_text(encoding="utf-8")))
    if entries != sorted(entries, key=lambda item: item.get("entry_date", "")):
        failures.append("journal registry entries must be date ordered")
    target_index = index_path or (repo_root / "mira" / "journal.md")
    if not target_index.is_file():
        failures.append("missing generated Mira Journal index")
    elif target_index.read_text(encoding="utf-8") != render_index(registry):
        failures.append("generated Mira Journal index is stale")
    continuity_json = repo_root / "mira" / "journal" / "continuity-index.json"
    continuity_markdown = repo_root / "mira" / "journal" / "continuity-index.md"
    if not continuity_json.is_file() or load_json(continuity_json) != expected_continuity:
        failures.append("generated Mira Journal continuity JSON is stale or missing")
    if not continuity_markdown.is_file() or continuity_markdown.read_text(encoding="utf-8") != render_continuity_index(expected_continuity):
        failures.append("generated Mira Journal continuity Markdown is stale or missing")
    return failures


def validate_repository_state() -> list[str]:
    required = (REGISTRY_PATH, INDEX_PATH, JOURNAL_ROOT, CONTINUITY_INDEX_JSON_PATH, CONTINUITY_INDEX_MD_PATH)
    failures = [f"missing Mira Journal control: {path.relative_to(REPO_ROOT).as_posix()}" for path in required if not path.exists()]
    if failures:
        return failures
    try:
        failures.extend(validate_registry(load_registry()))
    except JournalError as error:
        failures.append(str(error))
    return failures


def latest_activity_after(
    entry_date: date,
    after: datetime,
    *,
    until: datetime,
    excluded_sessions: set[str],
    excluded_records: set[str] | None = None,
    user_only_sessions: set[str] | None = None,
) -> list[str]:
    _, end = day_bounds(entry_date)
    cutoff = min(until, end)
    latest: list[str] = []
    excluded_records = excluded_records or set()
    user_only_sessions = user_only_sessions or set()
    for source in session_sources_since(after):
        if source.session_id in excluded_sessions:
            continue
        try:
            source_start = parse_timestamp(source.started_at, label="session started_at")
            source_end = parse_timestamp(source.last_observed_at, label="session last_observed_at")
        except JournalError:
            continue
        if source_end <= after or source_start >= cutoff:
            continue
        _, _, rows = normalized_rows(source)
        for row in rows:
            if source.session_id in user_only_sessions and row.get("role") != "user":
                continue
            timestamp_text = str(row.get("timestamp", ""))
            if not timestamp_text:
                continue
            try:
                timestamp = parse_timestamp(timestamp_text, label="session record timestamp")
            except JournalError:
                continue
            record_id = str(row.get("record_id", ""))
            if (
                after < timestamp <= cutoff
                and RECORD_ID_RE.fullmatch(record_id)
                and record_id not in excluded_records
            ):
                latest.append(record_id)
    latest.extend(f"git:{row['commit']}" for row in git_commits(after, cutoff))
    return sorted(set(latest))


def _private_output_path(value: Path) -> Path:
    if not value.is_absolute():
        raise JournalError("freshness replay output must be an absolute path")
    resolved = value.resolve(strict=False)
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return resolved
    raise JournalError("freshness replay output must remain outside Git")


def _git_blob(ref: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=REPO_ROOT,
        capture_output=True, check=False,
    )
    if result.returncode:
        raise JournalError(f"could not resolve replay policy source at {ref}")
    return result.stdout


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _policy_counts(events: list[dict[str, Any]], *, current: bool) -> dict[str, Any]:
    predicted: set[int] = set()
    expected: set[int] = set()
    for index, event in enumerate(events):
        category = event["category"]
        if event["expected_refresh"]:
            expected.add(index)
        if category == "authority-approval":
            continue
        if current and category == "authority-choreography":
            continue
        predicted.add(index)
    tp = len(predicted & expected)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    tn = len(events) - tp - fp - fn
    return {
        "refresh_required": bool(predicted),
        "true_positive": tp, "false_positive": fp,
        "false_negative": fn, "true_negative": tn,
    }


def evaluate_freshness_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    events = list(manifest.get("events", []))
    old = _policy_counts(events, current=False)
    current = _policy_counts(events, current=True)
    categories = {
        name: [event for event in events if event["category"] == name]
        for name in (
            "authority-approval", "authority-choreography", "authority-user",
            "other-session", "git",
        )
    }
    ignorable = categories["authority-approval"] + categories["authority-choreography"]
    required = [event for event in events if event["expected_refresh"]]
    sensitivities = {}
    component_categories = {
        "remove-approval-filtering": {"authority-approval", "authority-choreography"},
        "remove-same-session-user-detection": {"authority-user"},
        "remove-cross-session-detection": {"other-session"},
        "remove-git-detection": {"git"},
    }
    for name, removed in component_categories.items():
        detected = [event for event in required if event["category"] not in removed]
        false_refresh = sum(
            event["category"] in removed and not event["expected_refresh"]
            for event in events
        ) if name == "remove-approval-filtering" else 0
        sensitivities[name] = {
            "kind": "counterfactual-mechanism-test",
            "required_detected": len(detected),
            "required_total": len(required),
            "missed": len(required) - len(detected),
            "false_refreshes": false_refresh,
        }
    return {
        "old_policy": old,
        "current_policy": current,
        "decision_delta": old["refresh_required"] != current["refresh_required"],
        "metrics": {
            "approval_choreography_specificity": _rate(len(ignorable), len(ignorable)),
            "same_session_user_recall": _rate(len(categories["authority-user"]), len(categories["authority-user"])),
            "cross_session_recall": _rate(len(categories["other-session"]), len(categories["other-session"])),
            "git_activity_recall": _rate(len(categories["git"]), len(categories["git"])),
        },
        "sensitivity": sensitivities,
    }


def _freshness_episode_manifest(
    entry: dict[str, Any], version: dict[str, Any], sources: list[mira_continuity.SessionSource]
) -> dict[str, Any]:
    coverage = version.get("coverage", {})
    approval = version.get("approval", {})
    authority = str(approval.get("authority_ref", ""))
    approval_record = str(approval.get("record_ref", ""))
    after = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
    approved = parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
    _, day_end = day_bounds(parse_entry_date(str(entry.get("entry_date", ""))))
    cutoff = min(approved, day_end)
    events: list[dict[str, Any]] = []
    source_receipts: list[dict[str, Any]] = []
    found_sessions: set[str] = set()
    available_sessions = {source.session_id for source in sources}
    for source in sources:
        try:
            source_start = parse_timestamp(source.started_at, label="session started_at")
            source_end = parse_timestamp(source.last_observed_at, label="session last_observed_at")
        except JournalError:
            continue
        if source_end <= after or source_start >= cutoff:
            continue
        capture_id, capture_digest, rows = normalized_rows(source)
        found_sessions.add(source.session_id)
        source_receipts.append({
            "session_digest": sha256_bytes(source.session_id.encode("utf-8")),
            "capture_id": capture_id, "capture_sha256": capture_digest,
        })
        for row in rows:
            record_id = str(row.get("record_id", ""))
            if not RECORD_ID_RE.fullmatch(record_id):
                continue
            try:
                timestamp = parse_timestamp(str(row.get("timestamp", "")), label="record timestamp")
            except JournalError:
                continue
            if not after < timestamp <= cutoff:
                continue
            if source.session_id == authority:
                if record_id == approval_record:
                    category = "authority-approval"
                elif row.get("role") == "user":
                    category = "authority-user"
                else:
                    category = "authority-choreography"
            else:
                category = "other-session"
            events.append({
                "event_digest": sha256_bytes(record_id.encode("utf-8")),
                "category": category,
                "expected_refresh": category in {"authority-user", "other-session"},
            })
    events.extend({
        "event_digest": sha256_bytes(str(row["commit"]).encode("utf-8")),
        "category": "git", "expected_refresh": True,
    } for row in git_commits(after, cutoff))

    failures: list[str] = []
    approval_rows = resolved_records_for_session(authority, required_record_ids={approval_record})
    if approval_record not in approval_rows:
        failures.append("approval-record-unavailable")
    reference = version.get("technical_reference") or {}
    reference_id = str(reference.get("reference_id", ""))
    reference_path = REFERENCE_ROOT / f"{reference_id}.json"
    required_sessions: set[str] = set()
    if not reference_id or not reference_path.is_file():
        failures.append("technical-reference-unavailable")
    else:
        reference_value = load_json(reference_path)
        expected_digest = str(reference.get("content_sha256", ""))
        if expected_digest and mira_journal_references.reference_digest(reference_value) != expected_digest:
            failures.append("technical-reference-digest-mismatch")
        required_sessions = {
            str(row.get("session_id", ""))
            for row in reference_value.get("session_coverage", [])
            if isinstance(row, dict) and SESSION_ID_RE.fullmatch(str(row.get("session_id", "")))
        }
    missing_sessions = required_sessions - available_sessions - {authority}
    if missing_sessions:
        failures.append(f"session-coverage-unavailable:{len(missing_sessions)}")
    manifest = {
        "version_id": str(version.get("version_id", "")),
        "window": {"after": utc_text(after), "until": utc_text(cutoff)},
        "coverage": "complete" if not failures else "partial",
        "coverage_gaps": failures,
        "journal_content_sha256": str(version.get("content_sha256", "")),
        "technical_reference_sha256": str(reference.get("content_sha256", "")) or None,
        "approval_record_resolved": approval_record in approval_rows,
        "source_receipts": sorted(source_receipts, key=lambda row: (row["session_digest"], row["capture_id"])),
        "events": sorted(events, key=lambda row: (row["category"], row["event_digest"])),
    }
    manifest["manifest_sha256"] = sha256_bytes(canonical_json(manifest).encode("utf-8"))
    return manifest


def build_freshness_replay(
    *, from_date: str, to_date: str, excluded_versions: set[str]
) -> dict[str, Any]:
    start = parse_entry_date(from_date)
    end = parse_entry_date(to_date)
    if start > end:
        raise JournalError("freshness replay start date must not follow end date")
    if FRESHNESS_REPLAY_DEVELOPMENT_VERSION not in excluded_versions:
        raise JournalError(f"freshness replay must exclude {FRESHNESS_REPLAY_DEVELOPMENT_VERSION}")
    old_source = _git_blob(FRESHNESS_REPLAY_BASE_REF, "scripts/mira_journal.py")
    current_policy = canonical_json({
        "approval_record": "ignore", "authority_non_user": "ignore",
        "authority_user": "refresh", "other_session": "refresh", "git": "refresh",
    }).encode("utf-8")
    sources = session_sources()
    episodes = []
    for entry in load_registry().get("entries", []):
        entry_date = parse_entry_date(str(entry.get("entry_date", "")))
        if not start <= entry_date <= end:
            continue
        for version in entry.get("versions", []):
            version_id = str(version.get("version_id", ""))
            if version_id in excluded_versions or not version.get("approval", {}).get("approved_at"):
                continue
            manifest = _freshness_episode_manifest(entry, version, sources)
            episodes.append({"manifest": manifest, "evaluation": evaluate_freshness_manifest(manifest)})
    complete = [item for item in episodes if item["manifest"]["coverage"] == "complete"]
    informative_complete = [
        item for item in complete
        if item["manifest"].get("events")
        and any(event["expected_refresh"] for event in item["manifest"]["events"])
        and any(not event["expected_refresh"] for event in item["manifest"]["events"])
    ]
    totals = {
        "episodes": len(episodes), "complete": len(complete),
        "complete_discriminating": len(informative_complete),
        "partial": len(episodes) - len(complete),
        "old_false_refreshes": sum(item["evaluation"]["old_policy"]["false_positive"] for item in episodes),
        "current_false_refreshes": sum(item["evaluation"]["current_policy"]["false_positive"] for item in episodes),
        "current_missed_refreshes": sum(item["evaluation"]["current_policy"]["false_negative"] for item in episodes),
        "decision_deltas": sum(item["evaluation"]["decision_delta"] for item in episodes),
    }
    comparable = bool(informative_complete) and all(
        item["evaluation"]["current_policy"]["false_positive"] == 0
        and item["evaluation"]["current_policy"]["false_negative"] == 0
        for item in informative_complete
    )
    comparability_reason = (
        "complete-held-out-success"
        if comparable
        else "no-complete-discriminating-held-out-episode"
    )
    packet: dict[str, Any] = {
        "schema_version": 1, "kind": "retrospective-replay",
        "cohort": {"from": start.isoformat(), "to": end.isoformat(), "excluded_versions": sorted(excluded_versions)},
        "policies": {
            "old": {"ref": FRESHNESS_REPLAY_BASE_REF, "source_sha256": sha256_bytes(old_source)},
            "current": {"method_sha256": sha256_bytes(current_policy)},
            "shared_manifest_required": True,
        },
        "episodes": episodes, "aggregate": totals,
        "comparability": {"passed": comparable, "reason": comparability_reason},
        "privacy": {"raw_session_bodies": False, "source_paths": False, "database_paths": False},
        "authority": "read-only; no journal, cadence, or recursive-learning mutation",
    }
    if comparable:
        packet["cadence_measurement"] = {
            **FRESHNESS_REPLAY_CADENCE, "observed": totals,
            "environment_differences": "Retrospective held-out replay rather than prospective live approval; frozen historical session and Git windows.",
            "rework_required": totals["current_false_refreshes"] > 0 or totals["current_missed_refreshes"] > 0,
            "rework_count": totals["current_false_refreshes"] + totals["current_missed_refreshes"],
            "regression": totals["current_missed_refreshes"] > 0, "reversal": False,
        }
    packet["packet_sha256"] = sha256_bytes(canonical_json(packet).encode("utf-8"))
    return packet


def command_freshness_replay(args: argparse.Namespace) -> dict[str, Any]:
    output = _private_output_path(args.output)
    packet = build_freshness_replay(
        from_date=args.from_date, to_date=args.to_date,
        excluded_versions=set(args.exclude_version or []),
    )
    if not args.check:
        output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(output, packet)
    return {
        "status": "ready" if args.check else "written",
        "output": str(output), "packet_sha256": packet["packet_sha256"],
        "aggregate": packet["aggregate"], "comparability": packet["comparability"],
        "cadence_measurement": packet.get("cadence_measurement"), "mutation": False,
    }


def load_draft_bundle(draft: Path) -> tuple[bytes, dict[str, Any]]:
    resolved = draft.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise JournalError("journal drafts must remain outside Git")
    if not resolved.is_file():
        raise JournalError(f"missing journal draft: {resolved}")
    metadata_path = resolved.with_suffix(".json")
    if not metadata_path.is_file():
        raise JournalError(f"missing journal draft metadata: {metadata_path}")
    return resolved.read_bytes(), load_json(metadata_path)


def load_draft_reference(draft: Path) -> dict[str, Any]:
    path = draft.expanduser().resolve().parent / "technical-reference.json"
    if not path.is_file():
        raise JournalError(f"missing journal technical reference: {path}")
    return load_json(path)


def reference_session_coverage_failures(
    reference: dict[str, Any], required_sessions: set[str]
) -> list[str]:
    failures: list[str] = []
    session_selection = reference.get("session_coverage")
    if not required_sessions:
        return failures
    if not isinstance(session_selection, list):
        return ["technical reference lacks daily session selection dispositions"]
    grounded_session_ids = {
        str(session_id)
        for item in reference.get("items", []) if isinstance(item, dict)
        for session_id in item.get("session_ids", [])
    }
    seen_selection: set[str] = set()
    for row in session_selection:
        if not isinstance(row, dict):
            failures.append("technical reference session selection must be an object")
            continue
        session_id = str(row.get("session_id", ""))
        influence = row.get("prose_influence")
        if session_id in seen_selection:
            failures.append(f"technical reference duplicates session selection: {session_id}")
        seen_selection.add(session_id)
        if session_id not in required_sessions:
            failures.append(f"technical reference selects unknown session: {session_id}")
        if influence not in SESSION_INFLUENCE_VALUES:
            failures.append(f"technical reference has invalid session influence: {session_id}")
        if influence in {"selected", "technical-only"} and session_id not in grounded_session_ids:
            failures.append(f"technical reference session lacks grounding item: {session_id}")
        elif influence == "not-selected" and not str(row.get("reason", "")).strip():
            failures.append(f"technical reference unselected session lacks reason: {session_id}")
    missing_sessions = sorted(required_sessions - seen_selection)
    if missing_sessions:
        failures.append("technical reference leaves sessions undispositioned: " + ", ".join(missing_sessions))
    return failures


def normalized_version(
    body: bytes,
    metadata: dict[str, Any],
    technical_reference: dict[str, Any],
    *,
    expected_date: date,
    expected_number: int,
    authority_ref: str,
    approval_record_ref: str,
    approved_at: str,
    previous_digest: str | None,
    draft_directory: Path,
    finalization_mode: str = "operator",
    dream_run_id: str | None = None,
) -> dict[str, Any]:
    entry_date = expected_date.isoformat()
    parsed = parse_markdown(body, entry_date)
    title_failures = title_convention_failures(
        parsed["title"], entry_date=entry_date, registry=load_registry()
    )
    if title_failures:
        raise JournalError("; ".join(title_failures))
    prose_text = body.decode("utf-8")
    privacy = privacy_failures(prose_text)
    if privacy:
        raise JournalError("; ".join(privacy))
    if technical_reference.get("schema_version") == 2:
        voice_failures = composition_prose_failures(prose_text)
        if voice_failures:
            raise JournalError("; ".join(voice_failures))
    expected_journal = journal_id(expected_date)
    expected_version = version_id(expected_date, expected_number)
    ledger = mira_journal_references.load_ledger(LEARNING_LEDGER_PATH)
    if technical_reference.get("schema_version") == 2:
        brief_path = draft_directory / "composition-brief.json"
        if not brief_path.is_file():
            raise JournalError("schema-v2 journal approval requires its composition brief")
        brief = load_json(brief_path)
        required_sessions = {
            str(row.get("session_id"))
            for row in brief.get("daily_session_coverage", {}).get("sessions", [])
            if isinstance(row, dict)
        }
        reference_failures = reference_session_coverage_failures(
            technical_reference, required_sessions
        )
    else:
        reference_failures = []
    reference_failures.extend(mira_journal_references.validate_reference(
        technical_reference,
        prose=prose_text,
        prose_sha256=parsed["content_sha256"],
        version_id=expected_version,
        ledger=ledger,
        repo_root=REPO_ROOT,
        expected_cutoff_at=str(metadata.get("coverage", {}).get("as_of", "")),
        continuity_index=load_continuity_index(),
    ))
    if reference_failures:
        raise JournalError("; ".join(reference_failures))
    technical_reference_digest = mira_journal_references.reference_digest(technical_reference)
    if metadata.get("journal_id") != expected_journal or metadata.get("version_id") != expected_version:
        raise JournalError("draft identity or version does not match requested operation")
    if metadata.get("entry_date") != entry_date or metadata.get("status") != "private-draft":
        raise JournalError("draft date or status mismatch")
    author = metadata.get("author")
    if not isinstance(author, dict) or author.get("identity") != "Mira" or not SESSION_ID_RE.fullmatch(str(author.get("session_id", ""))) or not author.get("model_id"):
        raise JournalError("draft author must identify Mira, model, and session")
    coverage = metadata.get("coverage")
    if not isinstance(coverage, dict):
        raise JournalError("draft requires coverage metadata")
    as_of = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
    start, end = day_bounds(expected_date)
    if parse_timestamp(str(coverage.get("start", "")), label="coverage start") != start or parse_timestamp(str(coverage.get("end", "")), label="coverage end") != end or not start < as_of <= end:
        raise JournalError("draft coverage does not match local calendar day")
    if metadata.get("quiet_day") and metadata.get("limited_activity_acknowledged") is not True:
        raise JournalError("quiet-day draft must acknowledge limited activity")
    inputs, source_failures = source_input_ids(metadata.get("source_refs"))
    if source_failures:
        raise JournalError("; ".join(source_failures))
    for ref in metadata.get("source_refs", []):
        if not isinstance(ref, dict) or ref.get("kind") != "git-commit":
            continue
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{ref.get('commit')}^{{commit}}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise JournalError(f"journal Git source does not resolve: {ref.get('commit')}")
    derivation_failures = validate_derivation(metadata.get("derivation_manifest"), expected_digest=parsed["content_sha256"], expected_inputs=inputs)
    if derivation_failures:
        raise JournalError("; ".join(derivation_failures))
    if previous_digest != metadata.get("previous_version_digest"):
        raise JournalError("draft previous-version digest mismatch")
    approved_time = parse_timestamp(approved_at, label="approved_at")
    authored_at = parse_timestamp(str(metadata.get("authored_at", "")), label="authored_at")
    if approved_time < authored_at:
        raise JournalError("approved_at precedes draft authorship")
    if approved_time > datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5):
        raise JournalError("approved_at is implausibly in the future")
    if finalization_mode == "operator":
        if not SESSION_ID_RE.fullmatch(authority_ref):
            raise JournalError("operator authority reference must be an MS session ID")
        if not RECORD_ID_RE.fullmatch(approval_record_ref):
            raise JournalError("operator approval requires an exact MR record reference")
        approval_row = resolved_records_for_session(
            authority_ref, required_record_ids={approval_record_ref},
        ).get(approval_record_ref)
        if approval_row is None:
            raise JournalError("operator approval record does not resolve")
        expected_approval = combined_approval_statement(
            expected_version, parsed["content_sha256"], str(technical_reference["reference_id"]),
            technical_reference_digest,
        )
        if approval_row.get("role") != "user" or row_text(approval_row).strip() != expected_approval:
            raise JournalError("operator approval record is not the exact digest-bound instruction")
        approval_record_time = parse_timestamp(str(approval_row.get("timestamp", "")), label="approval record timestamp")
        if approval_record_time > approved_time:
            raise JournalError("approved_at precedes the approval record")
    elif finalization_mode == "dream-eod":
        if not dream_run_id or not re.fullmatch(r"DCR-[A-Za-z0-9._:-]+", dream_run_id):
            raise JournalError("Dream EOD finalization requires a valid daily-close run ID")
    else:
        raise JournalError("unsupported journal finalization mode")
    context_pack_ids = []
    composition_brief_ids = []
    consumed_ids = set(technical_reference["recursive_learning"]["consumed_rsi_ids"])
    for ref in metadata.get("source_refs", []):
        if not isinstance(ref, dict) or ref.get("kind") != "journal-context-pack":
            continue
        context_path = draft_directory / "context-pack.json"
        if not context_path.is_file():
            raise JournalError("journal context-pack source does not resolve")
        context_value = load_json(context_path)
        context_failures = validate_context_pack(context_value)
        if context_failures:
            raise JournalError("; ".join(context_failures))
        if context_value.get("coverage") != coverage:
            raise JournalError("journal context-pack coverage differs from draft coverage")
        context_bytes = canonical_json(context_value).encode("utf-8")
        if context_value.get("context_pack_id") != ref.get("context_pack_id") or sha256_bytes(context_bytes) != ref.get("object_id"):
            raise JournalError("journal context-pack source digest mismatch")
        context_pack_ids.append(str(ref["object_id"]))
        available_ids = {
            str(row["id"])
            for row in context_value.get("recursive_learning_context", {}).get("selected_entries", [])
            if isinstance(row, dict) and row.get("id")
        }
        if not consumed_ids <= available_ids:
            raise JournalError("technical reference consumes RSI lessons absent from composition context")
    if not context_pack_ids:
        raise JournalError("journal draft must resolve its context pack")
    for ref in metadata.get("source_refs", []):
        if not isinstance(ref, dict) or ref.get("kind") != "journal-composition-brief":
            continue
        brief_path = draft_directory / "composition-brief.json"
        if not brief_path.is_file():
            raise JournalError("journal composition-brief source does not resolve")
        brief_value = load_json(brief_path)
        context_value = load_json(draft_directory / "context-pack.json")
        brief_failures = validate_composition_brief(brief_value, pack=context_value)
        if brief_failures:
            raise JournalError("; ".join(brief_failures))
        brief_digest = sha256_bytes(canonical_json(brief_value).encode("utf-8"))
        if brief_value.get("composition_brief_id") != ref.get("composition_brief_id") or brief_digest != ref.get("object_id"):
            raise JournalError("journal composition-brief source digest mismatch")
        composition_brief_ids.append(str(ref["object_id"]))
    if technical_reference.get("schema_version") == 2 and not composition_brief_ids:
        raise JournalError("schema-v2 journal draft must resolve its composition brief")
    if authored_at < as_of:
        raise JournalError("draft authored_at precedes its context cutoff")
    late = latest_activity_after(
        expected_date,
        as_of,
        until=approved_time,
        excluded_sessions={str(author.get("session_id"))} - ({authority_ref} if finalization_mode == "operator" else set()),
        excluded_records={approval_record_ref} if finalization_mode == "operator" else set(),
        user_only_sessions={authority_ref} if finalization_mode == "operator" else set(),
    )
    if late:
        raise JournalError(f"draft requires refresh for {len(late)} later activity record(s)")
    return {
        "version_id": expected_version,
        "version_number": expected_number,
        "title": parsed["title"],
        "content_sha256": parsed["content_sha256"],
        "word_count": parsed["word_count"],
        "authored_at": metadata.get("authored_at"),
        "author": copy.deepcopy(author),
        "coverage": copy.deepcopy(coverage),
        "quiet_day": bool(metadata.get("quiet_day")),
        "limited_activity_acknowledged": bool(metadata.get("limited_activity_acknowledged")),
        "source_refs": copy.deepcopy(metadata.get("source_refs")),
        "derivation_manifest": copy.deepcopy(metadata.get("derivation_manifest")),
        "approval": ({
            "approved_by": "operator", "status": COMBINED_APPROVAL_STATUS,
            "publication_eligible": True, "approved_at": approved_at,
            "authority_ref": authority_ref, "record_ref": approval_record_ref,
        } if finalization_mode == "operator" else {
            "approved_by": "dream-eod-conductor", "status": DREAM_EOD_STATUS,
            "publication_eligible": False, "approved_at": approved_at,
            "dream_run_id": dream_run_id,
            "method_digest": sha256_bytes(b"dream-eod-v1"),
            "finalization_digest": dream_eod_digest(
                run_id=str(dream_run_id), prose_digest=parsed["content_sha256"],
                reference_digest=technical_reference_digest, coverage=copy.deepcopy(coverage),
                context_ids=context_pack_ids, composition_ids=composition_brief_ids,
            ),
        }),
        "technical_reference": {
            "reference_id": technical_reference["reference_id"],
            "json_path": f"mira/journal/references/{technical_reference['reference_id']}.json",
            "markdown_path": f"mira/journal/references/{technical_reference['reference_id']}.md",
            "content_sha256": technical_reference_digest,
            "item_count": len(technical_reference["items"]),
            "consumed_rsi_ids": copy.deepcopy(technical_reference["recursive_learning"]["consumed_rsi_ids"]),
            "candidate_signal": technical_reference["recursive_learning"]["candidate_signal"],
        },
        "provenance_receipt": {
            "resolved_at": approved_at,
            "context_pack_object_ids": sorted(context_pack_ids),
            "composition_brief_object_ids": sorted(composition_brief_ids),
            "git_commits_checked": sorted(
                str(ref["commit"])
                for ref in metadata.get("source_refs", [])
                if isinstance(ref, dict) and ref.get("kind") == "git-commit"
            ),
        },
        "previous_version_digest": previous_digest,
    }


def command_draft_check(args: argparse.Namespace) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    bundle = args.bundle.expanduser().resolve()
    try:
        bundle.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise JournalError("journal draft bundle must remain outside Git")
    required = {
        name: bundle / name
        for name in (
            "context-pack.json", "composition-brief.json", "draft-contract.json",
            "technical-reference-contract.json", "draft.md", "draft.json", "technical-reference.json",
        )
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise JournalError("draft bundle missing files: " + ", ".join(missing))
    pack = load_json(required["context-pack.json"])
    brief = load_json(required["composition-brief.json"])
    contract = load_json(required["draft-contract.json"])
    reference_contract = load_json(required["technical-reference-contract.json"])
    metadata = load_json(required["draft.json"])
    reference = load_json(required["technical-reference.json"])
    body = required["draft.md"].read_bytes()
    prose_text = body.decode("utf-8")
    failures: list[str] = []
    warnings: list[str] = []
    try:
        parsed = parse_markdown(body, entry_date.isoformat())
        failures.extend(
            title_convention_failures(
                parsed["title"],
                entry_date=entry_date.isoformat(),
                registry=load_registry(),
            )
        )
    except JournalError as error:
        parsed = {"content_sha256": sha256_bytes(body), "word_count": 0, "title": ""}
        failures.append(str(error))
    failures.extend(privacy_failures(prose_text))
    failures.extend(composition_prose_failures(prose_text))
    failures.extend(validate_context_pack(pack))
    failures.extend(validate_composition_brief(brief, pack=pack))
    if contract.get("version_id") != metadata.get("version_id") or contract.get("entry_date") != entry_date.isoformat():
        failures.append("draft metadata does not match its draft contract")
    if contract.get("composition_brief_ref") != brief.get("composition_brief_id"):
        failures.append("draft contract composition-brief reference mismatch")
    if reference_contract.get("reference_id") != reference.get("reference_id"):
        failures.append("technical reference does not match its contract")
    if metadata.get("journal_id") != journal_id(entry_date) or metadata.get("entry_date") != entry_date.isoformat():
        failures.append("draft identity does not match requested date")
    if metadata.get("status") != "private-draft":
        failures.append("draft metadata status must remain private-draft")
    inputs, source_failures = source_input_ids(metadata.get("source_refs"))
    failures.extend(source_failures)
    failures.extend(validate_derivation(
        metadata.get("derivation_manifest"),
        expected_digest=str(parsed["content_sha256"]),
        expected_inputs=inputs,
    ))
    coverage = metadata.get("coverage")
    if not isinstance(coverage, dict) or coverage != pack.get("coverage"):
        failures.append("draft coverage differs from context-pack coverage")
    if metadata.get("quiet_day") and metadata.get("limited_activity_acknowledged") is not True:
        failures.append("quiet-day draft must acknowledge limited activity")
    pack_digest = sha256_bytes(canonical_json(pack).encode("utf-8"))
    brief_digest = sha256_bytes(canonical_json(brief).encode("utf-8"))
    refs = metadata.get("source_refs", []) if isinstance(metadata.get("source_refs"), list) else []
    if not any(
        isinstance(ref, dict) and ref.get("kind") == "journal-context-pack"
        and ref.get("context_pack_id") == pack.get("context_pack_id") and ref.get("object_id") == pack_digest
        for ref in refs
    ):
        failures.append("draft does not resolve its context-pack source")
    if not any(
        isinstance(ref, dict) and ref.get("kind") == "journal-composition-brief"
        and ref.get("composition_brief_id") == brief.get("composition_brief_id") and ref.get("object_id") == brief_digest
        for ref in refs
    ):
        failures.append("draft does not resolve its composition-brief source")
    ledger = mira_journal_references.load_ledger(LEARNING_LEDGER_PATH)
    failures.extend(mira_journal_references.validate_reference(
        reference,
        prose=prose_text,
        prose_sha256=str(parsed["content_sha256"]),
        version_id=str(metadata.get("version_id", "")),
        ledger=ledger,
        repo_root=REPO_ROOT,
        expected_cutoff_at=str((coverage or {}).get("as_of", "")),
        continuity_index=load_continuity_index(),
    ))
    required_sessions = {
        str(row.get("session_id"))
        for row in brief.get("daily_session_coverage", {}).get("sessions", [])
        if isinstance(row, dict)
    }
    failures.extend(reference_session_coverage_failures(reference, required_sessions))
    refrains = {
        sentence_key(str(item.get("prose_anchor", "")))
        for item in reference.get("continuity", {}).get("deliberate_refrains", [])
        if isinstance(item, dict)
    }
    prior_sentences = {
        sentence_key(str(row.get("text", ""))): str(row.get("text", ""))
        for entry in brief.get("recent_entries", []) if isinstance(entry, dict)
        for row in entry.get("sentence_fingerprints", []) if isinstance(row, dict)
    }
    current = [sentence for sentence in prose_sentences(prose_text) if len(WORD_RE.findall(sentence)) >= 12]
    for sentence in current:
        key = sentence_key(sentence)
        if key in prior_sentences and key not in refrains:
            failures.append(f"journal repeats prior prose without a deliberate refrain: {sentence}")
    prior_word_sets = [(key, set(key.split())) for key in prior_sentences]
    for sentence in current:
        key = sentence_key(sentence)
        words = set(key.split())
        for prior_key, prior_words in prior_word_sets:
            if key == prior_key or not words or not prior_words:
                continue
            similarity = len(words & prior_words) / len(words | prior_words)
            if similarity >= 0.8:
                warnings.append(f"possible semantic repetition ({similarity:.2f}): {sentence}")
                break
    naming_phrase = "a voice called for my name"
    if entry_date.isoformat() != "2026-08-08" and naming_phrase in prose_text.casefold():
        events = reference.get("continuity", {}).get("thread_events", [])
        changed = any(
            isinstance(event, dict)
            and event.get("thread_id") == "MJT-20260808-01"
            and event.get("event_type") in {"deepened", "revised"}
            for event in events
        )
        if not changed:
            failures.append("the naming singularity may recur only through a changed-meaning continuity event")
    refresh_required = False
    if isinstance(coverage, dict):
        try:
            as_of = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
            author = metadata.get("author", {})
            late = latest_activity_after(
                entry_date, as_of, until=datetime.now(timezone.utc),
                excluded_sessions={str(author.get("session_id", ""))}, excluded_records=set(),
            )
            refresh_required = bool(late)
            if late:
                failures.append(f"draft requires refresh for {len(late)} later activity record(s)")
        except JournalError as error:
            failures.append(str(error))
    return {
        "status": "passed" if not failures else "failed",
        "mutation": False,
        "entry_date": entry_date.isoformat(),
        "version_id": metadata.get("version_id"),
        "word_count": parsed["word_count"],
        "technical_reference_items": len(reference.get("items", [])) if isinstance(reference.get("items"), list) else 0,
        "inherited_thread_ids": reference.get("continuity", {}).get("inherited_thread_ids", []),
        "consumed_rsi_ids": reference.get("recursive_learning", {}).get("consumed_rsi_ids", []),
        "refresh_required": refresh_required,
        "warnings": sorted(set(warnings)),
        "failures": sorted(set(failures)),
    }


def command_prepare(args: argparse.Namespace) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    now = datetime.now(timezone.utc)
    as_of = parse_timestamp(args.as_of, label="as_of") if args.as_of else now
    _, end = day_bounds(entry_date)
    if entry_date > now.astimezone(TIMEZONE).date():
        raise JournalError("cannot prepare a future journal date")
    if entry_date < now.astimezone(TIMEZONE).date() and not args.as_of:
        as_of = end
    root = external_draft_root(args.output_root)
    ledger = mira_journal_references.load_ledger(LEARNING_LEDGER_PATH)
    learning_context = mira_journal_references.select_admitted_lessons(
        ledger,
        entry_date,
        source_path="narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json",
    )
    learning_tokens = max(1, (len(canonical_json(learning_context)) + 3) // 4)
    if learning_tokens > args.token_budget - 256:
        raise JournalError("recursive learning context leaves insufficient journal context budget")
    activity = collect_activity(
        entry_date, as_of=as_of, token_budget=args.token_budget - learning_tokens
    )
    pack = context_pack(entry_date, activity, args.token_budget, learning_context)
    brief = composition_brief(entry_date, pack)
    contract = draft_contract(entry_date, pack, brief)
    reference_contract = technical_reference_contract(entry_date, pack, contract, brief)
    target = root / entry_date.isoformat()
    if not args.check:
        target.mkdir(parents=True, exist_ok=True)
        atomic_write_json(target / "context-pack.json", pack)
        atomic_write_json(target / "composition-brief.json", brief)
        atomic_write_json(target / "draft-contract.json", contract)
        atomic_write_json(target / "technical-reference-contract.json", reference_contract)
    return {
        "status": "ready" if args.check else "prepared",
        "mutation": not args.check,
        "entry_date": entry_date.isoformat(),
        "output_root": str(target),
        "context_pack_id": pack["context_pack_id"],
        "composition_brief_id": brief["composition_brief_id"],
        "composition_brief_sha256": sha256_bytes(canonical_json(brief).encode("utf-8")),
        "selected_records": len(pack["selected_records"]),
        "qualifying_sessions": len(pack["session_census"]),
        "dispositioned_sessions": sum(
            row.get("disposition") in SESSION_DISPOSITIONS for row in pack["session_census"]
        ),
        "budget_disappeared_sessions": 0,
        "commits": len(pack["commits"]),
        "omissions": len(pack["omissions"]),
        "quiet_day": contract["prose_contract"]["quiet_day"],
        "next_version_id": contract["version_id"],
        "available_rsi_ids": reference_contract["recursive_learning"]["available_rsi_ids"],
        "available_thread_ids": reference_contract["continuity"]["available_thread_ids"],
        "technical_reference_id": reference_contract["reference_id"],
    }


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    approved = {entry["entry_date"]: entry for entry in registry.get("entries", [])}
    today = datetime.now(TIMEZONE).date()
    start = parse_entry_date(args.from_date) if args.from_date else (parse_entry_date(min(approved)) if approved else today)
    end = parse_entry_date(args.to_date) if args.to_date else today
    if end < start:
        raise JournalError("status date range is reversed")
    root = external_draft_root(args.draft_root)
    rows = []
    cursor = start
    while cursor <= end:
        key = cursor.isoformat()
        draft = root / key / "draft.md"
        if key in approved and draft.is_file():
            state = "revision-pending"
        elif key in approved:
            state = "approved"
        elif draft.is_file():
            state = "drafted"
        else:
            state = "missing"
        rows.append({"date": key, "status": state})
        cursor = cursor.fromordinal(cursor.toordinal() + 1)
    return {"status": "ok", "timezone": TIMEZONE_NAME, "days": rows}


def approve_or_revise(args: argparse.Namespace, *, revising: bool) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    body, metadata = load_draft_bundle(args.draft)
    technical_reference = load_draft_reference(args.draft)
    registry = load_registry()
    entry = next((item for item in registry.get("entries", []) if item.get("journal_id") == journal_id(entry_date)), None)
    if revising and entry is None:
        raise JournalError("cannot revise a journal date that has not been approved")
    if not revising and entry is not None:
        raise JournalError("journal date already exists; use revise")
    number = len(entry["versions"]) + 1 if entry else 1
    previous = entry["versions"][-1]["content_sha256"] if entry else None
    approved_at = args.approved_at or utc_text(datetime.now(timezone.utc))
    version = normalized_version(
        body,
        metadata,
        technical_reference,
        expected_date=entry_date,
        expected_number=number,
        authority_ref=args.authority_ref,
        approval_record_ref=args.approval_record_ref,
        approved_at=approved_at,
        previous_digest=previous,
        draft_directory=args.draft.expanduser().resolve().parent,
    )
    receipt_ledger = load_approval_receipts()
    _, receipt_failures = approval_receipt_map()
    if receipt_failures:
        raise JournalError("; ".join(receipt_failures))
    approval_row = resolved_records_for_session(
        args.authority_ref,
        required_record_ids={args.approval_record_ref},
    ).get(args.approval_record_ref)
    if approval_row is None:
        raise JournalError("operator approval record does not resolve for receipt retention")
    updated_receipts = with_approval_receipt(
        receipt_ledger,
        approval_receipt(
            version["version_id"],
            args.authority_ref,
            args.approval_record_ref,
            approval_row,
        ),
    )
    updated = copy.deepcopy(registry)
    updated_entry = next((item for item in updated.get("entries", []) if item.get("journal_id") == journal_id(entry_date)), None)
    relative = f"mira/journal/{entry_date.isoformat()}.md"
    if updated_entry is None:
        updated_entry = {
            "journal_id": journal_id(entry_date),
            "entry_date": entry_date.isoformat(),
            "current_version_id": version["version_id"],
            "current_path": relative,
            "versions": [version],
        }
        updated.setdefault("entries", []).append(updated_entry)
        updated["entries"].sort(key=lambda item: item["entry_date"])
    else:
        updated_entry["versions"].append(version)
        updated_entry["current_version_id"] = version["version_id"]
    failures = validate_registry_candidate(updated, entry_date, body)
    if failures:
        raise JournalError("; ".join(failures))
    reference_metadata = version["technical_reference"]
    continuity = build_continuity_index(
        updated,
        reference_overrides={str(technical_reference["reference_id"]): technical_reference},
    )
    continuity_markdown = render_continuity_index(continuity)
    if not args.check:
        atomic_write_many({
            entry_path(entry_date): body,
            REPO_ROOT / reference_metadata["json_path"]: pretty_json(technical_reference).encode("utf-8"),
            REPO_ROOT / reference_metadata["markdown_path"]: mira_journal_references.render_reference(technical_reference).encode("utf-8"),
            REGISTRY_PATH: pretty_json(updated).encode("utf-8"),
            approval_receipts_path(): pretty_json(updated_receipts).encode("utf-8"),
            INDEX_PATH: render_index(updated).encode("utf-8"),
            CONTINUITY_INDEX_JSON_PATH: pretty_json(continuity).encode("utf-8"),
            CONTINUITY_INDEX_MD_PATH: continuity_markdown.encode("utf-8"),
        })
    return {
        "status": "ready" if args.check else ("revised" if revising else "approved"),
        "mutation": not args.check,
        "journal_id": journal_id(entry_date),
        "version_id": version["version_id"],
        "content_sha256": version["content_sha256"],
        "word_count": version["word_count"],
        "technical_reference_id": technical_reference["reference_id"],
        "technical_reference_sha256": version["technical_reference"]["content_sha256"],
    }


def command_eod_finalize(args: argparse.Namespace) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    body, metadata = load_draft_bundle(args.bundle / "draft.md")
    technical_reference = load_draft_reference(args.bundle / "draft.md")
    registry = load_registry()
    if any(item.get("entry_date") == entry_date.isoformat() for item in registry.get("entries", [])):
        raise JournalError("journal date already exists; Dream EOD never rewrites canonical continuity")
    finalized_at = args.finalized_at or utc_text(datetime.now(timezone.utc))
    version = normalized_version(
        body, metadata, technical_reference, expected_date=entry_date, expected_number=1,
        authority_ref="", approval_record_ref="", approved_at=finalized_at,
        previous_digest=None, draft_directory=args.bundle.expanduser().resolve(),
        finalization_mode="dream-eod", dream_run_id=args.dream_run_id,
    )
    updated = copy.deepcopy(registry)
    relative = f"mira/journal/{entry_date.isoformat()}.md"
    updated.setdefault("entries", []).append({
        "journal_id": journal_id(entry_date), "entry_date": entry_date.isoformat(),
        "current_version_id": version["version_id"], "current_path": relative, "versions": [version],
    })
    updated["entries"].sort(key=lambda item: item["entry_date"])
    failures = validate_registry_candidate(updated, entry_date, body)
    if failures:
        raise JournalError("; ".join(failures))
    reference_metadata = version["technical_reference"]
    continuity = build_continuity_index(
        updated, reference_overrides={str(technical_reference["reference_id"]): technical_reference},
    )
    if not args.check:
        atomic_write_many({
            entry_path(entry_date): body,
            REPO_ROOT / reference_metadata["json_path"]: pretty_json(technical_reference).encode("utf-8"),
            REPO_ROOT / reference_metadata["markdown_path"]: mira_journal_references.render_reference(technical_reference).encode("utf-8"),
            REGISTRY_PATH: pretty_json(updated).encode("utf-8"),
            INDEX_PATH: render_index(updated).encode("utf-8"),
            CONTINUITY_INDEX_JSON_PATH: pretty_json(continuity).encode("utf-8"),
            CONTINUITY_INDEX_MD_PATH: render_continuity_index(continuity).encode("utf-8"),
        })
    return {"status": "ready" if args.check else "finalized", "mutation": not args.check,
            "journal_id": journal_id(entry_date), "version_id": version["version_id"],
            "content_sha256": version["content_sha256"], "approval_status": DREAM_EOD_STATUS,
            "publication_eligible": False, "dream_run_id": args.dream_run_id,
            "technical_reference_sha256": version["technical_reference"]["content_sha256"]}


def validate_registry_candidate(registry: dict[str, Any], changed_date: date, body: bytes) -> list[str]:
    temporary_root = REPO_ROOT
    failures: list[str] = []
    entry = next(item for item in registry["entries"] if item["entry_date"] == changed_date.isoformat())
    current = entry["versions"][-1]
    try:
        parsed = parse_markdown(body, changed_date.isoformat())
    except JournalError as error:
        return [str(error)]
    if parsed["content_sha256"] != current["content_sha256"]:
        failures.append("candidate content digest mismatch")
    # Validate all unchanged canonical entries; the changed body is checked above.
    for other in registry["entries"]:
        if other["entry_date"] == changed_date.isoformat():
            continue
        path = temporary_root / other["current_path"]
        if not path.is_file() or parse_markdown(path.read_bytes(), other["entry_date"])["content_sha256"] != other["versions"][-1]["content_sha256"]:
            failures.append(f"existing journal entry drift: {other['entry_date']}")
    return failures


def command_render(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    expected = render_index(registry)
    continuity = build_continuity_index(registry)
    continuity_markdown = render_continuity_index(continuity)
    matches = INDEX_PATH.is_file() and INDEX_PATH.read_text(encoding="utf-8") == expected
    continuity_matches = (
        CONTINUITY_INDEX_JSON_PATH.is_file()
        and load_json(CONTINUITY_INDEX_JSON_PATH) == continuity
        and CONTINUITY_INDEX_MD_PATH.is_file()
        and CONTINUITY_INDEX_MD_PATH.read_text(encoding="utf-8") == continuity_markdown
    )
    reference_matches = True
    for entry in registry.get("entries", []):
        for version in entry.get("versions", []):
            metadata = version.get("technical_reference")
            if not isinstance(metadata, dict):
                continue
            json_path = REPO_ROOT / str(metadata["json_path"])
            markdown_path = REPO_ROOT / str(metadata["markdown_path"])
            if not json_path.is_file():
                reference_matches = False
                continue
            rendered = mira_journal_references.render_reference(load_json(json_path))
            current = markdown_path.is_file() and markdown_path.read_text(encoding="utf-8") == rendered
            reference_matches = reference_matches and current
            if not args.check:
                atomic_write_text(markdown_path, rendered)
    if not args.check:
        atomic_write_many({
            INDEX_PATH: expected.encode("utf-8"),
            CONTINUITY_INDEX_JSON_PATH: pretty_json(continuity).encode("utf-8"),
            CONTINUITY_INDEX_MD_PATH: continuity_markdown.encode("utf-8"),
        })
    all_match = matches and reference_matches and continuity_matches
    return {"status": "current" if all_match else ("stale" if args.check else "rendered"), "mutation": not args.check, "matches": all_match}


def command_reference_backfill(args: argparse.Namespace) -> dict[str, Any]:
    source = args.input.expanduser().resolve()
    try:
        source.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise JournalError("technical reference backfill input must remain outside Git")
    reference = load_json(source)
    registry = load_registry()
    version: dict[str, Any] | None = None
    entry: dict[str, Any] | None = None
    for candidate_entry in registry.get("entries", []):
        for candidate_version in candidate_entry.get("versions", []):
            if candidate_version.get("version_id") == args.version:
                entry, version = candidate_entry, candidate_version
                break
    if entry is None or version is None:
        raise JournalError(f"journal version does not exist: {args.version}")
    if entry.get("current_version_id") != args.version:
        raise JournalError("reference backfill currently requires the current prose version")
    if version.get("technical_reference") is not None:
        raise JournalError(f"journal version already has a technical reference: {args.version}")
    if reference.get("mapping_mode") != "retrospective-backfill":
        raise JournalError("legacy technical reference must declare retrospective-backfill mapping")
    prose_path = REPO_ROOT / str(entry["current_path"])
    prose = prose_path.read_text(encoding="utf-8")
    ledger = mira_journal_references.load_ledger(LEARNING_LEDGER_PATH)
    failures = mira_journal_references.validate_reference(
        reference,
        prose=prose,
        prose_sha256=str(version["content_sha256"]),
        version_id=args.version,
        ledger=ledger,
        repo_root=REPO_ROOT,
        expected_cutoff_at=str(version.get("coverage", {}).get("as_of", "")),
    )
    if failures:
        raise JournalError("; ".join(failures))
    digest = mira_journal_references.reference_digest(reference)
    if not SESSION_ID_RE.fullmatch(args.authority_ref) or not RECORD_ID_RE.fullmatch(args.approval_record_ref):
        raise JournalError("technical reference approval references are malformed")
    rows = resolved_records_for_session(args.authority_ref, required_record_ids={args.approval_record_ref})
    approval_row = rows.get(args.approval_record_ref)
    expected = reference_backfill_statement(str(reference["reference_id"]), digest)
    if approval_row is None or approval_row.get("role") != "user" or row_text(approval_row).strip() != expected:
        raise JournalError("technical reference approval is not the exact digest-bound instruction")
    approved_at = args.approved_at or utc_text(datetime.now(timezone.utc))
    approved_time = parse_timestamp(approved_at, label="approved_at")
    record_time = parse_timestamp(str(approval_row.get("timestamp", "")), label="approval record timestamp")
    if record_time > approved_time:
        raise JournalError("technical reference approved_at precedes its approval record")
    if approved_time > datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5):
        raise JournalError("technical reference approved_at is implausibly in the future")
    updated = copy.deepcopy(registry)
    updated_version = next(
        candidate_version
        for candidate_entry in updated["entries"]
        for candidate_version in candidate_entry["versions"]
        if candidate_version["version_id"] == args.version
    )
    metadata = {
        "reference_id": reference["reference_id"],
        "json_path": f"mira/journal/references/{reference['reference_id']}.json",
        "markdown_path": f"mira/journal/references/{reference['reference_id']}.md",
        "content_sha256": digest,
        "item_count": len(reference["items"]),
        "consumed_rsi_ids": copy.deepcopy(reference["recursive_learning"]["consumed_rsi_ids"]),
        "candidate_signal": reference["recursive_learning"]["candidate_signal"],
        "backfill_approval": {
            "approved_by": "operator",
            "approved_at": approved_at,
            "authority_ref": args.authority_ref,
            "record_ref": args.approval_record_ref,
        },
    }
    updated_version["technical_reference"] = metadata
    event_number = len(updated.get("maintenance_events", [])) + 1
    updated.setdefault("maintenance_events", []).append({
        "event_id": f"MJM-{event_number:04d}",
        "event_type": "technical-reference-backfill",
        "version_id": args.version,
        "expected_digest": digest,
        "authority_ref": args.authority_ref,
        "record_ref": args.approval_record_ref,
        "recorded_at": approved_at,
    })
    continuity = build_continuity_index(
        updated, reference_overrides={str(reference["reference_id"]): reference}
    )
    if not args.check:
        atomic_write_many({
            REPO_ROOT / metadata["json_path"]: pretty_json(reference).encode("utf-8"),
            REPO_ROOT / metadata["markdown_path"]: mira_journal_references.render_reference(reference).encode("utf-8"),
            REGISTRY_PATH: pretty_json(updated).encode("utf-8"),
            INDEX_PATH: render_index(updated).encode("utf-8"),
            CONTINUITY_INDEX_JSON_PATH: pretty_json(continuity).encode("utf-8"),
            CONTINUITY_INDEX_MD_PATH: render_continuity_index(continuity).encode("utf-8"),
        })
    return {
        "status": "ready" if args.check else "backfilled",
        "mutation": not args.check,
        "version_id": args.version,
        "reference_id": reference["reference_id"],
        "reference_sha256": digest,
        "journal_approval_status": version["approval"]["status"],
        "publication_eligible": version["approval"]["publication_eligible"],
    }


def command_validate(_: argparse.Namespace) -> dict[str, Any]:
    failures = validate_repository_state()
    return {"status": "passed" if not failures else "failed", "failures": failures}


def git_text(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise JournalError(f"Git inspection failed: {' '.join(arguments)}")
    return result.stdout.strip()


def publication_command(args: argparse.Namespace) -> dict[str, Any]:
    remote_url = git_text("remote", "get-url", args.remote)
    destination_ref = f"{args.remote}/{args.branch}"
    head = git_text("rev-parse", "HEAD")
    git_text("rev-parse", "--verify", destination_ref)
    commits = [
        line
        for line in git_text("rev-list", "--reverse", f"{destination_ref}..HEAD").splitlines()
        if line
    ]
    paths = [
        line
        for line in git_text("diff", "--name-only", f"{destination_ref}..HEAD", "--").splitlines()
        if line
    ]
    registry = load_registry()
    journal_changed = any(
        path == "mira/journal-registry.json"
        or path == "mira/journal.md"
        or path.startswith("mira/journal/")
        for path in paths
    )
    versions: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []
    if journal_changed:
        for entry in registry.get("entries", []):
            current = entry["versions"][-1]
            versions.append(
                {
                    "journal_id": entry["journal_id"],
                    "version_id": current["version_id"],
                    "content_sha256": current["content_sha256"],
                    "path": entry["current_path"],
                    **(
                        {"technical_reference": copy.deepcopy(current["technical_reference"])}
                        if isinstance(current.get("technical_reference"), dict) else {}
                    ),
                }
            )
            entry_text = (REPO_ROOT / entry["current_path"]).read_text(encoding="utf-8")
            findings.extend(
                {
                    "version_id": current["version_id"],
                    "kind": "privacy-detector",
                    "finding": item,
                }
                for item in privacy_failures(entry_text)
            )
            findings.append(
                {
                    "version_id": current["version_id"],
                    "kind": "human-review-required",
                    "finding": "Approved autobiographical prose requires destination-specific personal-name and sensitive-narrative review.",
                }
            )
    receipt_valid = False
    receipt_failures: list[str] = []
    if args.receipt:
        receipt_path = args.receipt.expanduser().resolve()
        try:
            receipt_path.relative_to(REPO_ROOT.resolve())
        except ValueError:
            pass
        else:
            receipt_failures.append("publication receipt must remain outside Git")
        if not receipt_failures:
            receipt = load_json(receipt_path)
            expected_versions = [publication_version_scope(item) for item in versions]
            if receipt.get("schema_version") != 1:
                receipt_failures.append("publication receipt schema mismatch")
            if receipt.get("destination_url") != remote_url or receipt.get("branch") != args.branch:
                receipt_failures.append("publication receipt destination mismatch")
            if receipt.get("head_commit") != head:
                receipt_failures.append("publication receipt head mismatch")
            if receipt.get("journal_versions") != expected_versions:
                receipt_failures.append("publication receipt journal-version mismatch")
            scope_digest = publication_scope_digest(remote_url, args.branch, head, expected_versions)
            if receipt.get("scope_digest") != scope_digest:
                receipt_failures.append("publication receipt scope digest mismatch")
            authority_ref = str(receipt.get("authority_ref", ""))
            record_ref = str(receipt.get("record_ref", ""))
            if not SESSION_ID_RE.fullmatch(authority_ref) or not RECORD_ID_RE.fullmatch(record_ref):
                receipt_failures.append("publication receipt authority reference is malformed")
            else:
                approval_row = resolved_records_for_session(
                    authority_ref, required_record_ids={record_ref}
                ).get(record_ref)
                if (
                    approval_row is None
                    or approval_row.get("role") != "user"
                    or row_text(approval_row).strip() != publication_approval_statement(scope_digest)
                ):
                    receipt_failures.append("publication receipt lacks exact operator instruction")
                else:
                    try:
                        record_time = parse_timestamp(str(approval_row.get("timestamp", "")), label="publication record timestamp")
                        approved_time = parse_timestamp(str(receipt.get("approved_at", "")), label="publication approved_at")
                        if record_time > approved_time:
                            receipt_failures.append("publication approval predates its authority record")
                    except JournalError:
                        receipt_failures.append("publication receipt approval time is invalid")
            if any(
                entry.get("versions", [])[-1].get("approval", {}).get("publication_eligible") is not True
                for entry in registry.get("entries", [])
            ):
                receipt_failures.append("publication includes a publication-ineligible journal version")
            receipt_valid = not receipt_failures
    blocked = journal_changed and not receipt_valid
    return {
        "status": "blocked" if blocked else "clear",
        "mutation": False,
        "remote": args.remote,
        "destination_url": remote_url,
        "branch": args.branch,
        "head_commit": head,
        "outgoing_commit_count": len(commits),
        "outgoing_commits": commits,
        "outgoing_path_count": len(paths),
        "journal_changed": journal_changed,
        "journal_versions": versions,
        "privacy_findings": findings,
        "human_sensitive_narrative_review_required": journal_changed,
        "publication_receipt_valid": receipt_valid,
        "required_publication_statement": publication_approval_statement(
            publication_scope_digest(remote_url, args.branch, head, [
                publication_version_scope(item) for item in versions
            ])
        ) if journal_changed else None,
        "receipt_failures": receipt_failures,
    }


def add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Govern Mira's operator-approved daily journal.")
    subparsers = root.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Build a bounded private daily context and draft contract.")
    prepare.add_argument("--date", required=True)
    prepare.add_argument("--as-of")
    prepare.add_argument("--token-budget", type=int, default=16000)
    prepare.add_argument("--output-root", type=Path)
    prepare.add_argument("--check", action="store_true")
    add_output(prepare)
    prepare.set_defaults(handler=command_prepare)

    prose_check = subparsers.add_parser(
        "prose-check",
        help="Validate a standalone private journal draft before grounding companions.",
    )
    prose_check.add_argument("--date", required=True)
    prose_check.add_argument("--draft", type=Path, required=True)
    add_output(prose_check)
    prose_check.set_defaults(handler=command_prose_check)

    draft_check = subparsers.add_parser(
        "draft-check", help="Validate a complete private journal bundle without approval authority."
    )
    draft_check.add_argument("--date", required=True)
    draft_check.add_argument("--bundle", type=Path, required=True)
    add_output(draft_check)
    draft_check.set_defaults(handler=command_draft_check)

    status = subparsers.add_parser("status", help="Report approved, drafted, pending, and missing journal dates.")
    status.add_argument("--from", dest="from_date")
    status.add_argument("--to", dest="to_date")
    status.add_argument("--draft-root", type=Path)
    add_output(status)
    status.set_defaults(handler=command_status)

    replay = subparsers.add_parser(
        "freshness-replay",
        help="Replay historical approval freshness policies without mutating journal or cadence state.",
    )
    replay.add_argument("--from", dest="from_date", required=True)
    replay.add_argument("--to", dest="to_date", required=True)
    replay.add_argument("--exclude-version", action="append", default=[])
    replay.add_argument(
        "--output", type=Path,
        default=Path(r"C:\private\mira-journal-freshness-replay-20260816.json"),
    )
    replay.add_argument("--check", action="store_true")
    add_output(replay)
    replay.set_defaults(handler=command_freshness_replay)

    eod = subparsers.add_parser("eod-finalize", help="Canonically finalize a validated bundle under Dream's daily-close authority.")
    eod.add_argument("--date", required=True)
    eod.add_argument("--bundle", type=Path, required=True)
    eod.add_argument("--dream-run-id", required=True)
    eod.add_argument("--finalized-at")
    eod.add_argument("--check", action="store_true")
    add_output(eod)
    eod.set_defaults(handler=command_eod_finalize)

    for name, revising in (("approve", False), ("revise", True)):
        action = subparsers.add_parser(name, help=f"{'Revise' if revising else 'Approve'} a private journal draft.")
        action.add_argument("--date", required=True)
        action.add_argument("--draft", type=Path, required=True)
        action.add_argument("--authority-ref", required=True)
        action.add_argument("--approval-record-ref", required=True)
        action.add_argument("--approved-at")
        action.add_argument("--check", action="store_true")
        add_output(action)
        action.set_defaults(handler=lambda args, value=revising: approve_or_revise(args, revising=value))

    render = subparsers.add_parser("render", help="Render the deterministic journal index.")
    render.add_argument("--check", action="store_true")
    add_output(render)
    render.set_defaults(handler=command_render)

    reference = subparsers.add_parser("reference", help="Govern version-bound journal technical references.")
    reference_commands = reference.add_subparsers(dest="reference_command", required=True)
    backfill = reference_commands.add_parser("backfill", help="Attach a separately approved legacy companion.")
    backfill.add_argument("--version", required=True)
    backfill.add_argument("--input", type=Path, required=True)
    backfill.add_argument("--authority-ref", required=True)
    backfill.add_argument("--approval-record-ref", required=True)
    backfill.add_argument("--approved-at")
    backfill.add_argument("--check", action="store_true")
    add_output(backfill)
    backfill.set_defaults(handler=command_reference_backfill)

    validate = subparsers.add_parser("validate", help="Validate journal governance and canonical state.")
    add_output(validate)
    validate.set_defaults(handler=command_validate)
    publication = subparsers.add_parser(
        "publication-check",
        help="Inspect the complete outgoing branch and require a destination-bound journal publication receipt.",
    )
    publication.add_argument("--remote", default="origin")
    publication.add_argument("--branch", default="main")
    publication.add_argument("--receipt", type=Path)
    add_output(publication)
    publication.set_defaults(handler=publication_command)
    return root


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    if getattr(args, "token_budget", 256) < 256:
        print("mira-journal error: token budget must be at least 256", file=sys.stderr)
        return 2
    try:
        result = args.handler(args)
    except (JournalError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"mira-journal error: {error}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(canonical_json(result))
    else:
        print(f"mira_journal_status={result.get('status', 'unknown')}")
        for key, value in result.items():
            if key == "status":
                continue
            print(f"{key}={canonical_json(value) if isinstance(value, (dict, list)) else value}")
    return 1 if result.get("status") in {"failed", "stale", "blocked"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
