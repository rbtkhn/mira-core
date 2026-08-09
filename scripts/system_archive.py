from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from system_archive_store import ArchiveError, ArtifactStore, RecordInput, canonical_json, catalog_counts, catalog_fingerprint, ingest_record, iter_active_records, parse_time, safe_logical_path, sha256_bytes, verify_derivation_acyclic


REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_ROOT = REPO_ROOT / "system-archive"
COLLECTIONS_PATH = SYSTEM_ROOT / "collections.json"
ARCHIVE_ROOT_ENV = "NARRATIVE_SYSTEM_ARCHIVE_ROOT"
REPLICA_ROOT_ENV = "NARRATIVE_SYSTEM_ARCHIVE_REPLICA_ROOT"
COMPILER_VERSION = "system-archive-context-compiler-v1"
REPLAY_VERSION = "system-archive-replay-plan-v1"
TOKEN_RE = re.compile(r"[\w'-]+",re.UNICODE)


def load_json(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as error: raise ArchiveError(f"could not read JSON {path}: {error}") from error


def write_json(path: Path,value: Any) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); temporary=path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n"); temporary.replace(path)


def external_output(path: Path) -> Path:
    resolved=path.expanduser().resolve()
    try: resolved.relative_to(REPO_ROOT.resolve())
    except ValueError: return resolved
    raise ArchiveError(f"generated System Archive output must be outside Git: {resolved}")


def configured_root(variable: str, *, required: bool=True) -> Path | None:
    value=os.environ.get(variable)
    if not value:
        if required: raise ArchiveError(f"{variable} is not configured")
        return None
    return Path(value)


def store(*,create: bool=False) -> ArtifactStore:
    root=configured_root(ARCHIVE_ROOT_ENV); assert root is not None; return ArtifactStore(root,REPO_ROOT,create=create)


def collection_document(path: Path=COLLECTIONS_PATH) -> dict[str,Any]:
    document=load_json(path)
    if document.get("schema_version")!=1 or not isinstance(document.get("collections"),list): raise ArchiveError("invalid System Archive collection registry")
    return document


def collection_map() -> dict[str,dict[str,Any]]:
    result={}
    for row in collection_document()["collections"]:
        identifier=row.get("id")
        if not isinstance(identifier,str) or not identifier or identifier in result: raise ArchiveError("duplicate or invalid System Archive collection id")
        result[identifier]=row
    return result


def selected_collections(values: Sequence[str]) -> list[dict[str,Any]]:
    available=collection_map(); selected=list(values) if values else list(available); unknown=sorted(set(selected)-set(available))
    if unknown: raise ArchiveError(f"unknown collection(s): {', '.join(unknown)}")
    return [available[item] for item in selected]


def stable_record_id(prefix: str,path: str) -> str: return f"{prefix}-{sha256_bytes(path.encode())[:20]}"
def day_timestamp(value: str) -> str: return parse_time(f"{value}T00:00:00Z",label="date",required=True) or ""


def capture_search_text(body: bytes) -> str:
    texts=[]
    try:
        with gzip.open(io.BytesIO(body),"rt",encoding="utf-8") as stream:
            for line in stream:
                record=json.loads(line)
                if record.get("kind")!="message" or record.get("role") not in {"user","assistant"}: continue
                texts.extend(part["text"] for part in record.get("content",[]) if isinstance(part,dict) and part.get("type")=="text" and isinstance(part.get("text"),str))
    except (OSError,UnicodeError,json.JSONDecodeError) as error: raise ArchiveError(f"invalid Mira capture: {error}") from error
    return "\n\n".join(texts)


def discover_archive(collection: Mapping[str,Any]) -> Iterator[tuple[RecordInput,Path]]:
    manifest=load_json(REPO_ROOT/str(collection["registry_path"])); sources=manifest.get("sources")
    if not isinstance(sources,list) or manifest.get("source_count")!=len(sources): raise ArchiveError("Narrative Geopolitics source manifest count mismatch")
    for source in sources:
        logical=safe_logical_path(str(source.get("local_path",""))); path=REPO_ROOT/logical
        if not path.is_file(): raise ArchiveError(f"missing collection body: {logical}")
        body=path.read_bytes()
        yield RecordInput(stable_record_id("SAR-NG",logical),"source",logical,str(collection["id"]),str(collection["authority_owner"]),str(collection["evidence_class"]),"import-process",str(manifest.get("manifest_id","source-manifest")),day_timestamp(str(manifest.get("imported_at",""))),day_timestamp(str(source.get("date",""))),None,{"title":source.get("title"),"source_class":source.get("source_class"),"modality":source.get("modality"),"voice_slugs":source.get("voice_slugs",[]),"host_slug":source.get("host_slug"),"manifest":str(collection["registry_path"])},body.decode("utf-8",errors="replace")),path


