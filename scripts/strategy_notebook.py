"""Read-only, bounded strategic recall. Stored text is not verified knowledge."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import date, datetime
import os
import tempfile
import notebook_paths as locations
from pathlib import Path

from repository_paths import resolve_geopolitics_reference
import journal_calendar
from validate_daily_run import strategy_notebook_section

REPO_ROOT = Path(__file__).resolve().parents[1]
SETTLED = {"considered", "deferred", "excluded"}
LIMIT = 12000
STOP = {"the", "and", "what", "which", "with", "from", "this", "that", "does", "how", "can", "for", "into"}


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def tokens(text):
    return set(re.findall(r"[a-z0-9]{3,}", text.casefold())) - STOP


def section(text, *names):
    for name in names:
        match = re.search(r"(?m)^## " + re.escape(name) + r"\s*\n", text)
        if match:
            end = re.search(r"(?m)^## ", text[match.end():])
            return text[match.end():match.end() + end.start() if end else len(text)].strip()
    return ""


def domain(repo):
    return resolve_geopolitics_reference(repo, "geopolitics")


def create_json(path, value):
    """Publish complete bytes without replacing another session's entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".notebook-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def contribution_paths(repo):
    paths = list((locations.root(repo) / "contributions").glob("*.json"))
    old = domain(repo) / "work/strategy-notebook/contributions"
    paths += [p for p in old.glob("*.json") if locations.resolve(repo, p.relative_to(repo).as_posix()) == p.resolve()]
    return paths


def contributions(repo=REPO_ROOT):
    rows = []
    for path in sorted(contribution_paths(repo)):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("content_sha256") != digest({k: v for k, v in value.items() if k != "content_sha256"}):
            raise ValueError(f"Notebook contribution digest mismatch: {path}")
        rows.append({**value, "path": path.relative_to(repo).as_posix()})
    return sorted(rows, key=lambda row: (row["closed_at"], row["contribution_id"]))


