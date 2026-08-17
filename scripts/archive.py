from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from archive_store import ArchiveError, ArtifactStore, RecordInput, add_edge, canonical_json, catalog_counts, catalog_fingerprint, ingest_record, iter_active_records, parse_time, safe_logical_path, sha256_bytes, verify_derivation_acyclic
from runtime_names import resolve_environment


REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_CONTROL_ROOT = REPO_ROOT / "archive"
COLLECTIONS_PATH = ARCHIVE_CONTROL_ROOT / "collections.json"
ARCHIVE_ROOT_ENV = "MIRA_CORE_ARCHIVE_ROOT"
REPLICA_ROOT_ENV = "MIRA_CORE_ARCHIVE_REPLICA_ROOT"
CONFIG_PATH_ENV = "MIRA_CORE_ARCHIVE_CONFIG"
DEFAULT_CONFIG_PATH = Path(r"C:\private\mira-core-archive-config.json")
FORMER_CONFIG_PATH = Path(r"C:\private\mira-core-system-archive-config.json")
LEGACY_CONFIG_PATH = Path(r"C:\private\narrative-system-archive-config.json")
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
    raise ArchiveError(f"generated Mira Archive output must be outside Git: {resolved}")


def storage_config() -> tuple[dict[str,Any] | None,Path]:
    configured=resolve_environment(CONFIG_PATH_ENV)
    path=Path(configured).expanduser() if configured else DEFAULT_CONFIG_PATH
    if not configured and not path.is_file():
        for fallback in (FORMER_CONFIG_PATH, LEGACY_CONFIG_PATH):
            if fallback.is_file():
                print(f"{fallback} is deprecated; use {DEFAULT_CONFIG_PATH}",file=sys.stderr)
                path=fallback
                break
    if not path.is_file(): return None,path
    document=load_json(path)
    if document.get("schema_version")!=1: raise ArchiveError(f"invalid Mira Archive storage configuration: {path}")
    for key in ("canonical_root","replica_root"):
        value=document.get(key)
        if not isinstance(value,str) or not value.strip() or not Path(value).expanduser().is_absolute():
            raise ArchiveError(f"invalid Mira Archive storage configuration: {key}")
    canonical=Path(document["canonical_root"]).expanduser().resolve(); replica=Path(document["replica_root"]).expanduser().resolve()
    if canonical==replica: raise ArchiveError("canonical and replica roots must differ")
    for root in (canonical,replica): validate_storage_root(root)
    return document,path.resolve()


def validate_storage_root(root: Path) -> Path:
    resolved=root.expanduser().resolve()
    try: resolved.relative_to(REPO_ROOT.resolve())
    except ValueError: pass
    else: raise ArchiveError(f"Mira Archive storage root must remain outside Git: {resolved}")
    if not resolved.is_dir(): raise ArchiveError(f"Mira Archive storage root does not exist: {resolved}")
    if not os.access(resolved,os.W_OK): raise ArchiveError(f"Mira Archive storage root is not writable: {resolved}")
    return resolved


def configured_root_resolution(variable: str, *, required: bool=True) -> tuple[Path | None,str | None]:
    environment_values={
        ARCHIVE_ROOT_ENV: resolve_environment(ARCHIVE_ROOT_ENV),
        REPLICA_ROOT_ENV: resolve_environment(REPLICA_ROOT_ENV),
    }
    document: dict[str,Any] | None=None; path=DEFAULT_CONFIG_PATH
    if not all(environment_values.values()): document,path=storage_config()
    keys={ARCHIVE_ROOT_ENV:"canonical_root",REPLICA_ROOT_ENV:"replica_root"}
    resolved: dict[str,tuple[Path,str]]={}
    for name,key in keys.items():
        value=environment_values[name]
        if value:
            resolved[name]=(validate_storage_root(Path(value)),f"environment:{name}")
        elif document is not None:
            resolved[name]=(validate_storage_root(Path(document[key])),f"config:{path}")
    if ARCHIVE_ROOT_ENV in resolved and REPLICA_ROOT_ENV in resolved and resolved[ARCHIVE_ROOT_ENV][0]==resolved[REPLICA_ROOT_ENV][0]:
        raise ArchiveError("canonical and replica roots must differ")
    if variable in resolved: return resolved[variable]
    if required: raise ArchiveError(f"{variable} is not configured and no valid private storage configuration was found")
    return None,None


def configured_root(variable: str, *, required: bool=True) -> Path | None:
    return configured_root_resolution(variable,required=required)[0]


def store(*,create: bool=False) -> ArtifactStore:
    root=configured_root(ARCHIVE_ROOT_ENV); assert root is not None; return ArtifactStore(root,REPO_ROOT,create=create)


def collection_document(path: Path=COLLECTIONS_PATH) -> dict[str,Any]:
    document=load_json(path)
    if document.get("schema_version")!=1 or not isinstance(document.get("collections"),list): raise ArchiveError("invalid Mira Archive collection registry")
    return document


def collection_map() -> dict[str,dict[str,Any]]:
    result={}
    for row in collection_document()["collections"]:
        identifier=row.get("id")
        if not isinstance(identifier,str) or not identifier or identifier in result: raise ArchiveError("duplicate or invalid Mira Archive collection id")
        result[identifier]=row
    return result


def selected_collections(values: Sequence[str], *, include_explicit_default: bool=False) -> list[dict[str,Any]]:
    available=collection_map()
    selected=list(values) if values else [
        identifier for identifier,row in available.items()
        if include_explicit_default or row.get("retrieval_policy")!="explicit-only"
    ]
    unknown=sorted(set(selected)-set(available))
    if unknown: raise ArchiveError(f"unknown collection(s): {', '.join(unknown)}")
    return [available[item] for item in selected]