def discover_mira(collection: Mapping[str,Any]) -> Iterator[tuple[RecordInput,Path]]:
    registry=load_json(REPO_ROOT/str(collection["registry_path"])); sessions=registry.get("sessions")
    if not isinstance(sessions,list): raise ArchiveError("invalid Mira session registry")
    for session in sessions:
        for capture in session.get("captures",[]):
            logical=safe_logical_path(str(capture.get("path",""))); path=REPO_ROOT/logical
            if not path.is_file(): raise ArchiveError(f"missing collection body: {logical}")
            body=path.read_bytes()
            if capture.get("sha256")!=sha256_bytes(body): raise ArchiveError(f"Mira registry hash mismatch: {logical}")
            yield RecordInput(str(capture.get("id")),"session-capture",logical,str(collection["id"]),str(collection["authority_owner"]),str(collection["evidence_class"]),"agent-session",str(session.get("id")),str(capture.get("observed_at")),str(session.get("started_at")),str(session.get("last_observed_at")),{"session_id":session.get("id"),"codex_session_id":session.get("codex_session_id"),"capture_id":capture.get("id"),"record_count":capture.get("record_count"),"source_class":capture.get("source_class"),"registry":str(collection["registry_path"])},capture_search_text(body)),path


def discover(collections: Sequence[Mapping[str,Any]]) -> Iterator[tuple[RecordInput,Path]]:
    for collection in collections:
        if collection.get("kind")=="narrative-geopolitics-source-manifest": yield from discover_archive(collection)
        elif collection.get("kind")=="mira-session-registry": yield from discover_mira(collection)
        else: raise ArchiveError(f"unsupported collection kind: {collection.get('kind')}")


