"""Private contextual ASR memory. Text judgments are supplied by the agent."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

from portable_paths import state_path

REPO = Path(__file__).resolve().parents[1]
BOUNDARY = "Contextually corrected; inferred from transcript text; not audio-verified. Examples are suggestions, not automatic rules."


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def identifier(value):
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Invalid content identifier")
    return value


def object_directories(path):
    """Missing state is empty; unreadable state must never look like no history."""
    try:
        return sorted(Path(path).iterdir())
    except FileNotFoundError:
        return []


class Memory:
    def __init__(self, repo=REPO, root=None):
        self.repo = Path(repo).resolve()
        self.workspace = digest(os.path.normcase(str(self.repo)))
        self.root = state_path(f"state/asr/{self.workspace}", root=root, repo_root=self.repo)

    def publish(self, category, key, files):
        """A directory becomes visible only after every file has been written."""
        parent = self.root / category
        if not parent.resolve().is_relative_to(self.root.resolve()):
            raise ValueError("Private storage path escapes workspace")
        parent.mkdir(parents=True, exist_ok=True)
        target = parent / identifier(key)
        if target.is_symlink():
            raise ValueError("Immutable objects may not be links")
        if target.exists():
            if any(not (target / name).is_file() or (target / name).read_bytes() != body for name, body in files.items()):
                raise ValueError("Existing immutable object differs or is incomplete")
            return target, True
        temporary = Path(tempfile.mkdtemp(prefix=".pending-", dir=parent))
        try:
            for name, body in files.items():
                with (temporary / name).open("xb") as stream:
                    stream.write(body)
                    stream.flush()
                    os.fsync(stream.fileno())
            try:
                temporary.rename(target)
            except OSError:
                if not target.exists():
                    raise
                if any((target / name).read_bytes() != body for name, body in files.items()):
                    raise ValueError("Concurrent object differs")
                return target, True
            return target, False
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)

    def source(self, raw):
        path = Path(raw)
        path = (self.repo / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file():
            raise ValueError(f"Missing source: {path}")
        body = path.read_bytes()
        text = body.decode("utf-8")
        manifest_path = self.repo / "archive/sources/geopolitics/source-manifest.json"
        manifest = read(manifest_path)
        matches = [r for r in manifest["sources"] if (self.repo / r["local_path"]).resolve() == path]
        archive_root = (self.repo / "archive/sources/geopolitics/sources").resolve()
        if path.is_relative_to(archive_root):
            if len(matches) != 1 or path.suffix != ".md":
                raise ValueError("Archived source requires unique manifest membership")
            row = matches[0]
            kind = "archived"
        else:
            match = re.search(r"(?m)^Video ID: ([A-Za-z0-9_-]{11})\s*$", text)
            rows = []
            for queue in (self.repo / "geopolitics/work/capture/youtube").glob("*.jsonl"):
                for line in queue.read_text(encoding="utf-8-sig").splitlines():
                    if not line.strip():
                        continue
                    candidate = json.loads(line)
                    attachment = candidate.get("transcript_path")
                    same_path = attachment and (self.repo / attachment).resolve() == path
                    same_id = match and candidate.get("source_identity") == "youtube:" + match[1]
                    if same_path or same_id:
                        rows.append(candidate)
            identities = {r.get("source_identity") for r in rows}
            if path.suffix.lower() != ".txt" or len(identities) != 1 or not all(identities):
                raise ValueError("Raw capture needs an unambiguous Geopolitics queue binding")
            row = rows[0]
            if match and row["source_identity"] != "youtube:" + match[1]:
                raise ValueError("Raw capture video identity mismatch")
            kind = "raw-unlanded" if not any(r.get("source_identity") == row["source_identity"] for r in manifest["sources"]) else "raw-capture-of-landed-source"
        metadata = {k: row[k] for k in ("source_identity", "title", "host_slug", "channel", "voice_slugs", "expected_voice", "url", "date", "publication_date") if k in row}
        marker = re.search(rb"(?mi)^## Transcript[^\r\n]*\r?\n", body) if kind == "archived" else re.search(rb"(?m)^\[\d+:\d+(?::\d+)?\]", body)
        if marker is None:
            raise ValueError("Cannot identify transcript body boundary")
        body_start = marker.end() if kind == "archived" else marker.start()
        if kind == "archived" and body[body_start:].lstrip().startswith(b"YouTube transcript"):
            caption = re.search(rb"(?m)^\[\d+:\d+(?::\d+)?\]", body[body_start:])
            if caption is None:
                raise ValueError("Embedded capture has no transcript boundary")
            body_start += caption.start()
        return {"path": str(path), "sha256": digest(body), "bytes": len(body), "body_start": body_start, "kind": kind, "metadata": metadata}, body

    def load_prepared(self, key, fresh=False):
        folder = self.root / "prepared" / identifier(key)
        prepared = read(folder / "prepared.json")
        if digest(prepared) != key or prepared["workspace"] != self.workspace:
            raise ValueError("Prepared input integrity failure")
        for i, source in enumerate(prepared["sources"]):
            body = (folder / f"source-{i}.txt").read_bytes()
            if digest(body) != source["sha256"]:
                raise ValueError("Frozen source integrity failure")
            if fresh and self.source(source["path"])[0] != source:
                raise ValueError("Source bytes or routing changed; prepare a new batch")
        return prepared, folder

    def prepare(self, paths):
        if not 1 <= len(paths) <= 100:
            raise ValueError("Select 1-100 sources")
        resolved = [self.source(p) for p in paths]
        if len({s[0]["path"] for s in resolved}) != len(paths):
            raise ValueError("Duplicate source path")
        value = {"schema_version": 1, "workspace": self.workspace, "sources": [s for s, _ in resolved]}
        key = digest(value)
        files = {"prepared.json": encoded(value), **{f"source-{i}.txt": b for i, (_, b) in enumerate(resolved)}}
        folder, reused = self.publish("prepared", key, files)
        return {"prepared_id": key, "path": str(folder), "reused": reused, "sources": value["sources"],
                "history": [self.search(s["metadata"].get("title", ""), limit=5) for s, _ in resolved], "boundary": BOUNDARY}

    def batches(self):
        for folder in object_directories(self.root / "batches"):
            if not re.fullmatch(r"[0-9a-f]{64}", folder.name):
                continue
            result = read(folder / "report.json")
            packet = read(folder / "packet.json")
            receipt = read(folder / "complete.json")
            if receipt != {"packet_sha256": digest(packet), "report_sha256": digest(result)}:
                raise ValueError("Batch completion integrity failure")
            if digest(packet) != folder.name:
                raise ValueError("Batch packet integrity failure")
            for row in result["sources"]:
                if row["derivative"] != f"corrected-{row['source']}.txt":
                    raise ValueError("Invalid derivative path")
                if digest((folder / row["derivative"]).read_bytes()) != row["output_sha256"]:
                    raise ValueError("Derivative integrity failure")
            yield folder.name, packet, result

    def examples(self):
        values = {}
        for key, packet, report in self.batches():
            prepared, _ = self.load_prepared(packet["prepared_id"])
            for i, correction in enumerate(packet["corrections"]):
                cid = f"{key}:{i}"
                source = prepared["sources"][correction["source"]]
                values[cid] = {**correction, "id": cid, "created_at": packet["created_at"], "model": packet["model"], "session": packet["session"], "source_identity": source["metadata"].get("source_identity", source["sha256"]),
                               "metadata": source["metadata"], "review_status": correction["status"], "review_reason": ""}
        for folder in object_directories(self.root / "reviews"):
            if not re.fullmatch(r"[0-9a-f]{64}", folder.name):
                continue
            event = read(folder / "event.json")
            if digest(event) != folder.name or event["correction_id"] not in values:
                raise ValueError("Review integrity failure")
            value = values[event["correction_id"]]
            # Sequence is local to the correction; hash directory order is immaterial.
            if event["sequence"] > value.get("review_sequence", 0):
                value.update(review_status=event["disposition"], review_reason=event["reason"],
                             review_sequence=event["sequence"], superseded_by=event.get("superseded_by"))
        return values

    def search(self, wording, context="", speaker="", channel="", limit=10):
        if not 1 <= limit <= 50:
            raise ValueError("Search limit must be 1-50")
        tokens = lambda s: set(re.findall(r"\w+", s.casefold()))
        wanted = tokens(wording + " " + context)
        groups = {}
        for value in self.examples().values():
            exact = bool(wording.strip()) and wording.casefold() == value["original"].casefold()
            overlap = len(wanted & tokens(value["original"] + " " + value["context"]))
            if not exact and not overlap:
                continue
            meta = json.dumps(value["metadata"]).casefold()
            score = 1000 * exact + overlap + 5 * bool(speaker and speaker.casefold() in meta) + 5 * bool(channel and channel.casefold() in meta)
            metadata_score = bool(speaker and speaker.casefold() in meta) + bool(channel and channel.casefold() in meta)
            rank = (int(exact), overlap, metadata_score)
            evidence = {k: value.get(k) for k in ("id", "context", "rationale", "review_status", "review_reason", "superseded_by")}
            group = (value["source_identity"], value["original"], value.get("replacement"), value["review_status"])
            if group not in groups:
                groups[group] = {**value, "score": score, "rank": rank, "example_ids": [value["id"]], "evidence": [evidence],
                                 "positive_suggestion": value["status"] == "accepted" and value["review_status"] in {"accepted", "confirmed"}}
            else:
                groups[group]["example_ids"].append(value["id"])
                groups[group]["evidence"].append(evidence)
                if rank > groups[group]["rank"]:
                    groups[group].update(value, score=score, rank=rank)
        ranked = sorted(groups.values(), key=lambda x: (*(-v for v in x["rank"]), x["id"]))
        # Return contrary history alongside positives, with a separate bound for each.
        return {"suggestions": [r for r in ranked if r["positive_suggestion"]][:limit],
                "alternatives": [r for r in ranked if not r["positive_suggestion"]][:limit], "boundary": BOUNDARY}

    def check(self, packet):
        prepared, folder = self.load_prepared(packet["prepared_id"], fresh=True)
        if packet.get("schema_version") != 1 or not all(isinstance(packet.get(k), str) and packet[k].strip() for k in ("model", "session", "created_at")):
            raise ValueError("Packet needs schema_version=1, model, session and created_at")
        if datetime.fromisoformat(packet["created_at"]).tzinfo is None:
            raise ValueError("created_at needs a timezone")
        coverage = packet.get("coverage")
        corrections = packet.get("corrections")
        if not isinstance(coverage, list) or len(coverage) != len(prepared["sources"]) or not isinstance(corrections, list):
            raise ValueError("Packet requires one coverage record per source and corrections list")
        if any(not isinstance(c, dict) for c in corrections + coverage):
            raise ValueError("Coverage and corrections must be objects")
        known = self.examples()
        outputs, report = {}, []
        for index, source in enumerate(prepared["sources"]):
            body = (folder / f"source-{index}.txt").read_bytes()
            cov = coverage[index]
            spans = cov.get("read_spans", [])
            if cov.get("source_sha256") != source["sha256"] or not isinstance(spans, list):
                raise ValueError("Coverage must bind source hash and read spans")
            previous = 0
            for start, end in spans:
                if type(start) is not int or type(end) is not int or not 0 <= previous <= start < end <= len(body):
                    raise ValueError("Invalid or overlapping reading spans")
                body[start:end].decode("utf-8")
                previous = end
            complete = bool(spans) and spans[0][0] == 0 and spans[-1][1] == len(body) and all(a[1] == b[0] for a, b in zip(spans, spans[1:]))
            if not complete and not str(cov.get("remaining", "")).strip():
                raise ValueError("Partial reading needs explicit remaining coverage")
            edits = []
            for number, c in enumerate(corrections):
                if c.get("source") != index:
                    continue
                if c.get("source_sha256") != source["sha256"] or c.get("status") not in {"accepted", "unresolved", "rejected"}:
                    raise ValueError("Correction source hash or disposition invalid")
                start, end = c.get("start"), c.get("end")
                if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(body):
                    raise ValueError("Correction offsets must select source bytes")
                if body[start:end].decode("utf-8") != c.get("original"):
                    raise ValueError("Original span mismatch")
                if not any(a <= start < end <= b for a, b in spans):
                    raise ValueError("Correction outside read coverage")
                if not all(isinstance(c.get(k), str) and c[k].strip() for k in ("context", "rationale", "confidence")):
                    raise ValueError("Correction needs context, rationale, confidence")
                context_bytes = c["context"].encode()
                occurrences = [m.start() for m in re.finditer(re.escape(context_bytes), body)]
                if not any(a <= pos <= start < end <= pos + len(context_bytes) <= b for pos in occurrences for a, b in spans):
                    raise ValueError("Supporting context must surround the span within read coverage")
                ids = c.get("example_ids")
                if not isinstance(ids, list) or any(cid not in known for cid in ids):
                    raise ValueError("Unknown or missing example references")
                replacement = c.get("replacement")
                if c["status"] == "accepted":
                    if start < source["body_start"]:
                        raise ValueError("Correction may not alter source wrapper")
                    if c["confidence"] != "high" or not isinstance(replacement, str) or not replacement or replacement == c["original"]:
                        raise ValueError("Accepted correction needs high confidence and a nonempty changed replacement")
                    if c.get("reviewed_in_context") is not True:
                        raise ValueError("Accepted correction requires context reread acknowledgement")
                    protected = r"\r|\n|>>|\[\d+:\d+(?::\d+)?\]|(?m:^#{1,6} )"
                    if re.search(protected, c["original"]) or re.search(protected, replacement):
                        raise ValueError("Correction may not alter layout, timestamps or speaker markers")
                    line_start = body.rfind(b"\n", 0, start) + 1
                    line_end = body.find(b"\n", end)
                    line = body[line_start:len(body) if line_end == -1 else line_end]
                    for marker in re.finditer(rb"\[\d+:\d+(?::\d+)?\]|^#{1,6} .*|>>|^>>[^:]*:", line):
                        if start < line_start + marker.end() and end > line_start + marker.start():
                            raise ValueError("Correction overlaps a timestamp, heading or speaker marker")
                    edits.append((start, end, replacement.encode()))
            edits.sort()
            if any(a[1] > b[0] for a, b in zip(edits, edits[1:])):
                raise ValueError("Overlapping edits")
            output = body
            for start, end, replacement in reversed(edits):
                output = output[:start] + replacement + output[end:]
            outputs[f"corrected-{index}.txt"] = output
            report.append({"source": index, "source_path": source["path"], "source_sha256": source["sha256"],
                           "kind": source["kind"], "metadata": source["metadata"],
                           "output_sha256": digest(output), "derivative": f"corrected-{index}.txt", "reading_complete": complete,
                           "remaining": cov.get("remaining", ""), "applied": len(edits),
                           "read_spans": spans,
                           "rejected": sum(c.get("source") == index and c["status"] == "rejected" for c in corrections),
                           "unresolved": sum(c.get("source") == index and c["status"] == "unresolved" for c in corrections),
                           "diff": "".join(difflib.unified_diff(body.decode().splitlines(True), output.decode().splitlines(True), fromfile="original", tofile="contextual derivative"))})
        if any(type(c.get("source")) is not int or not 0 <= c["source"] < len(prepared["sources"]) for c in corrections):
            raise ValueError("Correction references an unselected source")
        result = {"schema_version": 1, "batch_id": digest(packet), "prepared_id": packet["prepared_id"], "sources": report, "boundary": BOUNDARY}
        return result, outputs

    def save(self, packet):
        report, outputs = self.check(packet)
        receipt = {"packet_sha256": digest(packet), "report_sha256": digest(report)}
        folder, reused = self.publish("batches", report["batch_id"], {"packet.json": encoded(packet), "report.json": encoded(report), "complete.json": encoded(receipt), **outputs})
        return {**report, "path": str(folder), "reused": reused}

    def review(self, correction_id, disposition, reason, model, session, superseded_by=None):
        if disposition not in {"confirmed", "rejected", "superseded"} or not all(s.strip() for s in (reason, model, session)):
            raise ValueError("Review requires disposition, reason, model and session")
        self.root.mkdir(parents=True, exist_ok=True)
        lock = self.root / ".review-lock"
        try:
            lock.mkdir()
        except FileExistsError:
            raise ValueError("Review writer active or interrupted; inspect lock before retrying")
        try:
            examples = self.examples()
            if correction_id not in examples:
                raise ValueError("Unknown correction")
            if disposition == "superseded" and (superseded_by not in examples or superseded_by == correction_id):
                raise ValueError("Supersession needs a different existing correction")
            value = examples[correction_id]
            if disposition == "confirmed" and value["status"] != "accepted":
                raise ValueError("Unresolved/rejected candidates need a new accepted correction")
            event = {"correction_id": correction_id, "disposition": disposition, "reason": reason, "model": model,
                     "session": session, "superseded_by": superseded_by, "sequence": value.get("review_sequence", 0) + 1,
                     "at": datetime.now(timezone.utc).isoformat()}
            folder, _ = self.publish("reviews", digest(event), {"event.json": encoded(event)})
            return {**event, "path": str(folder)}
        finally:
            lock.rmdir()

    def report(self, batch_id):
        for key, packet, result in self.batches():
            if key == identifier(batch_id):
                return {**result, "path": str(self.root / "batches" / key),
                        "corrections": [v for k, v in self.examples().items() if k.startswith(key + ":")]}
        raise ValueError("Unknown batch")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("prepare"); p.add_argument("--path", action="append", required=True)
    p = subs.add_parser("search"); p.add_argument("--wording", required=True); p.add_argument("--context", default=""); p.add_argument("--speaker", default=""); p.add_argument("--channel", default=""); p.add_argument("--limit", type=int, default=10)
    for name in ("check", "save"):
        p = subs.add_parser(name); p.add_argument("--packet", type=Path, required=True)
    p = subs.add_parser("report"); p.add_argument("--batch-id", required=True)
    p = subs.add_parser("review")
    for arg in ("correction-id", "disposition", "reason", "model", "session"):
        p.add_argument("--" + arg, required=True)
    p.add_argument("--superseded-by")
    args = vars(parser.parse_args(argv))
    try:
        memory = Memory(root=args.pop("state_root")); command = args.pop("command")
        if command == "prepare": result = memory.prepare(args["path"])
        elif command in {"check", "save"}:
            result = getattr(memory, command)(read(args["packet"]))
            if command == "check": result = result[0]
        else: result = getattr(memory, command)(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        print(f"Contextual ASR blocked: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