def repository_path_for_logical(
    logical_path: str,
    collection_id: str,
    *,
    collections: Mapping[str,Mapping[str,Any]] | None=None,
) -> Path:
    logical=safe_logical_path(logical_path)
    collection=(collections or collection_map()).get(collection_id)
    if not collection or not collection.get("repository_root"):
        return REPO_ROOT/logical
    logical_root=safe_logical_path(str(collection["logical_root"])).rstrip("/")
    prefix=logical_root+"/"
    if not logical.startswith(prefix):
        raise ArchiveError(f"collection logical path escapes logical root: {logical}")
    repository_root=safe_logical_path(str(collection["repository_root"])).rstrip("/")
    return REPO_ROOT/repository_root/logical.removeprefix(prefix)


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
    repository_root=safe_logical_path(str(collection.get("repository_root",collection["logical_root"]))).rstrip("/")
    logical_root=safe_logical_path(str(collection["logical_root"])).rstrip("/")
    for source in sources:
        repository_path=safe_logical_path(str(source.get("local_path","")))
        prefix=repository_root+"/"
        if not repository_path.startswith(prefix): raise ArchiveError(f"Narrative Geopolitics source escapes repository root: {repository_path}")
        logical=safe_logical_path(logical_root+"/"+repository_path.removeprefix(prefix)); path=REPO_ROOT/repository_path
        if not path.is_file(): raise ArchiveError(f"missing collection body: {repository_path}")
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


def discover_journal(collection: Mapping[str,Any]) -> Iterator[tuple[RecordInput,Path]]:
    registry=load_json(REPO_ROOT/str(collection["registry_path"])); entries=registry.get("entries")
    if not isinstance(entries,list): raise ArchiveError("invalid Mira Journal registry")
    for entry in entries:
        versions=entry.get("versions",[])
        if not isinstance(versions,list) or not versions: raise ArchiveError("Mira Journal entry has no versions")
        current=versions[-1]; logical=safe_logical_path(str(entry.get("current_path",""))); path=REPO_ROOT/logical
        if not path.is_file(): raise ArchiveError(f"missing Mira Journal body: {logical}")
        body=path.read_bytes()
        if current.get("content_sha256")!=sha256_bytes(body): raise ArchiveError(f"Mira Journal registry hash mismatch: {logical}")
        approval=current.get("approval",{})
        metadata={
            "journal_id":entry.get("journal_id"),
            "version_id":current.get("version_id"),
            "title":current.get("title"),
            "word_count":current.get("word_count"),
            "authority_boundary":registry.get("authority_boundary"),
            "namespace_boundary":registry.get("namespace_boundary"),
            "retrieval_policy":collection.get("retrieval_policy"),
            "may_promote":False,
            "registry":str(collection["registry_path"]),
        }
        yield RecordInput(str(current.get("version_id")),"journal-entry",logical,str(collection["id"]),str(collection["authority_owner"]),str(collection["evidence_class"]),"model",str(current.get("author",{}).get("model_id","unknown")),str(approval.get("approved_at")),day_timestamp(str(entry.get("entry_date"))),None,metadata,body.decode("utf-8",errors="replace")),path