def close(value, repo=REPO_ROOT, check=False, legacy=False):
    import cognitive_context
    if value.get("no_save"):
        return {"status": "not-saved", "reason": "Explicit no-save instruction"}
    if not legacy and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", value.get("inquiry_id", "")):
        raise ValueError("A named Notebook inquiry_id is required")
    clean = dict(value)
    identifier = clean.get("contribution_id", "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", identifier):
        raise ValueError("A stable safe contribution_id is required")
    path = locations.root(repo) / "contributions" / (identifier + ".json")
    request_digest = digest(value)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        expected = digest({k: v for k, v in existing.items() if k != "content_sha256"})
        if existing.get("content_sha256") != expected:
            raise ValueError("Existing contribution integrity failure")
        if existing.get("request_sha256") != request_digest:
            raise ValueError("Contribution identity already exists with different content; append a correction")
        return {"status": "reused", "path": path.relative_to(repo).as_posix(), "content_sha256": expected}
    date.fromisoformat(clean["date"])
    if clean.get("entry_mode") == "current-geopolitics" and "survey" not in clean:
        raise ValueError("Current geopolitics contribution requires a survey binding")
    if "survey" in clean:
        from geo_strategy_acquisition import validate_survey
        validate_survey(clean["survey"], clean["date"], repo)
    timestamp = datetime.fromisoformat(clean["closed_at"])
    if timestamp.tzinfo is None:
        raise ValueError("closed_at must include a timezone")
    start, end = journal_calendar.day_bounds(date.fromisoformat(clean["date"]))
    if not start <= timestamp < end:
        raise ValueError("closed_at must fall within the declared dated-calendar day")
    for field in ("session_id", "question", "return_point"):
        if not isinstance(clean.get(field), str) or not clean[field].strip():
            raise ValueError(f"{field} is required")
    clean.setdefault("disposition_only", False)
    if not clean["disposition_only"]:
        for field in ("assessment", "delta"):
            if not isinstance(clean.get(field), str) or not clean[field].strip():
                raise ValueError(f"{field} is required")
    for field in ("source_dispositions", "correction_links", "note_proposals"):
        clean.setdefault(field, [])
        if not isinstance(clean[field], list):
            raise ValueError(f"{field} must be a list")
    if clean["source_dispositions"]:
        from geo_strategy_acquisition import scan
        known_sources, known_queues, _ = scan(repo)
    else:
        known_sources, known_queues = {}, {}
    for row in clean["source_dispositions"]:
        if row.get("status") not in SETTLED | {"analysis-pending", "unknown"} or not row.get("identity") or not row.get("reason"):
            raise ValueError("Invalid source disposition")
        if not re.fullmatch(r"[0-9a-f]{64}", row.get("version", "")):
            raise ValueError("Source version must be a SHA-256")
        path = locations.resolve(repo, row["path"])
        if not path.is_file():
            raise ValueError("Disposition source is unavailable")
        source = known_sources.get(row["identity"])
        queued = known_queues.get(row["identity"])
        expected = source["version"] if source else digest({k: queued.get(k) for k in ("url", "transcript_status", "next_action")}) if queued else None
        expected_path = source["path"] if source else queued["queue_path"] if queued else None
        if expected != row["version"] or expected_path != row["path"]:
            raise ValueError("Disposition source identity or version changed")
        if not source and row["status"] == "considered":
            raise ValueError("Unlanded transcript cannot be marked analytically considered")
    for link in clean["correction_links"]:
        if not locations.resolve(repo, link).is_file():
            raise ValueError("Correction target unavailable")
    clean["note_proposals"] = cognitive_context.nominations(clean["note_proposals"], repo)
    if "composition_refs" in clean:
        import composition_links
        composition_links.validate_responses(repo, clean["composition_refs"], clean["correction_links"])
        if clean["disposition_only"] and any(row["effect"] == "changed" for row in clean["composition_refs"]):
            raise ValueError("Changed composition judgment requires a substantive assessment")
    if clean["disposition_only"] and not clean["source_dispositions"]:
        raise ValueError("Disposition-only close requires at least one source disposition")
    evidence = clean.setdefault("evidence_refs", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence_refs must be a list")
    for ref in evidence:
        if not isinstance(ref, dict) or ref.get("evidence_class") not in {"observation", "source-assertion", "interpretation", "proposal", "verification"}:
            raise ValueError("Invalid evidence class")
        target = locations.resolve(repo, ref.get("ref"))
        if not target.is_file() or digest(target.read_bytes()) != ref.get("sha256"):
            raise ValueError("Evidence reference missing or changed")
    clean["schema_version"] = 1 if legacy else 2
    clean["request_sha256"] = request_digest
    clean.pop("content_sha256", None)
    clean["content_sha256"] = digest(clean)
    path = locations.root(repo) / "contributions" / (identifier + ".json")
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != clean:
            raise ValueError("Contribution identity already exists with different content; append a correction")
        return {"status": "reused", "path": path.relative_to(repo).as_posix(), "content_sha256": clean["content_sha256"]}
    if not check:
        try:
            create_json(path, clean)
        except FileExistsError:
            return close(value, repo, legacy=legacy)
    return {"status": "validated" if check else "saved", "path": path.relative_to(repo).as_posix(), "content_sha256": clean["content_sha256"]}


def read_legacy_entry(day, repo=REPO_ROOT):
    date.fromisoformat(day)
    daily = locations.daily(repo, day)
    monthly = locations.monthly(repo, day[:7])
    choices = []
    for path in (daily, monthly):
        if path.is_file():
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig").replace("\r\n", "\n")
            if path == monthly:
                text = strategy_notebook_section(text, day)
            if text.strip():
                choices.append((path, raw, text))
    if not choices:
        return None
    path, raw, text = choices[0]
    status = re.search(r"(?m)^Status:\s*`?([^`\n]+)", text)
    required = ("Strategic Question", "Bottom Line", "Delta")
    aliases = {"Strategic Question": "Question of Order", "Bottom Line": "Central Judgment"}
    findings = ["missing section: " + name for name in required if not section(text, name, aliases.get(name, name))]
    return {"entry_date": day, "path": path.relative_to(repo).as_posix(),
            "locator": f"Date: `{day}`" if path == monthly else "whole-file",
            "file_sha256": digest(raw), "content_sha256": digest(text.encode()),
            "declared_status": status.group(1) if status else "unspecified",
            "validation_findings": findings, "text": text, "alternatives": [
                {"path": p.relative_to(repo).as_posix(), "content_sha256": digest(t.encode()), "differs": t != text}
                for p, _, t in choices[1:]]}


def contribution_text(row):
    return "\n\n".join([
        "## Strategic Question\n" + row["question"],
        "## Bottom Line\n" + row.get("assessment", "Disposition only"),
        "## Delta\n" + row.get("delta", "No estimate composed"),
        "## Inquiry Return Point\n" + row["return_point"],
        "## Source Dispositions\n" + json.dumps(row["source_dispositions"], ensure_ascii=False),
        "## Corrections\n" + json.dumps(row["correction_links"]),
        "## Note Proposals\n" + json.dumps(row["note_proposals"], ensure_ascii=False),
        *(["## Composition Responses\n" + json.dumps(row["composition_refs"], ensure_ascii=False)] if row.get("composition_refs") else []),
        *(["## YouTube Survey Coverage\n" + json.dumps(row["survey"], ensure_ascii=False)] if "survey" in row else []),
    ])


def read_entry(day, repo=REPO_ROOT):
    rows = [row for row in contributions(repo) if row["date"] == day and not row.get("disposition_only")]
    if rows:
        row = rows[-1]
        return {"entry_date": day, "path": row["path"], "locator": row["contribution_id"],
                "content_sha256": row["content_sha256"], "file_sha256": digest((repo / row["path"]).read_bytes()),
                "declared_status": "internal Mind Notebook contribution", "validation_findings": [],
                "text": contribution_text(row), "alternatives": []}
    return read_legacy_entry(day, repo)


def inventory(repo):
    days = {p.stem for p in (locations.root(repo) / "daily").glob("????-??-??.md")}
    for path in (locations.root(repo) / "monthly").glob("????-??.md"):
        days.update(re.findall(r"Date: `(\d{4}-\d{2}-\d{2})`", path.read_text(encoding="utf-8")))
    for path in (domain(repo) / "work/daily").glob("????-??-??/strategy-notebook.md"):
        days.add(path.parent.name)
    for path in (domain(repo) / "work/strategy-notebook").glob("????-??.md"):
        days.update(re.findall(r"Date: `(\d{4}-\d{2}-\d{2})`", path.read_text(encoding="utf-8")))
    return [row for day in sorted(days) if (row := read_legacy_entry(day, repo))]


def git(repo, *args):
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, timeout=15)
    return result.stdout if result.returncode == 0 else b""


