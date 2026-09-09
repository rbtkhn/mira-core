"""Private workspace-bound Library encounters; interpretation is not RSI evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from portable_paths import state_path, require_private_path
from bridge_handoff import locked

REPO_ROOT = Path(__file__).resolve().parents[1]
CORE = ("Homer", "Biblical tradition", "Cicero", "Dante", "Shakespeare", "Goethe", "Voltaire", "Tolstoy")
STAGES = ("observation", "diagnosis", "persistent_intervention", "separate_validation", "later_outcome")
HISTORY_LIMIT = 30


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def workspace(repo):
    return os.path.normcase(str(Path(repo).resolve()))


def location(repo=REPO_ROOT, root=None):
    return state_path(f"library/journal/{digest(workspace(repo))[:24]}", root=root, repo_root=Path(repo))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def binding_path(binding, repo):
    raw = binding.get("ref", "")
    require(text(raw), "artifact ref required")
    path = Path(raw)
    if path.is_absolute():
        return require_private_path(path, label="Library Journal private reference", repo_root=repo)
    path = (repo / path).resolve()
    require(path.is_relative_to(repo.resolve()) and ".git" not in path.parts, "unsafe artifact reference")
    return path


def gaps(entry, repo=REPO_ROOT):
    result = []
    for b in entry["artifacts"]:
        p = binding_path(b, repo)
        if not p.is_file():
            result.append({"ref": b["ref"], "status": "missing"})
        elif hashlib.sha256(p.read_bytes()).hexdigest() != b["sha256"]:
            result.append({"ref": b["ref"], "status": "changed"})
    return [{**g, "entry_id": entry.get("entry_id"), "version": entry.get("version")} for g in result]


def check_input(e):
    require(isinstance(e, dict), "entry must be an object")
    for key in ("encounter_id", "title", "narrative", "occasion", "encounter", "change", "next_test", "coverage"):
        require(text(e.get(key)), f"{key} required")
    require(len(e["narrative"].encode()) <= 100000, "narrative exceeds bounded entry size")
    require(e.get("kind") in {"reading", "retrospective-foundation", "application"}, "invalid encounter kind")
    require(e.get("encounter_status") == "substantive-closed", "only substantive closed encounters may be recorded")
    require(e.get("save_requested", True) is True, "operator requested no saving")
    start = datetime.fromisoformat(e["encounter_started_at"])
    end = datetime.fromisoformat(e["encounter_ended_at"])
    require(start.tzinfo is not None and end.tzinfo is not None and start <= end, "encounter requires ordered timezone-aware dates")
    require(isinstance(e.get("authors"), list) and all(a in CORE for a in e["authors"]), "authors must belong to Core 8")
    require(isinstance(e.get("thread_ids"), list) and e["thread_ids"] and all(re.fullmatch(r"LJT-[a-z0-9-]+", t) for t in e["thread_ids"]), "stable LJT thread IDs required")
    require(isinstance(e.get("artifacts"), list) and e["artifacts"], "artifact bindings required")
    for b in e["artifacts"]:
        require(isinstance(b, dict) and text(b.get("ref")) and re.fullmatch(r"[a-f0-9]{64}", b.get("sha256", "")), "artifact ref and SHA256 required")
    refs = {b["ref"] for b in e["artifacts"]}
    require(isinstance(e.get("passages"), list), "passages must be declared")
    if e["kind"] == "reading":
        require(e["authors"] and e["passages"], "reading requires author and passage")
    for p in e["passages"]:
        require(all(text(p.get(k)) for k in ("source_id", "edition", "language", "boundary", "ref")), "passage edition and boundary required")
        require(p["ref"] in refs, "passage must bind its source body")
    require(isinstance(e.get("attribution"), list) and e["attribution"], "attribution required")
    for a in e["attribution"]:
        require(a.get("speaker") in {"operator", "mira", "joint"} and text(a.get("contribution")) and text(a.get("source")), "attribution requires speaker, contribution, source")
    for key in ("unresolved_questions", "counterevidence", "later_use_refs", "predecessor_ids", "metaphors", "learning_changes"):
        require(isinstance(e.get(key), list), f"{key} list required")
    require(all(r in refs for r in e["later_use_refs"]), "later use must bind an artifact")
    if e["kind"] == "application":
        require(e.get("application_mode") in {"retrospective-rehearsal", "subsequent-use"}, "application mode required")
        require(e["predecessor_ids"] and e["learning_changes"] and e["later_use_refs"], "application requires predecessor, change, and separate artifact")
        require(set(e["later_use_refs"]).isdisjoint(p["ref"] for p in e["passages"]), "application artifact cannot be a passage source")
    for m in e["metaphors"]:
        require(all(text(m.get(k)) for k in ("correspondence", "reveals", "breaks_at")), "metaphor must preserve its limit")
    for change in e["learning_changes"]:
        require(text(change.get("proposal")) and text(change.get("rejection_condition")), "learning proposal and rejection condition required")
        require(change.get("status") in {"proposed", "revisable-trial", "no-material-change", "rejected", "failed-transfer", "observed-later-use"}, "journal cannot admit or certify learning")
        require(set(change.get("stages", {})) == set(STAGES), "all five learning stages required")
        for stage in change["stages"].values():
            require(stage.get("status") in {"missing", "context-only", "linked-unassessed"}, "stage evidence must remain unassessed")
            require(text(stage.get("reason")) and isinstance(stage.get("refs"), list), "stage reason and refs required")
            require(all(r in refs for r in stage["refs"]), "stage references must be bound")
            require(stage["status"] != "linked-unassessed" or stage["refs"], "linked stage requires evidence")
        if change["status"] in {"observed-later-use", "failed-transfer"}:
            require(e["later_use_refs"], "later use or failure requires a separate artifact")
        if e.get("application_mode") == "retrospective-rehearsal":
            require(change["status"] != "observed-later-use", "rehearsal is not observed later use")
            require(change["stages"]["later_outcome"]["status"] != "linked-unassessed", "rehearsal cannot supply later outcome evidence")


def entries(repo=REPO_ROOT, root=None):
    values = []
    base = location(repo, root)
    try:
        base.stat()
    except FileNotFoundError:
        return values
    # glob silently suppresses permission errors on some Python versions.
    # An inaccessible private journal must never look like an empty history.
    paths = []
    for folder in base.iterdir():
        if folder.name.startswith("LJ-") and folder.is_dir():
            paths.extend(v / "entry.json" for v in folder.iterdir() if v.name.startswith("v") and v.is_dir())
    for path in sorted(paths):
        e = json.loads(path.read_text(encoding="utf-8"))
        require(e["workspace"] == workspace(repo), "workspace mismatch")
        require(e["digest"] == digest({k: v for k, v in e.items() if k != "digest"}), "entry digest mismatch")
        require(path.parent.joinpath("entry.md").read_text(encoding="utf-8") == e["narrative"], "narrative companion mismatch")
        check_input(e)
        require(e.get("schema_version") == 1, "unsupported journal schema")
        require(e["entry_id"] == "LJ-" + digest(e["encounter_id"])[:20], "encounter identity mismatch")
        require(path.parent.name == f"v{e['version']:06d}" and path.parent.parent.name == e["entry_id"], "entry path identity mismatch")
        values.append(e)
    by_id = {}
    for e in values:
        prior = by_id.get(e["entry_id"])
        require(e["version"] == (prior["version"] + 1 if prior else 1), "broken version lineage")
        require(e["previous_digest"] == (prior["digest"] if prior else None), "broken correction digest chain")
        by_id[e["entry_id"]] = e
    ids = set(by_id)
    require(all(p in ids and p != e["entry_id"] for e in values for p in e["predecessor_ids"]), "missing or self predecessor")
    return values


def context(focus="", repo=REPO_ROOT, root=None, thread_ids=None):
    all_entries = entries(repo, root)
    heads = {e["entry_id"]: e for e in all_entries}
    ordered = sorted(heads.values(), key=lambda e: (e["recorded_at"], e["entry_id"]), reverse=True)
    latest = ordered[:3]
    words = set(re.findall(r"\w+", focus.casefold())) - {"the", "and", "of", "a", "to"}
    def score(e):
        content = [e[k] for k in ("title", "occasion", "encounter", "change", "next_test", "unresolved_questions", "counterevidence")]
        content.extend(c["proposal"] + " " + c["rejection_condition"] for c in e["learning_changes"])
        return len(words & set(re.findall(r"\w+", json.dumps(content).casefold())))

    selected_ids = list(dict.fromkeys(thread_ids or []))
    require(len(selected_ids) <= 3, "at most three explicit threads")
    known = {t for e in ordered for t in e["thread_ids"]}
    require(all(t in known for t in selected_ids), "unknown explicit thread")
    seen_threads = set(selected_ids)
    for e in sorted(ordered[3:], key=lambda e: (-score(e), e["entry_id"])):
        new = set(e["thread_ids"]) - seen_threads
        if score(e) and new and len(seen_threads) < 3:
            selected = sorted(new)[:3-len(seen_threads)]
            seen_threads.update(selected)
    relevant = [e for e in ordered if set(e["thread_ids"]) & seen_threads and e not in latest]
    omitted_related = [e["entry_id"] for e in relevant[HISTORY_LIMIT:]]
    relevant = relevant[:HISTORY_LIMIT]
    chosen = {e["entry_id"] for e in latest + relevant}
    versions = {eid: [e for e in all_entries if e["entry_id"] == eid] for eid in heads}
    predecessors, cycles, omitted = set(), [], set()

    def visit(eid, trail):
        # Follow links on historical versions as well as current heads.
        for pid in sorted({p for e in versions[eid] for p in e["predecessor_ids"]}):
            if pid in trail:
                cycles.append(list(trail) + [pid])
            elif pid not in predecessors:
                if len(predecessors) >= HISTORY_LIMIT:
                    omitted.add(pid)
                else:
                    predecessors.add(pid)
                    visit(pid, (*trail, pid))

    for eid in sorted(chosen):
        visit(eid, (eid,))
    recovered = chosen | predecessors
    corrections = [e for e in all_entries if e["entry_id"] in recovered and e != heads[e["entry_id"]]]
    omitted_versions = [{"entry_id": e["entry_id"], "version": e["version"]} for e in corrections[:-HISTORY_LIMIT]]
    corrections = corrections[-HISTORY_LIMIT:]
    return {"authority": "private interpretive context; not identity or RSI evidence", "core_8": CORE,
            "latest": latest, "relevant_older_threads": sorted(seen_threads),
            "related": list({e["entry_id"]: e for e in relevant if e not in latest}.values()),
            "corrections_and_predecessors": corrections,
            "predecessor_history": [heads[eid] for eid in sorted(predecessors - chosen)],
            "history_limits": {"limit": HISTORY_LIMIT, "cycles": cycles, "omitted_predecessors": sorted(omitted), "omitted_related": omitted_related, "omitted_corrections": omitted_versions,
                               "truncated": bool(omitted or omitted_related or omitted_versions)},
            "evidence_gaps": [g for e in all_entries if e["entry_id"] in recovered for g in gaps(e, repo)], "writes_performed": False}


def summary(repo=REPO_ROOT, root=None):
    try:
        base = location(repo, root)
        if not base.is_dir():
            return {"id": "library-journal", "status": "unavailable", "error": "private store is missing"}
        rows = entries(repo, root)
        return {"id": "library-journal", "status": "available" if rows else "empty", "entry_count": len({e["entry_id"] for e in rows}), "version_count": len(rows), "owning_command": "tools/run.ps1 library-journal", "authority_status": "private-interpretive", "reporting_verb": "records"}
    except (OSError, ValueError, KeyError) as error:
        return {"id": "library-journal", "status": "unavailable", "error": str(error)}


def record(payload, *, repo=REPO_ROOT, root=None, check=False, revise=None):
    check_input(payload)
    require(not gaps(payload, repo), "source binding missing or changed")
    input_digest = digest(payload)
    target_root = location(repo, root)

    def build():
        old = entries(repo, root)
        encounter = [e for e in old if e["encounter_id"] == payload["encounter_id"]]
        latest = encounter[-1] if encounter else None
        if latest and latest["input_digest"] == input_digest:
            return latest, False
        require(not latest or revise == latest["digest"], "existing encounter requires revise with current digest")
        require(not revise or latest is not None, "revision requires existing encounter")
        require(all(p in {e["entry_id"] for e in old} for p in payload["predecessor_ids"]), "unknown predecessor")
        require(not latest or latest["entry_id"] not in payload["predecessor_ids"], "self predecessor")
        if payload["kind"] == "application":
            parents = [e for e in old if e["entry_id"] in payload["predecessor_ids"]]
            require(any(set(e["thread_ids"]) & set(payload["thread_ids"]) for e in parents), "application must reuse a predecessor thread")
            parent_refs = {b["ref"] for e in parents for b in e["artifacts"]}
            require(any(r not in parent_refs for r in payload["later_use_refs"]), "application requires a separate application artifact")
        e = {**payload, "schema_version": 1, "workspace": workspace(repo),
             "entry_id": "LJ-" + digest(payload["encounter_id"])[:20],
             "version": latest["version"] + 1 if latest else 1,
             "previous_digest": latest["digest"] if latest else None,
             "recorded_at": datetime.now(timezone.utc).isoformat(), "input_digest": input_digest}
        e.pop("digest", None)
        e["digest"] = digest(e)
        return e, True

    if check:
        e, changed = build()
        return {"status": "ready" if changed else "already-recorded", "entry_id": e["entry_id"], "writes_performed": False}
    with locked(target_root / ".write-lock"):
        e, changed = build()
        dest = target_root / e["entry_id"] / f"v{e['version']:06d}"
        if changed:
            dest.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix=".pending-", dir=dest.parent))
            try:
                (staging / "entry.md").write_text(e["narrative"], encoding="utf-8", newline="")
                (staging / "entry.json").write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")
                os.rename(staging, dest)
            finally:
                if staging.exists():
                    for p in staging.iterdir():
                        p.unlink()
                    staging.rmdir()
        # Disposable index: canonical entry directories always rebuild it on retry.
        index = [{k: r[k] for k in ("entry_id", "version", "recorded_at", "thread_ids", "digest")} for r in entries(repo, root)]
        index_temp = target_root / ".index.pending"
        index_temp.write_text(json.dumps(index, indent=2), encoding="utf-8")
        os.replace(index_temp, target_root / "index.json")
    return {"status": "saved" if changed else "already-recorded", "entry_id": e["entry_id"], "digest": e["digest"], "version": e["version"], "path": str(dest / "entry.md"), "writes_performed": changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="private platform state root override")
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "context", "show", "validate", "record", "revise"):
        sub = subs.add_parser(name)
        sub.add_argument("--json", action="store_true")
        if name in {"prepare", "context"}:
            sub.add_argument("--focus", default="")
            sub.add_argument("--thread-id", action="append", default=[])
        if name == "show":
            sub.add_argument("entry_id")
        if name in {"record", "revise"}:
            sub.add_argument("--input", required=True, type=Path)
            sub.add_argument("--check", action="store_true")
        if name == "revise":
            sub.add_argument("--expected-digest", required=True)
    args = parser.parse_args()
    try:
        if args.command in {"record", "revise"}:
            p = require_private_path(args.input, label="journal input")
            result = record(json.loads(p.read_text(encoding="utf-8-sig")), root=args.root, check=args.check, revise=getattr(args, "expected_digest", None))
        elif args.command in {"prepare", "context"}:
            result = context(args.focus, root=args.root, thread_ids=args.thread_id)
            if args.command == "prepare":
                result["application_contract"] = {"kind": "application", "application_mode": ["retrospective-rehearsal", "subsequent-use"], "requires": "predecessor encounter, reused thread, learning change and rejection condition, separate later_use_refs artifact"}
                result["entry_contract"] = {"required": ["encounter_id", "kind", "encounter_status", "encounter_started_at", "encounter_ended_at", "title", "narrative", "occasion", "encounter", "change", "next_test", "coverage", "authors", "thread_ids", "artifacts", "passages", "attribution", "unresolved_questions", "counterevidence", "later_use_refs", "predecessor_ids", "metaphors", "learning_changes"], "stage_names": STAGES, "recording": "substantive-closed only; not menus; no-save overrides"}
        else:
            rows = entries(root=args.root)
            if args.command == "show":
                rows = [e for e in rows if e["entry_id"] == args.entry_id]
                require(rows, "entry not found")
            evidence = [g for e in rows for g in gaps(e)]
            result = {"status": "evidence-gaps" if evidence else "valid", "versions": rows if args.command == "show" else len(rows), "evidence_gaps": evidence, "writes_performed": False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get("status") == "evidence-gaps":
            raise SystemExit(1)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error), "writes_performed": False}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