def external_manifest(collection: Mapping[str,Any]) -> dict[str,Any]:
    registry_path=REPO_ROOT/str(collection["registry_path"]); manifest=load_json(registry_path); documents=manifest.get("documents")
    version=manifest.get("schema_version")
    if version not in {1,2} or manifest.get("collection_id")!=collection.get("id") or not isinstance(documents,list):
        raise ArchiveError("invalid external corpus manifest")
    if manifest.get("source_repository")!=collection.get("source_repository") or manifest.get("source_commit")!=collection.get("source_commit"):
        raise ArchiveError("external corpus provenance differs from collection registry")
    if manifest.get("document_count")!=len(documents) or manifest.get("document_count")!=collection.get("expected_records"):
        raise ArchiveError("external corpus document count mismatch")
    seen=set(); logical_seen=set()
    required=("upstream_path","sha256","size","document_type","rights_status")
    for document in documents:
        if not isinstance(document,dict) or any(field not in document for field in required): raise ArchiveError("external corpus document is incomplete")
        upstream=safe_logical_path(str(document["upstream_path"]))
        if upstream in seen: raise ArchiveError(f"duplicate external corpus path: {upstream}")
        seen.add(upstream)
        if not isinstance(document["size"],int) or document["size"]<0: raise ArchiveError(f"invalid external corpus size: {upstream}")
        if not re.fullmatch(r"[0-9a-f]{64}",str(document["sha256"])): raise ArchiveError(f"invalid external corpus digest: {upstream}")
        if version==2:
            logical=safe_logical_path(str(document.get("logical_path","")))
            logical_root=safe_logical_path(str(collection.get("logical_root",""))).rstrip("/")+"/"
            if not logical.startswith(logical_root): raise ArchiveError(f"external corpus logical path escapes collection root: {logical}")
            if logical in logical_seen: raise ArchiveError(f"duplicate external corpus logical path: {logical}")
            logical_seen.add(logical)
        references=document.get("derived_from",[])
        if not isinstance(references,list) or any(not isinstance(item,str) for item in references): raise ArchiveError(f"invalid external corpus lineage: {upstream}")
    for document in documents:
        for target in document.get("derived_from",[]):
            if safe_logical_path(target) not in seen: raise ArchiveError(f"unresolved external corpus lineage target: {target}")
    if version==2:
        if manifest.get("object_byte_count")!=sum(int(row["size"]) for row in documents): raise ArchiveError("external corpus object byte count mismatch")
        exclusions=manifest.get("excluded_paths",[]); auxiliary=manifest.get("auxiliary_paths",[]); aliases=manifest.get("reference_aliases",[])
        if not isinstance(exclusions,list) or not isinstance(auxiliary,list) or not isinstance(aliases,list): raise ArchiveError("invalid external corpus v2 path controls")
        excluded_paths=[]
        for exclusion in exclusions:
            if not isinstance(exclusion,dict) or any(field not in exclusion for field in ("upstream_path","sha256","size","reason")): raise ArchiveError("invalid external corpus exclusions")
            excluded=safe_logical_path(str(exclusion["upstream_path"])); excluded_paths.append(excluded)
            if not isinstance(exclusion["size"],int) or exclusion["size"]<0 or not re.fullmatch(r"[0-9a-f]{64}",str(exclusion["sha256"])) or not str(exclusion["reason"]).strip(): raise ArchiveError("invalid external corpus exclusions")
        if len(set(excluded_paths))!=len(excluded_paths) or set(excluded_paths)&seen: raise ArchiveError("invalid external corpus exclusions")
        auxiliary_paths=[safe_logical_path(str(item)) for item in auxiliary]
        if len(set(auxiliary_paths))!=len(auxiliary_paths) or any(item not in seen for item in auxiliary_paths): raise ArchiveError("invalid external corpus auxiliary paths")
        source_prefix=safe_logical_path(str(manifest.get("source_prefix",""))).rstrip("/")+"/"
        outside_prefix={item for item in seen if not item.startswith(source_prefix)}
        if outside_prefix!=set(auxiliary_paths): raise ArchiveError("external corpus documents differ from auxiliary allowlist")
        alias_ids=set()
        for alias in aliases:
            if not isinstance(alias,dict) or alias.get("scope")!="lineage-resolution-only" or alias.get("relation_type")!="derived_from": raise ArchiveError("invalid external corpus reference alias")
            alias_id=str(alias.get("id","")); source=safe_logical_path(str(alias.get("from_prefix",""))).rstrip("/")+"/"; target=safe_logical_path(str(alias.get("to_prefix",""))).rstrip("/")+"/"
            allowed_source=safe_logical_path(str(alias.get("allowed_source_prefix",""))); allowed_target=safe_logical_path(str(alias.get("allowed_target_prefix",""))).rstrip("/")+"/"
            if not alias_id or alias_id in alias_ids or source==target or not allowed_source or not allowed_target: raise ArchiveError("invalid external corpus reference alias")
            alias_ids.add(alias_id)
        for document in documents:
            receipts=document.get("lineage_resolution_receipts",[])
            if not isinstance(receipts,list): raise ArchiveError(f"invalid lineage resolution receipts: {document['upstream_path']}")
            for receipt in receipts:
                if not isinstance(receipt,dict) or receipt.get("alias_id") not in alias_ids or safe_logical_path(str(receipt.get("resolved_target",""))) not in set(document.get("derived_from",[])): raise ArchiveError(f"invalid lineage resolution receipt: {document['upstream_path']}")
    return manifest