def inventory(collections: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    counts={}; total=0; digest=hashlib.sha256(); seen=set()
    for record,path in discover(collections):
        if record.logical_path in seen: raise ArchiveError(f"duplicate collection logical path: {record.logical_path}")
        seen.add(record.logical_path); body=path.read_bytes(); counts[record.collection_id]=counts.get(record.collection_id,0)+1; total+=len(body); digest.update(canonical_json([record.logical_path,sha256_bytes(body),len(body)]).encode()+b"\n")
    return {"collections":counts,"records":sum(counts.values()),"original_bytes":total,"inventory_sha256":digest.hexdigest()}


def ingest_command(args: argparse.Namespace) -> dict[str,Any]:
    collections=selected_collections(args.collection); planned=inventory(collections)
    if args.check: return {"status":"ready","mutation":False,**planned}
    archive=store(create=True); added=unchanged=0
    with archive.connect(create=True) as connection:
        for record,path in discover(collections):
            _,changed,_=ingest_record(connection,archive,record,path.read_bytes()); added+=int(changed); unchanged+=int(not changed)
        connection.commit(); return {"status":"ingested","mutation":True,"added_versions":added,"unchanged":unchanged,"catalog":catalog_counts(connection),"catalog_fingerprint":catalog_fingerprint(connection),**planned}


def status_command(_: argparse.Namespace) -> dict[str,Any]:
    configured=configured_root(ARCHIVE_ROOT_ENV,required=False)
    if configured is None: return {"status":"unconfigured","environment":ARCHIVE_ROOT_ENV}
    archive=ArtifactStore(configured,REPO_ROOT)
    with archive.connect() as connection: return {"status":"available","root":str(archive.root),"catalog":catalog_counts(connection),"catalog_fingerprint":catalog_fingerprint(connection)}


def hydrate_command(args: argparse.Namespace) -> dict[str,Any]:
    archive=store(); collections=[row["id"] for row in selected_collections(args.collection)]; matching=would_write=0
    with archive.connect() as connection:
        rows=list(iter_active_records(connection,collection_ids=collections))
        for row in rows:
            target=REPO_ROOT/row["logical_path"]; body=archive.get_object(row["object_id"])
            if target.is_file() and target.read_bytes()==body: matching+=1; continue
            would_write+=1
            if not args.check:
                target.parent.mkdir(parents=True,exist_ok=True); temporary=target.with_name(f".{target.name}.hydrate-{os.getpid()}"); temporary.write_bytes(body); temporary.replace(target)
    return {"status":"ready" if args.check else "hydrated","mutation":not args.check,"records":len(rows),"matching":matching,"would_write":would_write,"written":0 if args.check else would_write}


def verify_catalog(archive: ArtifactStore, *, full: bool) -> list[str]:
    failures=[]
    with archive.connect() as connection:
        integrity=connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity!="ok": failures.append(f"SQLite integrity check: {integrity}")
        failures.extend(f"foreign-key violation: {tuple(row)}" for row in connection.execute("PRAGMA foreign_key_check")); failures.extend(verify_derivation_acyclic(connection))
        for row in connection.execute("SELECT object_id,original_size,stored_size FROM objects ORDER BY object_id"):
            path=archive.object_path(row["object_id"])
            if not path.is_file(): failures.append(f"missing object: {row['object_id']}")
            elif path.stat().st_size!=row["stored_size"]: failures.append(f"stored-size mismatch: {row['object_id']}")
            elif full:
                try: archive.get_object(row["object_id"],expected_size=row["original_size"])
                except ArchiveError as error: failures.append(str(error))
        missing=connection.execute("SELECT COUNT(*) FROM active_paths a WHERE NOT EXISTS (SELECT 1 FROM record_fts f WHERE f.record_id=a.record_id AND CAST(f.version AS INTEGER)=a.version)").fetchone()[0]
        if missing: failures.append(f"active records missing FTS rows: {missing}")
    return failures


def validate_repository_state(repo_root: Path=REPO_ROOT) -> list[str]:
    failures=[]; required=("system-archive/README.md","system-archive/architecture.md","system-archive/collections.json","system-archive/context-policy.json","system-archive/schemas/context-pack.schema.json","system-archive/schemas/derivation-manifest.schema.json","system-archive/schemas/replay-plan.schema.json","system-archive/schemas/task-spec.schema.json")
    failures.extend(f"missing System Archive control: {path}" for path in required if not (repo_root/path).is_file())
    try:
        document=collection_document(repo_root/"system-archive"/"collections.json"); identifiers=set()
        for row in document["collections"]:
            identifier=row.get("id")
            if identifier in identifiers: failures.append(f"duplicate System Archive collection: {identifier}")
            identifiers.add(identifier)
            if not (repo_root/str(row.get("registry_path",""))).is_file(): failures.append(f"missing collection registry: {row.get('registry_path')}")
            for field in ("kind","authority_owner","evidence_class"):
                if not isinstance(row.get(field),str) or not row[field].strip(): failures.append(f"collection {identifier} missing {field}")
    except (ArchiveError,KeyError,TypeError) as error: failures.append(str(error))
    try:
        result=subprocess.run(["git","ls-files","-z","--","narrative-geopolitics/archive/sources","mira/continuity/captures"],cwd=repo_root,check=True,capture_output=True)
        failures.extend(f"tracked corpus body: {item.decode(errors='replace')}" for item in result.stdout.split(b"\0") if item)
    except (OSError,subprocess.CalledProcessError) as error: failures.append(f"could not inspect tracked corpus bodies: {error}")
    return failures


def validate_command(args: argparse.Namespace) -> dict[str,Any]:
    failures=validate_repository_state()
    if not args.git_only: failures.extend(verify_catalog(store(),full=args.full))
    return {"status":"passed" if not failures else "failed","failures":failures}


def verify_command(args: argparse.Namespace) -> dict[str,Any]:
    archive=store(); failures=verify_catalog(archive,full=True)
    if args.hydration:
        with archive.connect() as connection:
            for row in iter_active_records(connection):
                path=REPO_ROOT/row["logical_path"]
                if not path.is_file(): failures.append(f"missing hydrated path: {row['logical_path']}")
                elif sha256_bytes(path.read_bytes())!=row["object_id"]: failures.append(f"hydration mismatch: {row['logical_path']}")
    return {"status":"passed" if not failures else "failed","failures":failures}


def fts_expression(query: str) -> str:
    tokens=TOKEN_RE.findall(query.casefold())
    if not tokens: raise ArchiveError("search query contains no searchable terms")
    return " AND ".join('"'+token.replace('"','""')+'"' for token in tokens[:32])


def search_rows(connection: sqlite3.Connection, *, query: str, collections: Sequence[str], as_of: str | None, limit: int) -> list[sqlite3.Row]:
    clauses=["record_fts MATCH ?","a.record_id=record_fts.record_id","a.version=CAST(record_fts.version AS INTEGER)"]; parameters=[fts_expression(query)]
    if collections: clauses.append("r.collection_id IN (%s)" % ",".join("?" for _ in collections)); parameters.extend(collections)
    if as_of: clauses.append("r.observed_at<=?"); parameters.append(parse_time(as_of,label="as_of",required=True))
    parameters.append(limit)
    return list(connection.execute("SELECT r.*,record_fts.body AS search_body,bm25(record_fts) AS rank FROM record_fts JOIN active_paths a JOIN records r ON r.record_id=a.record_id AND r.version=a.version WHERE "+" AND ".join(clauses)+" ORDER BY rank ASC,r.observed_at DESC,r.logical_path ASC LIMIT ?",parameters))


def row_summary(row: sqlite3.Row) -> dict[str,Any]:
    return {"record_id":row["record_id"],"version":int(row["version"]),"record_type":row["record_type"],"object_id":row["object_id"],"logical_path":row["logical_path"],"collection_id":row["collection_id"],"authority_owner":row["authority_owner"],"evidence_class":row["evidence_class"],"world_valid_from":row["world_valid_from"],"world_valid_to":row["world_valid_to"],"observed_at":row["observed_at"],"producer":{"kind":row["producer_kind"],"id":row["producer_id"]},"metadata":json.loads(row["metadata_json"])}


def search_command(args: argparse.Namespace) -> dict[str,Any]:
    archive=store(); collections=[row["id"] for row in selected_collections(args.collection)]
    with archive.connect() as connection: rows=search_rows(connection,query=args.query,collections=collections,as_of=args.as_of,limit=args.limit)
    return {"status":"ok","query":args.query,"as_of":parse_time(args.as_of,label="as_of") if args.as_of else None,"results":[{**row_summary(row),"rank":row["rank"]} for row in rows]}


def lineage_command(args: argparse.Namespace) -> dict[str,Any]:
    archive=store()
    with archive.connect() as connection:
        version=args.version or connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(args.record,)).fetchone()[0]
        if version is None: raise ArchiveError(f"unknown record: {args.record}")
        clauses=[]; parameters=[]
        if args.direction in {"out","both"}: clauses.append("(source_record_id=? AND source_version=?)"); parameters.extend((args.record,version))
        if args.direction in {"in","both"}: clauses.append("(target_record_id=? AND target_version=?)"); parameters.extend((args.record,version))
        edges=[dict(row) for row in connection.execute("SELECT * FROM edges WHERE "+" OR ".join(clauses)+" ORDER BY relation_type,edge_id",parameters)]
    return {"status":"ok","record_id":args.record,"version":int(version),"edges":edges}