def historical(row, day, repo):
    """Only committed historical bytes establish an available-by-cutoff version."""
    cutoff = journal_calendar.day_bounds(date.fromisoformat(day))[1].isoformat()
    paths = list(dict.fromkeys([locations.original(repo, row["path"]), row["path"]]))
    for path in list(paths):
        if path.startswith("geopolitics/"):
            paths.append("narrative-geopolitics/" + path.split("/", 1)[1])
    recovered = []
    for path in paths:
        commit = git(repo, "log", "-1", f"--before={cutoff}", "--format=%H", "--", path).decode().strip()
        if not commit:
            continue
        raw = git(repo, "show", f"{commit}:{path}")
        if not raw:
            continue
        text = raw.decode("utf-8-sig").replace("\r\n", "\n")
        if row["locator"] != "whole-file":
            text = strategy_notebook_section(text, row["entry_date"])
        if not text.strip():
            continue
        status = re.search(r"(?m)^Status:\s*`?([^`\n]+)", text)
        recovered.append({**row, "text": text, "file_sha256": digest(raw), "content_sha256": digest(text.encode()),
                "declared_status": status.group(1) if status else "unspecified", "historical_path": path,
                "version_ref": commit, "version_time": git(repo, "show", "-s", "--format=%cI", commit).decode().strip(),
                "temporal_status": "committed-by-cutoff"})
    return max(recovered, key=lambda r: r["version_time"]) if recovered else None


def revision_targets(row):
    """A link alone is a comparison, not a declaration of revision."""
    result = set()
    for paragraph in re.split(r"\n\s*\n", row["text"]):
        if re.search(r"\b(corrects?|revises?|supersedes?|retracts?|correction|revision of)\b", paragraph, re.I):
            for link in re.findall(r"\]\(([^)]+)\)", paragraph):
                result.update(re.findall(r"\d{4}-\d{2}-\d{2}", link))
    return result


def disposition(day, repo=REPO_ROOT, applicable=True):
    try:
        row = read_entry(day, repo)
        if row is None:
            return {"status": "unavailable" if applicable else "not-applicable", "reason": "No dated Notebook found.", "authority_effect": "none"}
        deferred = bool(re.search(r"analytical (?:judgment held|debt)|analysis (?:incomplete|deferred)|judgment held", row["declared_status"] + " " + row["text"][:1500], re.I))
        return {"status": "analysis-deferred" if deferred else "present", "path": row["path"],
                "digest": row["content_sha256"], "declared_status": row["declared_status"],
                "reason": "Presence is not analytical completeness or verification.", "authority_effect": "none"}
    except (OSError, ValueError) as error:
        return {"status": "unavailable", "reason": str(error), "authority_effect": "none"}


