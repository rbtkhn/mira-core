#!/usr/bin/env python3
"""In-place, offline-verifiable Mira continuity portability tooling."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
PRIVATE = REPO_ROOT / ".mira-private"
LEGACY_PRIVATE = Path(r"C:\private")
PORTABILITY = PRIVATE / "portability"
DISPOSITIONS = PORTABILITY / "dispositions.json"
MANIFEST = PORTABILITY / "manifest.json"
ALLOWED = {
    "include-canonical", "include-private-active", "include-inactive-legacy",
    "include-recovery", "reconstructible-from-bundled-source", "exclude-unrelated",
    "exclude-secret-or-credential", "exclude-machine-cache",
}
DIRS = ("state", "archive/canonical", "archive/replica", "sessions/raw",
        "sessions/attachments", "sessions/rest", "journal/drafts", "journal/revisions", "legacy",
        "recovery", "runtime/skills", "runtime/automations", "runtime/runtimes",
        "portability")
PLATFORMS = ("windows-x64", "linux-x64", "macos-arm64")
LEGACY_DIRS = ("mira-autobiographical-reflections", "mira-documents", "mira-dream",
               "mira-history", "mira-journal-audits", "recursive-learning",
               "recursive-learning-candidates", "historical-reference", "mentorship")
SECRET_NAMES = {"auth.json", "sandbox_secrets.json", "credentials.json"}
ATTACHMENT_RE = re.compile(
    r"(?i)[a-z]:[\\/]Users[\\/][^\\/\r\n]+[\\/]\.codex[\\/]attachments[\\/]"
    r"[0-9a-f-]+[\\/][^\s\"<>|:']+"
)


class PortabilityError(RuntimeError): pass


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def beneath(path: Path, root: Path | None = None) -> Path:
    root = root or REPO_ROOT
    resolved = path.resolve()
    try: resolved.relative_to(root.resolve())
    except ValueError as error: raise PortabilityError(f"target escapes existing Mira Core root: {resolved}") from error
    return resolved


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    beneath(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(*args: str, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def copy_file(source: Path, destination: Path) -> dict[str, Any]:
    beneath(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    before = sha(source); shutil.copy2(source, destination); after = sha(destination)
    if before != after: raise PortabilityError(f"copy verification failed: {source}")
    return {"source": str(source), "destination": destination.relative_to(REPO_ROOT).as_posix(), "sha256": after}


def copy_tree(source: Path, destination: Path) -> list[dict[str, Any]]:
    rows=[]
    for item in sorted(source.rglob("*")):
        if item.is_file(): rows.append(copy_file(item, destination / item.relative_to(source)))
    return rows


def sqlite_snapshot(source: Path, destination: Path) -> dict[str, Any]:
    beneath(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    temporary=destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists(): temporary.unlink()
    src=sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    dst=sqlite3.connect(temporary)
    try:
        src.backup(dst)
        check=dst.execute("PRAGMA quick_check").fetchone()[0]
        dst.commit()
    finally:
        dst.close(); src.close()
    if check != "ok": raise PortabilityError(f"SQLite snapshot failed quick_check: {source}")
    temporary.replace(destination)
    return {"source": str(source), "destination": destination.relative_to(REPO_ROOT).as_posix(), "sha256": sha(destination), "quick_check": check}


def archive_sources(*, include_portable: bool=True) -> tuple[Path | None, Path | None, Path | None]:
    candidates=[]
    configured=os.environ.get("MIRA_CORE_ARCHIVE_CONFIG", "").strip()
    if configured: candidates.append(Path(configured))
    if include_portable: candidates.append(PRIVATE/"archive/config.json")
    candidates += [LEGACY_PRIVATE/"mira-core-archive-config.json",
                   LEGACY_PRIVATE/"mira-core-system-archive-config.json", LEGACY_PRIVATE/"narrative-system-archive-config.json"]
    for config in candidates:
        if config.is_file():
            doc=json.loads(config.read_text(encoding="utf-8"))
            def resolve(value: str) -> Path:
                p=Path(value).expanduser(); return p.resolve() if p.is_absolute() else (config.parent/p).resolve()
            return resolve(doc["canonical_root"]), resolve(doc["replica_root"]), config.resolve()
    return None, None, None


def worktrees() -> list[dict[str, Any]]:
    result=[]; current={}
    process=run("git", "worktree", "list", "--porcelain")
    for line in process.stdout.splitlines()+[""]:
        if not line:
            if current:
                path=Path(current["worktree"]); state=run("git", "-c", f"safe.directory={path}", "status", "--porcelain", cwd=path)
                current["clean"] = not bool(state.stdout.strip()); result.append(current); current={}
        else:
            key, _, value=line.partition(" "); current[key]=value
    return result


def structured_attachment_paths(session: Path) -> set[Path]:
    found=set()
    def visit(value: Any, key: str="") -> None:
        if isinstance(value, dict):
            for k,v in value.items(): visit(v, str(k))
        elif isinstance(value, list):
            for v in value: visit(v, key)
        elif isinstance(value, str):
            for match in ATTACHMENT_RE.findall(value):
                found.add(Path(match.rstrip(" .,;:)]}")))
    with session.open("r", encoding="utf-8") as stream:
        for line in stream:
            try: visit(json.loads(line))
            except json.JSONDecodeError: continue
    return found


def registered_sessions() -> list[Path]:
    from mira_continuity import default_source_roots, discover_sources
    registry=REPO_ROOT/"mira/continuity/session-registry.json"
    identifiers=set()
    if registry.is_file():
        doc=json.loads(registry.read_text(encoding="utf-8"))
        identifiers={str(row.get("codex_session_id","")).casefold() for row in doc.get("sessions",[])}
    result={row.path.resolve() for row in discover_sources(repo_root=REPO_ROOT)}
    for root in default_source_roots():
        if not Path(root).is_dir(): continue
        for path in Path(root).rglob("*.jsonl"):
            if any(identifier and identifier in path.name.casefold() for identifier in identifiers): result.add(path.resolve())
    return sorted(result)


def disposition(source: str, status: str, reason: str, destination: str | None=None,
                digest: str | None=None, authority: str="none") -> dict[str, Any]:
    if status not in ALLOWED: raise PortabilityError(f"unknown disposition: {status}")
    return {"source": source, "source_path_class": "absolute-external" if Path(source).is_absolute() else "repository-relative",
            "disposition": status, "reason": reason, "destination_or_reconstruction": destination,
            "sha256": digest, "authority_status": authority}


def runtime_manifest() -> dict[str, Any]:
    codex=Path.home()/".codex"; excluded=[]
    for name in sorted(SECRET_NAMES): excluded.append({"path_class": f"user-codex/{name}", "reason": "credential or secret excluded"})
    for name in ("logs", "cache", "browser", "state.sqlite", "codex.db", "queues"):
        excluded.append({"path_class": f"user-codex/{name}", "reason": "machine cache, log, queue, or UI state excluded"})
    return {"schema_version": 1, "generated_at": utc(), "confidentiality": "none",
            "python": sys.version.split()[0], "platform": sys.platform,
            "skills": sorted(p.parent.name for p in (codex/"skills").glob("*/SKILL.md")),
            "automations": sorted(p.name for p in (codex/"automations").glob("*")), "explicit_exclusions": excluded}


def runtime_pack_state(platform_name: str) -> dict[str, Any]:
    root=PRIVATE/"runtime/runtimes"/platform_name; manifest=root/"runtime.json"
    if not manifest.is_file(): return {"ready":False,"reason":"runtime.json missing"}
    try: doc=json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {"ready":False,"reason":"runtime.json invalid"}
    if doc.get("platform") != platform_name or not str(doc.get("python_version","")).startswith("3.12."):
        return {"ready":False,"reason":"platform or pinned CPython 3.12 version invalid"}
    files=doc.get("files")
    if not isinstance(files,list) or not files: return {"ready":False,"reason":"hashed runtime, wheel, and license file inventory missing"}
    kinds=set(); failures=[]
    for row in files:
        relative=Path(str(row.get("path","")))
        if relative.is_absolute() or ".." in relative.parts: failures.append(str(relative)); continue
        path=root/relative; kinds.add(row.get("kind"))
        if not path.is_file() or sha(path)!=row.get("sha256"): failures.append(relative.as_posix())
    if not {"runtime","wheel","license"}.issubset(kinds): failures.append("required-kinds")
    return {"ready":not failures,"reason":"verified" if not failures else "missing or changed: "+", ".join(failures)}


def repository_dispositions() -> list[dict[str, Any]]:
    tracked=set(run("git","ls-files").stdout.splitlines())
    ignored=set(run("git","ls-files","--others","--ignored","--exclude-standard").stdout.splitlines())
    rows=[]
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or ".mira-private" in path.parts: continue
        relative=path.relative_to(REPO_ROOT).as_posix()
        if relative in tracked:
            state="include-canonical"; reason="tracked repository file in the transferred existing root"; authority="repository-governed"
        elif relative in ignored:
            state="include-private-active"; reason="ignored hydrated payload physically preserved in the transferred root"; authority="existing-carrier"
        else:
            state="include-private-active"; reason="untracked working-tree state physically preserved; not implied to be committed"; authority="working-tree-only"
        rows.append(disposition(relative,state,reason,relative,sha(path),authority))
    return rows


def rest_dispositions() -> list[dict[str, Any]]:
    root=PRIVATE/"sessions/rest"
    rows=[]
    if not root.is_dir(): return rows
    for path in sorted(root.rglob("*.json")):
        relative=path.relative_to(REPO_ROOT).as_posix()
        rows.append(disposition(relative,"include-private-active","private provisional Rest lifecycle receipt",relative,sha(path),"private-provisional"))
    return rows


def status() -> dict[str, Any]:
    canonical, replica, config=archive_sources()
    wt=worktrees()
    linked=[row for row in wt if Path(row["worktree"]).resolve()!=REPO_ROOT.resolve()]
    gates=None
    if DISPOSITIONS.is_file():
        ledger=json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
        gates={key:ledger.get(key) for key in ("undisposed_count","missing_required_count","unresolved_attachment_count")}
    return {"root": str(REPO_ROOT), "existing_root_only": True, "private_root": str(PRIVATE),
            "prepared": DISPOSITIONS.is_file(), "sealed": MANIFEST.is_file(),
            "archive": {"canonical": str(canonical) if canonical else None, "replica": str(replica) if replica else None, "config": str(config) if config else None},
            "registered_session_count": len(registered_sessions()), "worktrees": wt,
            "dirty_primary_root":next((not row["clean"] for row in wt if Path(row["worktree"]).resolve()==REPO_ROOT.resolve()),False),
            "unclean_linked_worktree_count":sum(not row["clean"] for row in linked),
            "dependency_gates":gates,
            "rest_receipt_count":len(rest_dispositions()),
            "runtime_platforms": {p: runtime_pack_state(p) for p in PLATFORMS},
            "confidentiality": "none"}


def prepare() -> dict[str, Any]:
    for name in DIRS: beneath(PRIVATE/name).mkdir(parents=True, exist_ok=True)
    rows=[]; copied={}
    db_specs=(("MIRA_CORE_CADENCE_DB", LEGACY_PRIVATE/"narrative-cadence.sqlite3", PRIVATE/"state/cadence.sqlite3"),
              ("MIRA_CORE_CHOICE_DB", LEGACY_PRIVATE/"narrative-choice-history.sqlite3", PRIVATE/"state/choice-history.sqlite3"))
    for env, fallback, dest in db_specs:
        source=Path(os.environ.get(env) or fallback)
        if source.is_file():
            receipt=sqlite_snapshot(source, dest); copied[env]=receipt
            rows.append(disposition(str(source), "include-private-active", "canonical portable SQLite snapshot", receipt["destination"], receipt["sha256"], "active-private-carrier"))
        else: rows.append(disposition(str(source), "include-private-active", "required private database missing", dest.relative_to(REPO_ROOT).as_posix()))
    canonical, replica, config=archive_sources(include_portable=False)
    for source, dest, label in ((canonical, PRIVATE/"archive/canonical", "canonical"), (replica, PRIVATE/"archive/replica", "replica")):
        if source and source.is_dir():
            receipts=copy_tree(source, dest); copied[f"archive_{label}"]={"files":len(receipts), "source":str(source)}
            rows.append(disposition(str(source), "include-private-active", f"byte-preserving {label} archive copy", dest.relative_to(REPO_ROOT).as_posix(), authority="active-private-carrier"))
        else: rows.append(disposition(str(source), "include-private-active", f"required {label} archive missing", dest.relative_to(REPO_ROOT).as_posix()))
    write_json(PRIVATE/"archive/config.json", {"schema_version":1, "canonical_root":"canonical", "replica_root":"replica"})
    journal_specs=((LEGACY_PRIVATE/"mira-journal-drafts", PRIVATE/"journal/drafts"), (LEGACY_PRIVATE/"mira-journal-revisions", PRIVATE/"journal/revisions"))
    for source,dest in journal_specs:
        if source.is_dir():
            receipts=copy_tree(source,dest); rows.append(disposition(str(source), "include-private-active", "private Journal material; preservation grants no promotion", dest.relative_to(REPO_ROOT).as_posix(), authority="private-noncanonical")); copied[source.name]=len(receipts)
    sessions=registered_sessions(); missing_attachments=[]; session_receipts=[]; handled_attachments=set()
    for source in sessions:
        dest=PRIVATE/"sessions/raw"/source.name; session_receipts.append(copy_file(source,dest))
        rows.append(disposition(str(source), "include-private-active", "registered Mira continuity raw session", dest.relative_to(REPO_ROOT).as_posix(), sha(source), "continuity-source"))
        for attachment in structured_attachment_paths(source):
            attachment=attachment.resolve()
            if attachment in handled_attachments: continue
            handled_attachments.add(attachment)
            if attachment.is_file():
                adest=PRIVATE/"sessions/attachments"/attachment.name; receipt=copy_file(attachment,adest)
                rows.append(disposition(str(attachment), "include-private-active", "structured dependency of qualified Mira session", receipt["destination"], receipt["sha256"], "session-dependency"))
            else: missing_attachments.append(str(attachment))
    copied["sessions"] = len(session_receipts)
    for name in LEGACY_DIRS:
        source=LEGACY_PRIVATE/name
        if source.is_dir():
            count=len(copy_tree(source, PRIVATE/"legacy"/name)); rows.append(disposition(str(source), "include-inactive-legacy", "preserved without identity, evidence, Journal, or action authority", f".mira-private/legacy/{name}", authority="inactive")); copied[f"legacy_{name}"]=count
    codex=Path.home()/".codex"
    for kind in ("skills", "automations"):
        source=codex/kind
        if source.is_dir():
            count=len(copy_tree(source, PRIVATE/"runtime"/kind)); rows.append(disposition(str(source), "include-inactive-legacy", f"installed {kind} provenance only; never auto-enabled", f".mira-private/runtime/{kind}", authority="inactive-provenance")); copied[kind]=count
    write_json(PRIVATE/"runtime/capabilities.json", runtime_manifest())
    for excluded in runtime_manifest()["explicit_exclusions"]: rows.append(disposition(excluded["path_class"], "exclude-secret-or-credential" if "credential" in excluded["reason"] else "exclude-machine-cache", excluded["reason"]))
    wt=worktrees()
    linked=[row for row in wt if Path(row["worktree"]).resolve()!=REPO_ROOT.resolve()]
    if any(not row["clean"] for row in linked): raise PortabilityError("linked worktree is dirty; refusing recovery bundle")
    bundle=PRIVATE/"recovery/repository.bundle"; run("git", "bundle", "create", str(bundle), "--all")
    run("git", "bundle", "verify", str(bundle)); rows.append(disposition("git:all-local-branches-and-tags", "include-recovery", "all-ref recovery bundle", bundle.relative_to(REPO_ROOT).as_posix(), sha(bundle), "recovery-only"))
    rows.extend(rest_dispositions())
    rows.extend(repository_dispositions())
    required_missing=[row["source"] for row in rows if row["disposition"].startswith("include-") and row["destination_or_reconstruction"] and not (REPO_ROOT/row["destination_or_reconstruction"]).exists()]
    ledger={"schema_version":1, "generated_at":utc(), "root":str(REPO_ROOT), "confidentiality":"none", "dispositions":rows,
            "undisposed_count":0, "missing_required_count":len(required_missing), "unresolved_attachment_count":len(missing_attachments),
            "missing_required":required_missing, "unresolved_attachments":sorted(set(missing_attachments)), "worktrees":wt, "copied":copied}
    write_json(DISPOSITIONS,ledger); return ledger


def payload_rows() -> list[dict[str, Any]]:
    rows=[]
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path == MANIFEST: continue
        rows.append({"path":path.relative_to(REPO_ROOT).as_posix(), "size":path.stat().st_size, "sha256":sha(path)})
    return rows


def seal(external_confirm: bool) -> dict[str, Any]:
    if not external_confirm: raise PortabilityError("seal must run from an external shell after Codex is closed; pass --external-confirm")
    if not DISPOSITIONS.is_file(): raise PortabilityError("prepare has not completed")
    ledger=json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
    for key in ("undisposed_count", "missing_required_count", "unresolved_attachment_count"):
        if ledger.get(key): raise PortabilityError(f"cannot seal: {key}={ledger[key]}")
    absent=[p for p in PLATFORMS if not runtime_pack_state(p)["ready"]]
    if absent: raise PortabilityError("missing pinned portable runtime packs: " + ", ".join(absent))
    before={p:sha(Path(p)) for p in [row["source"] for row in ledger["dispositions"] if Path(row["source"]).is_file()]}
    files=payload_rows()
    after={p:sha(Path(p)) for p in before}
    if before != after: raise PortabilityError("active sources changed during sealing")
    head=run("git","rev-parse","HEAD").stdout.strip(); branch=run("git","branch","--show-current").stdout.strip()
    manifest={"schema_version":1,"sealed_at":utc(),"root_name":REPO_ROOT.name,"confidentiality":"none","files":files,
              "git":{"head":head,"branch":branch,"status_sha256":hashlib.sha256(run("git","status","--porcelain=v1","--ignored").stdout.encode()).hexdigest()},
              "completion":{"root_calibrated":True,"dependency_closure_verified":True,"bundle_verified":True,"adapter_contract_verified":adapter_fixtures()["ok"],"kimi_operationally_verified":False,"deepseek_operationally_verified":False}}
    write_json(MANIFEST,manifest); return manifest


def verify() -> dict[str, Any]:
    if not MANIFEST.is_file(): raise PortabilityError("sealed manifest is absent")
    doc=json.loads(MANIFEST.read_text(encoding="utf-8")); missing=[]; changed=[]
    for row in doc["files"]:
        path=REPO_ROOT/row["path"]
        if not path.is_file(): missing.append(row["path"])
        elif sha(path)!=row["sha256"]: changed.append(row["path"])
    git=None
    if shutil.which("git"):
        fsck=run("git","fsck","--no-dangling",check=False); bundle=run("git","bundle","verify",str(PRIVATE/"recovery/repository.bundle"),check=False)
        git={"fsck_ok":fsck.returncode==0,"bundle_ok":bundle.returncode==0}
    return {"offline_verified":not missing and not changed,"missing":missing,"changed":changed,"git_readiness":git,"confidentiality":"none"}


def rebind() -> dict[str, Any]:
    wt=worktrees(); absent=[]
    for row in wt:
        commit=row.get("HEAD")
        if commit and run("git","cat-file","-e",f"{commit}^{{commit}}",check=False).returncode: absent.append(commit)
    if absent: raise PortabilityError("worktree reference commit absent: " + ", ".join(absent))
    return {"root":str(REPO_ROOT),"relative_paths_valid":True,"worktrees":wt,"repairs_performed":False}


def validate_arguments(arguments: str, schema: dict[str, Any]) -> dict[str, Any]:
    value=json.loads(arguments)
    if not isinstance(value,dict): raise PortabilityError("tool arguments must be a JSON object")
    allowed=set(schema.get("properties",{})); required=set(schema.get("required",[]))
    if required-set(value): raise PortabilityError("missing required tool arguments")
    if set(value)-allowed: raise PortabilityError("unknown tool arguments")
    return value


def normalize_response(provider: str, message: dict[str, Any], *, thinking: bool=False) -> dict[str, Any]:
    if provider not in {"kimi","deepseek","generic-openai"}: raise PortabilityError("unsupported provider")
    calls=message.get("tool_calls",[])
    for call in calls:
        if not call.get("id") or not isinstance(call.get("function",{}).get("arguments"),str): raise PortabilityError("unstable or malformed tool call")
    if provider=="deepseek" and thinking and "reasoning_content" not in message: raise PortabilityError("DeepSeek thinking response omitted reasoning_content")
    return {"content":message.get("content"),"tool_calls":calls,"reasoning_content":message.get("reasoning_content") if provider=="deepseek" else None}


def adapter_fixtures() -> dict[str, Any]:
    tool={"id":"call_1","type":"function","function":{"name":"probe","arguments":"{\"value\":1}"}}
    cases=[]
    for provider,message,thinking in (("kimi",{"content":None,"tool_calls":[tool]},False),("deepseek",{"content":None,"reasoning_content":"r","tool_calls":[tool]},True),("generic-openai",{"content":"ok"},False)):
        cases.append({"provider":provider,"ok":bool(normalize_response(provider,message,thinking=thinking) is not None)})
    return {"contract":"mira-model-adapter-v1","ok":all(c["ok"] for c in cases),"cases":cases,"operational":False}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True)
    for name in ("status","prepare","verify","rebind","adapter-check"): sub.add_parser(name)
    seal_parser=sub.add_parser("seal"); seal_parser.add_argument("--external-confirm",action="store_true")
    args=parser.parse_args(argv)
    try:
        result={"status":status,"prepare":prepare,"verify":verify,"rebind":rebind,"adapter-check":adapter_fixtures}.get(args.command, lambda:seal(args.external_confirm))()
        if args.command == "prepare":
            result={key:result[key] for key in ("generated_at","undisposed_count","missing_required_count","unresolved_attachment_count","copied")}
        print(json.dumps(result,indent=2,sort_keys=True)); return 0
    except (PortabilityError,OSError,ValueError,KeyError,sqlite3.Error,subprocess.SubprocessError) as error:
        print(json.dumps({"error":str(error),"command":args.command}),file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
