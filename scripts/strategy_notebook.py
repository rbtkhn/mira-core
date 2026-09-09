"""Read-only, bounded strategic recall. Stored text is not verified knowledge."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from repository_paths import resolve_geopolitics_reference
import journal_calendar
from validate_daily_run import strategy_notebook_section

REPO_ROOT = Path(__file__).resolve().parents[1]
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


def read_entry(day, repo=REPO_ROOT):
    date.fromisoformat(day)
    daily = domain(repo) / "work/daily" / day / "strategy-notebook.md"
    monthly = domain(repo) / "work/strategy-notebook" / f"{day[:7]}.md"
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


def inventory(repo):
    days = set()
    for path in (domain(repo) / "work/daily").glob("????-??-??/strategy-notebook.md"):
        days.add(path.parent.name)
    for path in (domain(repo) / "work/strategy-notebook").glob("????-??.md"):
        days.update(re.findall(r"Date: `(\d{4}-\d{2}-\d{2})`", path.read_text(encoding="utf-8")))
    return [row for day in sorted(days) if (row := read_entry(day, repo))]


def git(repo, *args):
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, timeout=15)
    return result.stdout if result.returncode == 0 else b""


def historical(row, day, repo):
    """Only committed historical bytes establish an available-by-cutoff version."""
    cutoff = journal_calendar.day_bounds(date.fromisoformat(day))[1].isoformat()
    paths = [row["path"]]
    if row["path"].startswith("geopolitics/"):
        paths.append("narrative-geopolitics/" + row["path"].split("/", 1)[1])
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


def context(day, focus="", repo=REPO_ROOT, limit=LIMIT):
    date.fromisoformat(day)
    rows = inventory(repo)
    target = next((r for r in rows if r["entry_date"] == day), None)
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
    selected = ([target] if target else []) + earlier[:2]
    dates = {r["entry_date"] for r in selected}
    later = sorted([r for r in rows if r["entry_date"] > day and revision_targets(r) & dates],
                   key=lambda r: (-date.fromisoformat(r["entry_date"]).toordinal(), r["path"]))
    result = {"schema_version": 1, "entry_date": day, "focus": focus, "status": "available" if selected else "no-relevant-material",
              "historical_context": [], "later_context": [], "omitted": [], "gaps": [],
              "authority": "interpretive strategic context; not verified facts, identity, or action authority"}
    remaining = min(limit, LIMIT)
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
    result["content_sha256"] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    query = commands.add_parser("context")
    query.add_argument("--date", required=True)
    query.add_argument("--focus", default="")
    query.add_argument("--json", action="store_true")
    notes = commands.add_parser("note-search", help="Read-only duplicate orientation; inspect full targets before nomination.")
    notes.add_argument("--focus", required=True)
    notes.add_argument("--work-id", action="append", default=[])
    notes.add_argument("--json", action="store_true")
    check = commands.add_parser("check-nominations", help="Validate candidate-only judgments without saving notes.")
    check.add_argument("--input", required=True, type=Path)
    check.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.command == "context":
        result = context(args.date, args.focus)
    else:
        import cognitive_context
        result = cognitive_context.note_search(args.focus, REPO_ROOT, work_ids=args.work_id) if args.command == "note-search" else cognitive_context.nominations(json.loads(args.input.read_text(encoding="utf-8")), REPO_ROOT)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