def external_source_root(collection: Mapping[str,Any],source_root: Path | None) -> Path:
    if source_root is None: raise ArchiveError(f"collection {collection['id']} requires --source-root")
    root=source_root.resolve()
    if not root.is_dir(): raise ArchiveError(f"external corpus source root is not a directory: {root}")
    try: root.relative_to(REPO_ROOT.resolve())
    except ValueError: pass
    else: raise ArchiveError("external corpus source root must be outside the Mira Core repository")
    result=subprocess.run(["git","-c",f"safe.directory={root.as_posix()}","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True)
    if result.returncode or result.stdout.strip()!=collection.get("source_commit"):
        raise ArchiveError(f"external corpus source commit mismatch: expected {collection.get('source_commit')}")
    return root


def external_record_id(collection: Mapping[str,Any],upstream_path: str) -> str:
    identity=f"{collection['source_repository']}@{collection['source_commit']}:{upstream_path}"
    prefix=str(collection.get("record_id_prefix","SAR-IL"))
    if not re.fullmatch(r"SAR-[A-Z0-9]{2,8}",prefix): raise ArchiveError(f"invalid external corpus record id prefix: {prefix}")
    return stable_record_id(prefix,identity)


def discover_external_corpus_v1(collection: Mapping[str,Any],manifest: Mapping[str,Any],source_root: Path | None) -> Iterator[tuple[RecordInput,Path]]:
    root=external_source_root(collection,source_root); documents=manifest["documents"]
    expected={safe_logical_path(str(row["upstream_path"])) for row in documents}; source_prefix=safe_logical_path(str(manifest["source_prefix"]))
    lane_root=(root/source_prefix).resolve()
    if not lane_root.is_dir(): raise ArchiveError(f"missing external corpus source prefix: {source_prefix}")
    actual={item.relative_to(root).as_posix() for item in lane_root.rglob("*") if item.is_file() and item.name!=".gitkeep"}
    missing=sorted(expected-actual); unexpected=sorted(actual-expected)
    if missing: raise ArchiveError(f"missing external corpus paths: {', '.join(missing[:5])}")
    if unexpected: raise ArchiveError(f"unexpected external corpus paths: {', '.join(unexpected[:5])}")
    observed=day_timestamp(str(manifest["imported_at"])); authority=str(collection["authority_owner"])
    prefix=source_prefix.rstrip("/")+"/"
    for document in documents:
        upstream=safe_logical_path(str(document["upstream_path"])); path=(root/upstream).resolve()
        try: path.relative_to(root)
        except ValueError as error: raise ArchiveError(f"external corpus path escapes source root: {upstream}") from error
        body=path.read_bytes()
        if len(body)!=document["size"] or sha256_bytes(body)!=document["sha256"]: raise ArchiveError(f"external corpus hash mismatch: {upstream}")
        relative=upstream[len(prefix):] if upstream.startswith(prefix) else upstream
        logical=safe_logical_path(f"external-corpora/{collection['id']}/{relative}")
        publication=document.get("publication_date")
        metadata={"title":document.get("title"),"document_type":document["document_type"],"genre":collection.get("genre"),"upstream_path":upstream,"source_repository":collection["source_repository"],"source_commit":collection["source_commit"],"rights_status":document["rights_status"],"retrieval_policy":collection.get("retrieval_policy"),"may_promote":False,"manifest":str(collection["registry_path"])}
        yield RecordInput(external_record_id(collection,upstream),str(document["document_type"]),logical,str(collection["id"]),authority,str(collection["evidence_class"]),"external-repository",f"{collection['source_repository']}@{collection['source_commit']}",observed,day_timestamp(str(publication)) if publication else None,None,metadata,body.decode("utf-8",errors="replace")),path


def git_object_bytes(root: Path,commit: str,path: str) -> bytes:
    result=subprocess.run(["git","-c",f"safe.directory={root.as_posix()}","-C",str(root),"cat-file","blob",f"{commit}:{path}"],capture_output=True)
    if result.returncode: raise ArchiveError(f"missing external corpus git object: {path}")
    return result.stdout


def discover_external_corpus_v2(collection: Mapping[str,Any],manifest: Mapping[str,Any],source_root: Path | None) -> Iterator[tuple[RecordInput,bytes]]:
    root=external_source_root(collection,source_root); documents=manifest["documents"]; commit=str(collection["source_commit"])
    source_prefix=safe_logical_path(str(manifest["source_prefix"])); prefix=source_prefix.rstrip("/")+"/"
    result=subprocess.run(["git","-c",f"safe.directory={root.as_posix()}","-C",str(root),"ls-tree","-r","--name-only",commit,"--",source_prefix],capture_output=True,text=True)
    if result.returncode: raise ArchiveError("could not enumerate external corpus git tree")
    actual={item for item in result.stdout.splitlines() if item and not item.endswith("/.gitkeep")}
    canonical={safe_logical_path(str(row["upstream_path"])) for row in documents if str(row["upstream_path"]).startswith(prefix)}
    excluded={safe_logical_path(str(row["upstream_path"])) for row in manifest.get("excluded_paths",[])}
    missing=sorted((canonical|excluded)-actual); unexpected=sorted(actual-(canonical|excluded))
    if missing: raise ArchiveError(f"missing external corpus paths: {', '.join(missing[:5])}")
    if unexpected: raise ArchiveError(f"unexpected external corpus paths: {', '.join(unexpected[:5])}")
    observed=day_timestamp(str(manifest["imported_at"])); authority=str(collection["authority_owner"]); aliases={str(row["id"]):row for row in manifest.get("reference_aliases",[])}
    for exclusion in manifest.get("excluded_paths",[]):
        upstream=safe_logical_path(str(exclusion["upstream_path"])); body=git_object_bytes(root,commit,upstream)
        if len(body)!=exclusion["size"] or sha256_bytes(body)!=exclusion["sha256"]: raise ArchiveError(f"external corpus exclusion hash mismatch: {upstream}")
    for document in documents:
        upstream=safe_logical_path(str(document["upstream_path"])); body=git_object_bytes(root,commit,upstream)
        if len(body)!=document["size"] or sha256_bytes(body)!=document["sha256"]: raise ArchiveError(f"external corpus hash mismatch: {upstream}")
        text=body.decode("utf-8",errors="replace")
        for receipt in document.get("lineage_resolution_receipts",[]):
            original=str(receipt["original_reference"]); alias=aliases[str(receipt["alias_id"])]
            if original not in text: raise ArchiveError(f"lineage receipt reference absent from source: {upstream}")
            normalized=safe_logical_path(str(receipt["normalized_original_path"])); from_prefix=safe_logical_path(str(alias["from_prefix"])).rstrip("/")+"/"; to_prefix=safe_logical_path(str(alias["to_prefix"])).rstrip("/")+"/"
            expected_normalized=safe_logical_path(posixpath.normpath(posixpath.join(posixpath.dirname(upstream),original)))
            allowed_source=safe_logical_path(str(alias["allowed_source_prefix"])); allowed_target=safe_logical_path(str(alias["allowed_target_prefix"])).rstrip("/")+"/"
            if normalized!=expected_normalized or not upstream.startswith(allowed_source) or not normalized.startswith(from_prefix): raise ArchiveError(f"lineage receipt is outside alias source: {upstream}")
            resolved=to_prefix+normalized[len(from_prefix):]
            if resolved!=safe_logical_path(str(receipt["resolved_target"])) or not resolved.startswith(allowed_target): raise ArchiveError(f"lineage receipt target mismatch: {upstream}")
        publication=document.get("publication_date")
        metadata={"title":document.get("title"),"document_type":document["document_type"],"genre":collection.get("genre"),"upstream_path":upstream,"source_repository":collection["source_repository"],"source_commit":collection["source_commit"],"rights_status":document["rights_status"],"rights_policy":document.get("rights_policy"),"retrieval_policy":collection.get("retrieval_policy"),"hydration_policy":collection.get("hydration_policy"),"body_status":document.get("body_status"),"completeness_status":document.get("completeness_status"),"source_body_availability":document.get("source_body_availability"),"may_promote":False,"may_quote":False,"may_republish":False,"may_route_to_customer":False,"manifest":str(collection["registry_path"])}
        yield RecordInput(external_record_id(collection,upstream),str(document["document_type"]),safe_logical_path(str(document["logical_path"])),str(collection["id"]),authority,str(collection["evidence_class"]),"external-repository",f"{collection['source_repository']}@{collection['source_commit']}",observed,day_timestamp(str(publication)) if publication else None,None,metadata,text),body


def discover_external_corpus(collection: Mapping[str,Any],source_root: Path | None) -> Iterator[tuple[RecordInput,Path|bytes]]:
    manifest=external_manifest(collection)
    if manifest["schema_version"]==1: yield from discover_external_corpus_v1(collection,manifest,source_root)
    else: yield from discover_external_corpus_v2(collection,manifest,source_root)


REPOSITORY_ARTIFACT_PREFIXES = (
    "docs/audits/",
    "narrative-geopolitics/work/system-improvement/mira-journal-outcomes/",
)
REPOSITORY_ARTIFACT_TYPES = {"baseline-audit","validation-receipt","outcome-measurement"}


def repository_artifact_manifest(collection: Mapping[str,Any]) -> dict[str,Any]:
    manifest=load_json(REPO_ROOT/str(collection["registry_path"])); documents=manifest.get("documents")
    if manifest.get("schema_version")!=1 or manifest.get("collection_id")!=collection.get("id") or not isinstance(documents,list):
        raise ArchiveError("invalid repository artifact manifest")
    if manifest.get("document_count")!=len(documents): raise ArchiveError("repository artifact document count mismatch")
    paths=[]
    for document in documents:
        if not isinstance(document,dict): raise ArchiveError("repository artifact document is malformed")
        required=("path","sha256","size","document_type","observed_at","derived_from","may_promote")
        if any(field not in document for field in required): raise ArchiveError("repository artifact document is incomplete")
        logical=safe_logical_path(str(document["path"])); paths.append(logical)
        if not logical.startswith(REPOSITORY_ARTIFACT_PREFIXES): raise ArchiveError(f"repository artifact path is outside the allowlist: {logical}")
        if document["document_type"] not in REPOSITORY_ARTIFACT_TYPES: raise ArchiveError(f"unsupported repository artifact type: {document['document_type']}")
        if not re.fullmatch(r"[0-9a-f]{64}",str(document["sha256"])) or not isinstance(document["size"],int) or document["size"]<0:
            raise ArchiveError(f"repository artifact digest or size is malformed: {logical}")
        if document["may_promote"] is not False: raise ArchiveError(f"repository artifact may not promote: {logical}")
        parse_time(str(document["observed_at"]),label="repository artifact observed_at",required=True)
        if not isinstance(document["derived_from"],list): raise ArchiveError(f"repository artifact lineage is malformed: {logical}")
        body=REPO_ROOT/logical
        if not body.is_file(): raise ArchiveError(f"missing repository artifact: {logical}")
        value=body.read_bytes()
        if sha256_bytes(value)!=document["sha256"] or len(value)!=document["size"]:
            raise ArchiveError(f"repository artifact bytes differ from manifest: {logical}")
    if len(set(paths))!=len(paths): raise ArchiveError("duplicate repository artifact path")
    known=set(paths)
    for document in documents:
        for target in document["derived_from"]:
            if safe_logical_path(str(target)) not in known: raise ArchiveError(f"unresolved repository artifact lineage: {target}")
    return manifest


def repository_artifact_record_id(document: Mapping[str,Any]) -> str:
    identity=f"{safe_logical_path(str(document['path']))}\n{document['sha256']}"
    return stable_record_id("SAR-SI",identity)


def discover_repository_artifacts(collection: Mapping[str,Any]) -> Iterator[tuple[RecordInput,Path]]:
    manifest=repository_artifact_manifest(collection); logical_root=safe_logical_path(str(collection["logical_root"]))
    for document in manifest["documents"]:
        source=safe_logical_path(str(document["path"])); digest=str(document["sha256"])
        logical=f"{logical_root}/{digest[:16]}/{source}"
        yield RecordInput(
            repository_artifact_record_id(document),str(document["document_type"]),logical,str(collection["id"]),
            str(collection["authority_owner"]),str(collection["evidence_class"]),"repository-process",
            str(manifest["manifest_id"]),str(document["observed_at"]),str(document["observed_at"]),None,
            {"source_path":source,"source_sha256":digest,"retrieval_policy":collection.get("retrieval_policy"),
             "may_promote":False,"manifest":str(collection["registry_path"])},
            (REPO_ROOT/source).read_text(encoding="utf-8",errors="replace"),
        ),REPO_ROOT/source


def read_discovered_body(source: Path|bytes) -> bytes: return source if isinstance(source,bytes) else source.read_bytes()


COLLECTION_ADAPTERS = {
    "narrative-geopolitics-source-manifest": lambda collection,source_root: discover_archive(collection),
    "mira-session-registry": lambda collection,source_root: discover_mira(collection),
    "mira-journal-registry": lambda collection,source_root: discover_journal(collection),
    "external-corpus-manifest": lambda collection,source_root: discover_external_corpus(collection,source_root),
    "repository-artifact-manifest": lambda collection,source_root: discover_repository_artifacts(collection),
}


def discover(collections: Sequence[Mapping[str,Any]],source_root: Path | None=None) -> Iterator[tuple[RecordInput,Path|bytes]]:
    for collection in collections:
        adapter=COLLECTION_ADAPTERS.get(str(collection.get("kind")))
        if adapter is None: raise ArchiveError(f"unsupported collection kind: {collection.get('kind')}")
        yield from adapter(collection,source_root)


def inventory(collections: Sequence[Mapping[str,Any]],source_root: Path | None=None) -> dict[str,Any]:
    counts={}; total=0; digest=hashlib.sha256(); seen=set()
    for record,path in discover(collections,source_root):
        if record.logical_path in seen: raise ArchiveError(f"duplicate collection logical path: {record.logical_path}")
        seen.add(record.logical_path); body=read_discovered_body(path); counts[record.collection_id]=counts.get(record.collection_id,0)+1; total+=len(body); digest.update(canonical_json([record.logical_path,sha256_bytes(body),len(body)]).encode()+b"\n")
    return {"collections":counts,"records":sum(counts.values()),"original_bytes":total,"inventory_sha256":digest.hexdigest()}


def add_external_corpus_lineage(connection: sqlite3.Connection,collection: Mapping[str,Any]) -> int:
    manifest=external_manifest(collection); added=0
    for document in manifest["documents"]:
        references=document.get("derived_from",[])
        if not references: continue
        source_id=external_record_id(collection,str(document["upstream_path"])); source_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(source_id,)).fetchone()[0]
        if source_version is None: raise ArchiveError(f"missing external lineage source: {document['upstream_path']}")
        for target_path in references:
            target_id=external_record_id(collection,target_path); target_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(target_id,)).fetchone()[0]
            if target_version is None: raise ArchiveError(f"missing external lineage target: {target_path}")
            before=connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
            metadata={"manifest":str(collection["registry_path"])}
            if manifest.get("schema_version")==2:
                receipt=next((row for row in document.get("lineage_resolution_receipts",[]) if row.get("resolved_target")==target_path),None)
                metadata={**metadata,"resolution":"reviewed-historical-relocation" if receipt else "literal"}
                if receipt: metadata.update({"alias_id":receipt["alias_id"],"original_reference":receipt["original_reference"]})
            add_edge(connection,source=(source_id,int(source_version)),target=(target_id,int(target_version)),relation_type="derived_from",metadata=metadata)
            added+=int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]>before)
    return added


