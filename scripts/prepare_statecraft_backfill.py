"""Prepare a deterministic 2026 statecraft backfill for best-intake.

This tool is intentionally preparatory: it reads the local upstream mirror,
creates an inventory and metadata/body sidecars under work/backfill, and does
not publish archive or manifest changes. The existing best-intake helper is
the publisher of record.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = Path(r"C:\dev\strategy-codex\source-archive\statecraft")
BACKFILL_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "backfill-2026"
VOICE_ROOT = REPO_ROOT / "narrative-geopolitics" / "voices"
MANIFEST_PATH = REPO_ROOT / "archive" / "geopolitics" / "source-manifest.json"


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, meta, body = text.split("---", 2)
    fields: dict[str, str] = {}
    for line in meta.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip("'\"")
        fields[key.strip()] = value
    return fields, body.lstrip("\n")


def known_provenance() -> tuple[set[str], set[str]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    paths = {
        str(row.get("upstream_path", "")).replace("/", "\\").lower()
        for row in manifest.get("sources", [])
        if row.get("upstream_path")
    }
    urls = {
        str(row.get("source_url", "")).strip()
        for row in manifest.get("sources", [])
        if row.get("source_url")
    }
    return paths, urls


def voice_hits(filename: str, voices: list[str], fields: dict[str, str]) -> list[str]:
    hits = [voice for voice in voices if re.search(rf"(^|[-_]){re.escape(voice)}([-_.]|$)", filename)]
    # The canonical voice is Mercouris for both solo and The Duran uploads.
    if "alexander-mercouris" in filename and "mercouris" not in hits:
        hits.append("mercouris")
    if "jiang" in voices and any("jiang xueqin" in fields.get(key, "").lower() for key in ("host", "guest", "show", "channel_name")):
        hits.append("jiang")
    return sorted(set(hits))


def host_slug(fields: dict[str, str], filename: str) -> str:
    if fields.get("channel_slug"):
        return fields["channel_slug"]
    for candidate in (
        "alexander-mercouris", "glenn-diesen", "dialogue-works", "judging-freedom",
        "daniel-davis", "mario-nawfal", "mearsheimer",
    ):
        if candidate in filename:
            return candidate
    return "upstream-unresolved"


def title(fields: dict[str, str], path: Path) -> str:
    return fields.get("title") or re.sub(r"-2026-\d{2}-\d{2}$", "", path.stem).replace("source-", "", 1).replace("-", " ").strip().title()


def local_target_exists(source_title: str, pub_date: str) -> bool:
    slug = re.sub(r"[^a-z0-9]+", "-", source_title.lower()).strip("-")
    return (REPO_ROOT / "archive" / "geopolitics" / "sources" / pub_date / f"source-{slug}-{pub_date}.md").exists()


def source_files() -> list[Path]:
    return sorted(
        path for path in UPSTREAM_ROOT.rglob("source-*.md")
        if re.search(r"\\2026-\d{2}-\d{2}\\", str(path))
    )


def prepare() -> list[dict[str, object]]:
    voices = sorted(path.name for path in VOICE_ROOT.iterdir() if path.is_dir() and not path.name.startswith("_"))
    known_paths, known_urls = known_provenance()
    BACKFILL_ROOT.mkdir(parents=True, exist_ok=True)
    for generated in BACKFILL_ROOT.glob("2026-*/metadata/*.md"):
        generated.unlink()
    for generated in BACKFILL_ROOT.glob("2026-*/bodies/*.txt"):
        generated.unlink()
    records: list[dict[str, object]] = []
    for path in source_files():
        fields, body = frontmatter_and_body(path)
        rel = str(path).replace("\\", "/")
        normalized = str(path).replace("/", "\\").lower()
        pub_date = fields.get("pub_date") or next((part for part in path.parts if re.fullmatch(r"2026-\d{2}-\d{2}", part)), "")
        hits = voice_hits(path.name, voices, fields)
        reason = "eligible"
        if normalized in known_paths or fields.get("source_url", "") in known_urls or local_target_exists(title(fields, path), pub_date):
            reason = "already_imported"
        elif not hits:
            reason = "unrecognized_voice"
        elif path.name == "header.md":
            reason = "land_header"
        elif not body.strip():
            reason = "empty_body"
        record: dict[str, object] = {
            "upstream_path": rel,
            "upstream_absolute_path": str(path),
            "date": pub_date,
            "month": pub_date[:7],
            "title": title(fields, path),
            "voice_slugs": hits,
            "host_slug": host_slug(fields, path.name),
            "host": fields.get("host", ""),
            "guest": fields.get("guest", ""),
            "show": fields.get("show", fields.get("channel_name", "")),
            "source_form": fields.get("source_form", "interview"),
            "source_url": fields.get("source_url", ""),
            "body_kind": fields.get("kind", "transcript"),
            "disposition": reason,
            "missing_month_cell": None,
        }
        records.append(record)
        if reason == "eligible":
            month_dir = BACKFILL_ROOT / pub_date[:7]
            bodies_dir = month_dir / "bodies"
            meta_dir = month_dir / "metadata"
            bodies_dir.mkdir(parents=True, exist_ok=True)
            meta_dir.mkdir(parents=True, exist_ok=True)
            body_path = bodies_dir / f"{path.stem}.txt"
            body_path.write_text(body, encoding="utf-8")
            metadata_lines = [
                f"pub_date: {pub_date}",
                f"ingest_date: {date.today().isoformat()}",
                f"title: {record['title']}",
                f"url: {record['source_url']}",
                f"body_file: {body_path}",
                f"host_slug: {record['host_slug']}",
                f"host: {record['host']}",
                f"guest: {record['guest']}",
                f"show: {record['show']}",
                f"source_form: {record['source_form']}",
                "kind: transcript",
                "source_class: historical upstream transcript backfill",
                "modality: transcript",
                "review_state: unreviewed",
                "routing_state: provisional",
                "source_note: Imported from the local strategy-codex source archive; transcript body preserved and not treated as verified fact.",
                "editorial_note: Historical backfill; upstream transcript metadata retained where available.",
                f"upstream_path: {rel}",
            ]
            for voice in hits:
                metadata_lines.append(f"voice_slug: {voice}")
            (meta_dir / f"{path.stem}.md").write_text("\n".join(metadata_lines) + "\n", encoding="utf-8")
    (BACKFILL_ROOT / "inventory.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    records = prepare()
    counts = Counter(str(item["disposition"]) for item in records)
    eligible = [item for item in records if item["disposition"] == "eligible"]
    print(json.dumps({"records": len(records), "eligible": len(eligible), "dispositions": counts}, indent=2, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