def excerpt(text: str,query: str,maximum: int) -> str:
    positions=[text.casefold().find(token.casefold()) for token in TOKEN_RE.findall(query)]; positions=[p for p in positions if p>=0]; center=min(positions) if positions else 0; start=max(0,center-maximum//4); end=min(len(text),start+maximum); return text[max(0,end-maximum):end]


def context_command(args: argparse.Namespace) -> dict[str,Any]:
    task=load_json(args.task)
    if task.get("schema_version")!=1 or not isinstance(task.get("task_id"),str) or not isinstance(task.get("query"),str): raise ArchiveError("invalid context task specification")
    output=external_output(args.output); configured=[row["id"] for row in selected_collections(args.collection)]; requested=task.get("collections",configured)
    if not isinstance(requested,list) or any(item not in configured for item in requested): raise ArchiveError("task requests an unavailable collection")
    archive=store(); selected=[]; omitted=[]; remaining=args.token_budget
    with archive.connect() as connection:
        rows=search_rows(connection,query=task["query"],collections=requested,as_of=args.as_of,limit=min(int(task.get("max_records",50)),200))
        for row in rows:
            available=remaining-160
            if available<32: omitted.append({"record_id":row["record_id"],"reason":"token-budget"}); continue
            content=excerpt(row["search_body"],task["query"],min(available*4,8000)); estimate=160+max(1,(len(content)+3)//4)
            if estimate>remaining: omitted.append({"record_id":row["record_id"],"reason":"token-budget"}); continue
            selected.append({**row_summary(row),"content_excerpt":content,"estimated_tokens":estimate,"selection":{"method":"fts5-bm25-temporal-authority-v1","rank":row["rank"],"reason":"matched task query within collection and observation-time constraints"}}); remaining-=estimate
        fingerprint=catalog_fingerprint(connection)
    core={"schema_version":1,"compiler_version":COMPILER_VERSION,"task":task,"as_of":parse_time(args.as_of,label="as_of",required=True),"token_budget":args.token_budget,"estimated_tokens":args.token_budget-remaining,"catalog_fingerprint":fingerprint,"authority_boundary":"Context selection supplies provenance-linked memory; it does not change collection authority, factual adjudication, operator belief, or identity.","selected_records":selected,"contrary_or_superseding_material":[],"unresolved_material":[],"omissions":omitted}
    pack_id="CP-"+sha256_bytes(canonical_json(core).encode())[:24]
    pack={**core,"context_pack_id":pack_id,"derivation_manifest":{"schema_version":1,"derivation_id":"DRV-"+sha256_bytes(canonical_json([pack_id,fingerprint]).encode())[:24],"transformation_type":"deterministic-context-compilation","deterministic":True,"producer":{"kind":"tool","id":COMPILER_VERSION},"input_object_ids":[row["object_id"] for row in selected],"output_digest":sha256_bytes(canonical_json(core).encode()),"prompt_digest":None,"evaluation_refs":[]}}
    if not args.check: write_json(output,pack)
    return {"status":"ready" if args.check else "written","mutation":not args.check,"output":str(output),"context_pack":pack}


def replay_command(args: argparse.Namespace) -> dict[str,Any]:
    task=load_json(args.task); output=external_output(args.output); core={"schema_version":1,"contract":REPLAY_VERSION,"task":task,"as_of":parse_time(args.as_of,label="as_of",required=True),"context_pack_ref":args.context_pack,"success_criteria":task.get("success_criteria",[]),"required_receipts":["runtime-and-model-identity","input-context-digest","output-object-digest","evaluation-result","cost-latency-and-token-usage"],"execution":"external-only","canonical_effect":"none"}; value={**core,"replay_plan_id":"RP-"+sha256_bytes(canonical_json(core).encode())[:24]}
    if not args.check: write_json(output,value)
    return {"status":"ready" if args.check else "written","mutation":not args.check,"output":str(output),"replay_plan":value}


def copy_replica(source: ArtifactStore,destination: ArtifactStore) -> None:
    destination.objects_root.mkdir(parents=True,exist_ok=True)
    for item in source.objects_root.rglob("*.zst"):
        target=destination.objects_root/item.relative_to(source.objects_root)
        if target.is_file() and target.read_bytes()==item.read_bytes(): continue
        target.parent.mkdir(parents=True,exist_ok=True); temporary=target.with_name(f".{target.name}.replica-{os.getpid()}"); shutil.copyfile(item,temporary); temporary.replace(target)
    with source.connect() as source_connection:
        temporary=destination.root/f".catalog.sqlite3.replica-{os.getpid()}"; temporary.unlink(missing_ok=True); replica=sqlite3.connect(temporary)
        try: source_connection.backup(replica)
        finally: replica.close()
        temporary.replace(destination.catalog_path)


def replica_command(args: argparse.Namespace) -> dict[str,Any]:
    source=store(); replica_root=configured_root(REPLICA_ROOT_ENV); assert replica_root is not None
    if args.sync and not args.check: copy_replica(source,ArtifactStore(replica_root,REPO_ROOT,create=True))
    try:
        replica=ArtifactStore(replica_root,REPO_ROOT)
        with source.connect() as left,replica.connect() as right: left_fp,right_fp=catalog_fingerprint(left),catalog_fingerprint(right); left_counts,right_counts=catalog_counts(left),catalog_counts(right)
        failures=verify_catalog(replica,full=args.full)
        if left_fp!=right_fp: failures.append("replica catalog fingerprint differs")
        if left_counts!=right_counts: failures.append("replica catalog counts differ")
    except ArchiveError as error: left_fp=right_fp=None; left_counts=right_counts={}; failures=[str(error)]
    return {"status":"healthy" if not failures else "unhealthy","mutation":bool(args.sync and not args.check),"source_fingerprint":left_fp,"replica_fingerprint":right_fp,"source_counts":left_counts,"replica_counts":right_counts,"failures":failures}


def benchmark_command(args: argparse.Namespace) -> dict[str,Any]:
    root=external_output(args.temp_root); root.mkdir(parents=True,exist_ok=True); database=root/"system-archive-benchmark.sqlite3"; database.unlink(missing_ok=True); started=time.perf_counter(); connection=sqlite3.connect(database)
    try:
        connection.execute("CREATE TABLE records(id INTEGER PRIMARY KEY,collection TEXT,observed TEXT,object_id TEXT)"); connection.execute("CREATE INDEX records_lookup ON records(collection,observed,id)")
        for start in range(0,args.records,10000): connection.executemany("INSERT INTO records VALUES(?,?,?,?)",((i,f"collection-{i%7}",f"2026-01-{i%28+1:02d}T00:00:00Z",hashlib.sha256(str(i).encode()).hexdigest()) for i in range(start,min(start+10000,args.records))))
        connection.commit(); ingestion=time.perf_counter()-started; query_started=time.perf_counter(); result=connection.execute("SELECT COUNT(*) FROM records WHERE collection=? AND observed<=?",("collection-3","2026-01-20T00:00:00Z")).fetchone()[0]; query=time.perf_counter()-query_started
    finally: connection.close()
    return {"status":"complete","records":args.records,"database":str(database),"ingestion_seconds":ingestion,"indexed_query_seconds":query,"query_result":result}


def parser() -> argparse.ArgumentParser:
    root=argparse.ArgumentParser(description="System Archive epistemic substrate"); sub=root.add_subparsers(dest="command",required=True)
    def output(p: argparse.ArgumentParser) -> None: p.add_argument("--json",action="store_true")
    p=sub.add_parser("status"); output(p); p.set_defaults(handler=status_command)
    p=sub.add_parser("ingest"); p.add_argument("--check",action="store_true"); p.add_argument("--collection",action="append",default=[]); output(p); p.set_defaults(handler=ingest_command)
    p=sub.add_parser("hydrate"); p.add_argument("--check",action="store_true"); p.add_argument("--collection",action="append",default=[]); output(p); p.set_defaults(handler=hydrate_command)
    p=sub.add_parser("validate"); p.add_argument("--git-only",action="store_true"); p.add_argument("--full",action="store_true"); output(p); p.set_defaults(handler=validate_command)
    p=sub.add_parser("verify"); p.add_argument("--hydration",action="store_true"); output(p); p.set_defaults(handler=verify_command)
    p=sub.add_parser("search"); p.add_argument("--query",required=True); p.add_argument("--collection",action="append",default=[]); p.add_argument("--as-of"); p.add_argument("--limit",type=int,default=20); output(p); p.set_defaults(handler=search_command)
    p=sub.add_parser("lineage"); p.add_argument("--record",required=True); p.add_argument("--version",type=int); p.add_argument("--direction",choices=("in","out","both"),default="both"); output(p); p.set_defaults(handler=lineage_command)
    context=sub.add_parser("context"); context_sub=context.add_subparsers(dest="context_command",required=True); p=context_sub.add_parser("build"); p.add_argument("--task",type=Path,required=True); p.add_argument("--as-of",required=True); p.add_argument("--token-budget",type=int,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--collection",action="append",default=[]); p.add_argument("--check",action="store_true"); output(p); p.set_defaults(handler=context_command)
    replay=sub.add_parser("replay"); replay_sub=replay.add_subparsers(dest="replay_command",required=True); p=replay_sub.add_parser("plan"); p.add_argument("--task",type=Path,required=True); p.add_argument("--as-of",required=True); p.add_argument("--context-pack",required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--check",action="store_true"); output(p); p.set_defaults(handler=replay_command)
    p=sub.add_parser("replica-status"); p.add_argument("--sync",action="store_true"); p.add_argument("--check",action="store_true"); p.add_argument("--full",action="store_true"); output(p); p.set_defaults(handler=replica_command)
    p=sub.add_parser("benchmark"); p.add_argument("--records",type=int,default=1000000); p.add_argument("--temp-root",type=Path,required=True); output(p); p.set_defaults(handler=benchmark_command)
    return root


def main(arguments: list[str] | None=None) -> int:
    args=parser().parse_args(arguments)
    if getattr(args,"token_budget",256)<256: print("system-archive error: token budget must be at least 256",file=sys.stderr); return 2
    if not 1<=getattr(args,"limit",1)<=1000: print("system-archive error: limit must be between 1 and 1000",file=sys.stderr); return 2
    try: result=args.handler(args)
    except (ArchiveError,OSError,sqlite3.Error,KeyError,TypeError,ValueError) as error: print(f"system-archive error: {error}",file=sys.stderr); return 1
    print(canonical_json(result) if args.json else "\n".join([f"system_archive_status={result.get('status','unknown')}",*(f"{k}={canonical_json(v) if isinstance(v,(dict,list)) else v}" for k,v in result.items() if k!="status")]))
    return 1 if result.get("status") in {"failed","unhealthy"} else 0


if __name__=="__main__": raise SystemExit(main())