def add_repository_artifact_lineage(connection: sqlite3.Connection,collection: Mapping[str,Any]) -> int:
    manifest=repository_artifact_manifest(collection); by_path={str(row["path"]):row for row in manifest["documents"]}; added=0
    for document in manifest["documents"]:
        source_id=repository_artifact_record_id(document); source_version=connection.execute(
            "SELECT MAX(version) FROM records WHERE record_id=?",(source_id,)
        ).fetchone()[0]
        if source_version is None: raise ArchiveError(f"missing repository artifact lineage source: {document['path']}")
        for target_path in document["derived_from"]:
            target=by_path[str(target_path)]; target_id=repository_artifact_record_id(target); target_version=connection.execute(
                "SELECT MAX(version) FROM records WHERE record_id=?",(target_id,)
            ).fetchone()[0]
            if target_version is None: raise ArchiveError(f"missing repository artifact lineage target: {target_path}")
            before=connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
            add_edge(connection,source=(source_id,int(source_version)),target=(target_id,int(target_version)),relation_type="derived_from",metadata={"manifest":str(collection["registry_path"])})
            added+=int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]>before)
    return added


def add_journal_lineage(connection: sqlite3.Connection) -> int:
    journal=load_json(REPO_ROOT/"mira"/"journal-registry.json")
    continuity=load_json(REPO_ROOT/"mira"/"continuity"/"session-registry.json")
    record_capture: dict[str,str]={}
    for session in continuity.get("sessions",[]):
        for capture in session.get("captures",[]):
            path=REPO_ROOT/str(capture.get("path",""))
            if not path.is_file(): continue
            try:
                rows=[json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]
            except (OSError,json.JSONDecodeError): continue
            for row in rows:
                if isinstance(row,dict) and isinstance(row.get("record_id"),str):
                    record_capture[row["record_id"]]=str(capture.get("id"))
    added=0
    for entry in journal.get("entries",[]):
        versions=entry.get("versions",[])
        if not versions: continue
        current=versions[-1]; journal_id=str(current.get("version_id"))
        source_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(journal_id,)).fetchone()[0]
        if source_version is None: continue
        source=(journal_id,int(source_version))
        capture_records: dict[str,list[str]]={}
        for ref in current.get("source_refs",[]):
            if not isinstance(ref,dict): continue
            if ref.get("kind")=="mira-session-capture":
                capture_records.setdefault(str(ref.get("capture_id")),[]).extend(str(item) for item in ref.get("record_ids",[]))
            elif ref.get("kind")=="mira-session-records":
                for record_id in ref.get("record_ids",[]):
                    capture_id=record_capture.get(str(record_id))
                    if capture_id: capture_records.setdefault(capture_id,[]).append(str(record_id))
        for capture_id,record_ids in sorted(capture_records.items()):
            target_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(capture_id,)).fetchone()[0]
            if target_version is None: continue
            before=connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
            add_edge(connection,source=source,target=(capture_id,int(target_version)),relation_type="derived_from",metadata={"record_ids":sorted(set(record_ids))})
            added+=int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]>before)
        approval=current.get("approval",{})
        approval_capture=record_capture.get(str(approval.get("record_ref","")))
        if approval_capture:
            target_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(approval_capture,)).fetchone()[0]
            if target_version is not None:
                before=connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
                add_edge(connection,source=source,target=(approval_capture,int(target_version)),relation_type="collection:mira-journal:approved_by",metadata={"record_ref":approval.get("record_ref")})
                added+=int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]>before)
        if len(versions)>1:
            previous_id=str(versions[-2].get("version_id"))
            previous_version=connection.execute("SELECT MAX(version) FROM records WHERE record_id=?",(previous_id,)).fetchone()[0]
            if previous_version is not None:
                before=connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
                add_edge(connection,source=source,target=(previous_id,int(previous_version)),relation_type="supersedes")
                added+=int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0]>before)
    return added