def context(day, focus="", repo=REPO_ROOT, limit=LIMIT, inquiry_id=None):
    date.fromisoformat(day)
    rows = inventory(repo)
    target = next((r for r in rows if r["entry_date"] == day), None)
    focus_entry = read_entry(day, repo) if not inquiry_id else None
    if not focus and focus_entry:
        focus = section(focus_entry["text"], "Strategic Question", "Question of Order")
    if not focus and target:
        focus = section(target["text"], "Strategic Question", "Question of Order")
    if not focus:
        judgment = domain(repo) / "work/daily" / day / "judgment.md"
        if judgment.is_file():
            focus = section(judgment.read_text(encoding="utf-8"), "Strategic Question", "Question of Order")
    words = tokens(focus)
    def score(row):
        return len(words & tokens(" ".join(section(row["text"], *names) for names in
                   [("Strategic Question", "Question of Order"), ("Bottom Line", "Central Judgment"), ("Delta",)])))
    earlier = sorted([r for r in rows if r["entry_date"] < day and words and score(r)],
                     key=lambda r: (-score(r), -date.fromisoformat(r["entry_date"]).toordinal(), r["path"]))
    selected = ([] if inquiry_id else ([target] if target and (not words or score(target)) else []) + earlier[:2])
    dates = {r["entry_date"] for r in selected}
    later = sorted([r for r in rows if r["entry_date"] > day and revision_targets(r) & dates],
                   key=lambda r: (-date.fromisoformat(r["entry_date"]).toordinal(), r["path"]))
    result = {"schema_version": 1, "entry_date": day, "focus": focus, "status": "available" if selected else "no-relevant-material",
              "historical_context": [], "later_context": [], "omitted": [], "gaps": [],
              "authority": "interpretive strategic context; not verified facts, identity, or action authority"}
    entries = contributions(repo)
    relevant = [row for row in entries if row["date"] <= day and
                (row.get("inquiry_id") == inquiry_id if inquiry_id else bool(words and words & tokens(row["question"])))]
    # Follow correction links to both legacy entries and session contributions.
    linked = {locations.identity(repo, row["path"]) for row in relevant + selected}
    while True:
        additions = [row for row in entries if row not in relevant and (linked.intersection(locations.identity(repo, p) for p in row["correction_links"]) or locations.identity(repo, row["path"]) in {locations.identity(repo, p) for current in relevant for p in current["correction_links"]})]
        if not additions:
            break
        relevant.extend(additions)
        linked.update(row["path"] for row in additions)
    reserved = min(max(0, limit), LIMIT, sum(len(contribution_text(row)) for row in relevant))
    remaining = max(0, min(limit, LIMIT) - reserved)
    def append(row, group):
        nonlocal remaining
        text = row["text"]
        # Entire entry preserves qualifications; never detach a fluent conclusion from its limits.
        handle = {k: v for k, v in row.items() if k != "text"}
        if len(text) > remaining:
            result["omitted"].append({**handle, "reason": "complete qualified entry exceeds remaining excerpt budget"})
            return
        remaining -= len(text)
        result[group].append({**handle, "excerpt": text})
    for row in selected:
        old = historical(row, day, repo)
        if old:
            append(old, "historical_context")
        else:
            result["gaps"].append({"path": row["path"], "status": "historical_version_unavailable"})
        if not old or old["content_sha256"] != row["content_sha256"]:
            append({**row, "temporal_status": "current-version; historical availability unestablished"}, "later_context")
    for row in later[:2]:
        append({**row, "temporal_status": "explicit-later-revision"}, "later_context")
    result["omitted"].extend({"path": r["path"], "entry_date": r["entry_date"], "reason": "selection budget"} for r in earlier[2:] + later[2:])
    result["gaps"].append({"status": "correction-coverage-not-exhaustive", "reason": "Only explicit revision links are followed."})
    remaining += reserved
    result["contributions"] = []
    for row in sorted(relevant, key=lambda item: (item["closed_at"], item["contribution_id"]), reverse=True):
        excerpt = contribution_text(row)
        if len(excerpt) > remaining:
            result["omitted"].append({"path": row["path"], "reason": "complete qualified contribution exceeds remaining excerpt budget"})
            continue
        remaining -= len(excerpt)
        result["contributions"].append({**row, "excerpt": excerpt,
            "temporal_status": "later-correction" if row["date"] > day else "recorded-contribution; not independently verified"})
    if result["contributions"]:
        result["status"] = "available"
    result["contributions"].sort(key=lambda item: (item["closed_at"], item["contribution_id"]))
    result["inquiry_id"] = inquiry_id
    result["inquiry_candidates"] = sorted({r["inquiry_id"] for r in relevant if r.get("inquiry_id")})
    result["ambiguous"] = not inquiry_id and len(result["inquiry_candidates"]) > 1
    result["content_sha256"] = digest(result)
    return result