def ingest_command(args: argparse.Namespace) -> dict[str,Any]:
    collections=selected_collections(args.collection,include_explicit_default=True)
    if not args.collection:
        collections=[
            row for row in collections
            if row.get("kind") not in {"external-corpus-manifest","repository-artifact-manifest"}
        ]
    if args.source_root and not any(row.get("kind")=="external-corpus-manifest" for row in collections): raise ArchiveError("--source-root requires an external corpus collection")
    planned=inventory(collections,args.source_root)
    if args.check: return {"status":"ready","mutation":False,**planned}
    archive=store(create=True); added=unchanged=0
    with archive.connect(create=True) as connection:
        for record,path in discover(collections,args.source_root):
            _,changed,_=ingest_record(connection,archive,record,read_discovered_body(path)); added+=int(changed); unchanged+=int(not changed)
        lineage_edges=add_journal_lineage(connection) if any(row.get("id")=="mira-journal" for row in collections) else 0
        for collection in collections:
            if collection.get("kind")=="external-corpus-manifest": lineage_edges+=add_external_corpus_lineage(connection,collection)
            elif collection.get("kind")=="repository-artifact-manifest": lineage_edges+=add_repository_artifact_lineage(connection,collection)
        connection.commit(); return {"status":"ingested","mutation":True,"added_versions":added,"unchanged":unchanged,"lineage_edges_added":lineage_edges,"catalog":catalog_counts(connection),"catalog_fingerprint":catalog_fingerprint(connection),**planned}


def status_command(_: argparse.Namespace) -> dict[str,Any]:
    configured,source=configured_root_resolution(ARCHIVE_ROOT_ENV,required=False)
    if configured is None: return {"status":"unconfigured","environment":ARCHIVE_ROOT_ENV,"config_path":str(storage_config()[1])}
    archive=ArtifactStore(configured,REPO_ROOT)
    with archive.connect() as connection:
        collections=collection_visibility(connection)
        return {"status":"available","root":str(archive.root),"configuration_source":source,"catalog":catalog_counts(connection),"catalog_fingerprint":catalog_fingerprint(connection),"collections":collections}


def catalog_collection_counts(connection: sqlite3.Connection) -> dict[str,int]:
    return {str(row["collection_id"]):int(row["count"]) for row in connection.execute("SELECT collection_id,COUNT(*) AS count FROM active_paths GROUP BY collection_id ORDER BY collection_id")}


def collection_visibility(connection: sqlite3.Connection) -> dict[str,Any]:
    registry=collection_map(); catalog=catalog_collection_counts(connection); catalog_metadata=catalog_collection_metadata(connection); identifiers=sorted(set(registry)|set(catalog))
    rows=[]
    for identifier in identifiers:
        registered=registry.get(identifier,{}); catalog_row=catalog_metadata.get(identifier,{})
        rows.append({
            "id":identifier,
            "registry_present":identifier in registry,
            "catalog_present":identifier in catalog,
            "active_records":catalog.get(identifier,0),
            "kind":registered.get("kind"),
            "retrieval_policy":registered.get("retrieval_policy"),
            "hydration_policy":registered.get("hydration_policy"),
            "registry_path":registered.get("registry_path") or catalog_row.get("manifest"),
            "authority_owner":registered.get("authority_owner") or catalog_row.get("authority_owner"),
            "evidence_class":registered.get("evidence_class") or catalog_row.get("evidence_class"),
        })
    registry_ids=set(registry); catalog_ids=set(catalog)
    return {"registered":len(registry_ids),"catalog":len(catalog_ids),"shared":sorted(registry_ids&catalog_ids),"registry_only":sorted(registry_ids-catalog_ids),"catalog_only":sorted(catalog_ids-registry_ids),"items":rows}


def catalog_collection_metadata(connection: sqlite3.Connection) -> dict[str,dict[str,Any]]:
    result={}
    for row in connection.execute("SELECT collection_id,authority_owner,evidence_class,metadata_json FROM records WHERE (collection_id,version) IN (SELECT collection_id,MAX(version) FROM records GROUP BY collection_id) ORDER BY collection_id"):
        metadata=json.loads(row["metadata_json"])
        result[str(row["collection_id"])]={"authority_owner":row["authority_owner"],"evidence_class":row["evidence_class"],"manifest":metadata.get("manifest")}
    return result


def collections_command(_: argparse.Namespace) -> dict[str,Any]:
    archive=store()
    with archive.connect() as connection: collections=collection_visibility(connection); fingerprint=catalog_fingerprint(connection)
    return {"status":"ok","catalog_fingerprint":fingerprint,"collections":collections,"authority_boundary":"Collection visibility is inventory evidence only; it does not repair registries, hydrate bodies, verify claims, publish, or promote records across collections."}