def inquiry_context(day, focus="", repo=REPO_ROOT, inquiry_id=None):
    entries = [row for row in contributions(repo) if row["date"] <= day and not row.get("disposition_only")]
    legacy = inventory(repo)
    candidates = [(row["date"], row["closed_at"], row["question"]) for row in entries]
    candidates += [(row["entry_date"], "", section(row["text"], "Strategic Question", "Question of Order")) for row in legacy if row["entry_date"] <= day]
    inferred = not focus
    if not focus and candidates and not inquiry_id:
        focus = max(candidates)[2]
    result = context(day, focus, repo, inquiry_id=inquiry_id)
    result["focus_basis"] = "latest recorded inquiry; activity not inferred" if inferred else "explicit inquiry"
    import composition_links
    selected = list(dict.fromkeys(row["path"] for group in ("historical_context", "later_context", "contributions")
                                 for row in result.get(group, [])))
    result["compositions"] = []
    catalog = composition_links.inventory(repo) if selected else ([], [])
    for ref in selected[:5]:
        result["compositions"].append({"notebook_ref": ref, **composition_links.search(repo, notebook_ref=ref, limit=5, catalog=catalog)})
    if len(selected) > 5:
        result["omitted"].append({"kind": "composition lookups", "count": len(selected) - 5, "reason": "result budget"})
    result.pop("content_sha256", None)
    result["content_sha256"] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compositions = commands.add_parser("composition-search", help="Read-only explicit Mind/Study lineage")
    selection = compositions.add_mutually_exclusive_group(required=True)
    selection.add_argument("--notebook-ref")
    selection.add_argument("--artifact-ref")
    compositions.add_argument("--json", action="store_true")
    validation = commands.add_parser("composition-validate", help="Read-only composition metadata validation")
    validation.add_argument("--artifact-ref", required=True)
    validation.add_argument("--json", action="store_true")
    query = commands.add_parser("context")
    query.add_argument("--date", required=True)
    query.add_argument("--focus", default="")
    query.add_argument("--inquiry-id")
    query.add_argument("--json", action="store_true")
    notes = commands.add_parser("note-search", help="Read-only duplicate orientation; inspect full targets before nomination.")
    notes.add_argument("--focus", required=True)
    notes.add_argument("--work-id", action="append", default=[])
    notes.add_argument("--json", action="store_true")
    check = commands.add_parser("check-nominations", help="Validate candidate-only judgments without saving notes.")
    check.add_argument("--input", required=True, type=Path)
    check.add_argument("--json", action="store_true")
    close_parser = commands.add_parser("close")
    close_parser.add_argument("--input", required=True, type=Path)
    close_parser.add_argument("--check", action="store_true")
    close_parser.add_argument("--json", action="store_true")
    view = commands.add_parser("render", help="Read-only Markdown with relocated links")
    view.add_argument("--ref", required=True)
    args = parser.parse_args()
    if args.command == "render":
        print(locations.readable(REPO_ROOT, args.ref))
        return
    if args.command == "close":
        result = close(json.loads(args.input.read_text(encoding="utf-8")), check=args.check)
    elif args.command in {"composition-search", "composition-validate"}:
        import composition_links
        if args.command == "composition-validate":
            result = composition_links.inspect(REPO_ROOT, args.artifact_ref)
        else:
            result = composition_links.search(REPO_ROOT, args.notebook_ref, args.artifact_ref)
    elif args.command == "context":
        result = inquiry_context(args.date, args.focus, inquiry_id=args.inquiry_id)
    else:
        import cognitive_context
        result = cognitive_context.note_search(args.focus, REPO_ROOT, work_ids=args.work_id) if args.command == "note-search" else cognitive_context.nominations(json.loads(args.input.read_text(encoding="utf-8")), REPO_ROOT)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