def hydrate_command(args: argparse.Namespace) -> dict[str,Any]:
    selected=selected_collections(args.collection,include_explicit_default=True)
    disabled=[row["id"] for row in selected if row.get("hydration_policy")=="disabled"]
    if args.collection and disabled: raise ArchiveError(f"hydration disabled for collection(s): {', '.join(disabled)}")
    selected=[row for row in selected if row.get("hydration_policy")!="disabled"]
    archive=store(); collections=[row["id"] for row in selected]; collection_by_id={str(row["id"]):row for row in selected}; matching=would_write=0
    with archive.connect() as connection:
        rows=list(iter_active_records(connection,collection_ids=collections))
        for row in rows:
            target=repository_path_for_logical(row["logical_path"],row["collection_id"],collections=collection_by_id); body=archive.get_object(row["object_id"])
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
    failures=[]; required=("archive/README.md","archive/architecture.md","archive/collections.json","archive/context-policy.json","archive/schemas/context-pack.schema.json","archive/schemas/derivation-manifest.schema.json","archive/schemas/replay-plan.schema.json","archive/schemas/task-spec.schema.json","archive/schemas/repository-artifact-manifest.schema.json")
    failures.extend(f"missing Mira Archive control: {path}" for path in required if not (repo_root/path).is_file())
    try:
        document=collection_document(repo_root/"archive"/"collections.json"); identifiers=set()
        for row in document["collections"]:
            identifier=row.get("id")
            if identifier in identifiers: failures.append(f"duplicate Mira Archive collection: {identifier}")
            identifiers.add(identifier)
            if not (repo_root/str(row.get("registry_path",""))).is_file(): failures.append(f"missing collection registry: {row.get('registry_path')}")
            for field in ("kind","authority_owner","evidence_class"):
                if not isinstance(row.get(field),str) or not row[field].strip(): failures.append(f"collection {identifier} missing {field}")
            if row.get("retrieval_policy") not in {None,"default","explicit-only"}: failures.append(f"collection {identifier} has invalid retrieval_policy")
            if row.get("hydration_policy") not in {None,"default","disabled"}: failures.append(f"collection {identifier} has invalid hydration_policy")
            if row.get("kind") not in COLLECTION_ADAPTERS: failures.append(f"unsupported collection kind: {row.get('kind')}")
            elif row.get("kind")=="external-corpus-manifest": external_manifest(row)
            elif row.get("kind")=="repository-artifact-manifest": repository_artifact_manifest(row)
        policy=load_json(repo_root/"archive"/"context-policy.json")
        derived=sorted(str(row["id"]) for row in document["collections"] if row.get("retrieval_policy")=="explicit-only")
        if policy.get("explicit_only_collections")!=derived: failures.append("Mira Archive explicit-only policy drifts from collection registry")
    except (ArchiveError,KeyError,TypeError) as error: failures.append(str(error))
    try:
        result=subprocess.run(["git","ls-files","-z","--","archive/sources/geopolitics/sources","mira/continuity/captures"],cwd=repo_root,check=True,capture_output=True)
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
        collections=collection_map()
        with archive.connect() as connection:
            for row in iter_active_records(connection):
                path=repository_path_for_logical(row["logical_path"],row["collection_id"],collections=collections)
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
    archive=store()
    with archive.connect() as connection:
        collections=search_collection_ids(args.collection,connection)
        rows=search_rows(connection,query=args.query,collections=collections,as_of=args.as_of,limit=args.limit)
    return {"status":"ok","query":args.query,"as_of":parse_time(args.as_of,label="as_of") if args.as_of else None,"results":[{**row_summary(row),"rank":row["rank"]} for row in rows]}


def search_collection_ids(values: Sequence[str], connection: sqlite3.Connection) -> list[str]:
    if not values: return [row["id"] for row in selected_collections(values)]
    registry=set(collection_map()); catalog=set(catalog_collection_counts(connection)); unknown=sorted(set(values)-registry-catalog)
    if unknown: raise ArchiveError(f"unknown collection(s): {', '.join(unknown)}")
    return list(values)


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
    root=external_output(args.temp_root); root.mkdir(parents=True,exist_ok=True); database=root/"archive-benchmark.sqlite3"; database.unlink(missing_ok=True); started=time.perf_counter(); connection=sqlite3.connect(database)
    try:
        connection.execute("CREATE TABLE records(id INTEGER PRIMARY KEY,collection TEXT,observed TEXT,object_id TEXT)"); connection.execute("CREATE INDEX records_lookup ON records(collection,observed,id)")
        for start in range(0,args.records,10000): connection.executemany("INSERT INTO records VALUES(?,?,?,?)",((i,f"collection-{i%7}",f"2026-01-{i%28+1:02d}T00:00:00Z",hashlib.sha256(str(i).encode()).hexdigest()) for i in range(start,min(start+10000,args.records))))
        connection.commit(); ingestion=time.perf_counter()-started; query_started=time.perf_counter(); result=connection.execute("SELECT COUNT(*) FROM records WHERE collection=? AND observed<=?",("collection-3","2026-01-20T00:00:00Z")).fetchone()[0]; query=time.perf_counter()-query_started
    finally: connection.close()
    return {"status":"complete","records":args.records,"database":str(database),"ingestion_seconds":ingestion,"indexed_query_seconds":query,"query_result":result}


def parser() -> argparse.ArgumentParser:
    root=argparse.ArgumentParser(description="Mira Archive epistemic substrate"); sub=root.add_subparsers(dest="command",required=True)
    def output(p: argparse.ArgumentParser) -> None: p.add_argument("--json",action="store_true")
    p=sub.add_parser("status"); output(p); p.set_defaults(handler=status_command)
    p=sub.add_parser("collections"); output(p); p.set_defaults(handler=collections_command)
    p=sub.add_parser("ingest"); p.add_argument("--check",action="store_true"); p.add_argument("--collection",action="append",default=[]); p.add_argument("--source-root",type=Path); output(p); p.set_defaults(handler=ingest_command)
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
    if getattr(args,"token_budget",256)<256: print("archive error: token budget must be at least 256",file=sys.stderr); return 2
    if not 1<=getattr(args,"limit",1)<=1000: print("archive error: limit must be between 1 and 1000",file=sys.stderr); return 2
    try: result=args.handler(args)
    except (ArchiveError,OSError,sqlite3.Error,KeyError,TypeError,ValueError) as error: print(f"archive error: {error}",file=sys.stderr); return 1
    print(canonical_json(result) if args.json else "\n".join([f"archive_status={result.get('status','unknown')}",*(f"{k}={canonical_json(v) if isinstance(v,(dict,list)) else v}" for k,v in result.items() if k!="status")]))
    return 1 if result.get("status") in {"failed","unhealthy"} else 0


if __name__=="__main__": raise SystemExit(main())
