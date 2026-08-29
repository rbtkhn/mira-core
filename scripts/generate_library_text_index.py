"""Generate the human-facing library text source index from the registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "archive" / "library" / "library-registry.json"
INDEX_PATH = ROOT / "archive" / "library" / "text-sources-index.md"


def escape_cell(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for source in registry["sources"]:
        for body in source.get("text_bodies") or []:
            rows.append(
                {
                    "source_id": source.get("source_id", ""),
                    "author": source.get("author", ""),
                    "registry_title": source.get("title", ""),
                    "work_title": body.get("work_title", ""),
                    "edition": body.get("edition_label", ""),
                    "language": body.get("language", ""),
                    "license": body.get("license_status", ""),
                    "bytes": body.get("text_bytes", 0),
                    "uri": body.get("text_location", ""),
                    "body_id": body.get("body_id", ""),
                    "coverage": source.get("coverage_notes") or source.get("notes", ""),
                }
            )

    rows.sort(key=lambda row: (row["source_id"], row["body_id"]))

    lines = [
        "# Library Text Sources Index",
        "",
        "This index lists source text bodies admitted in `archive/library/library-registry.json`. "
        "The source bodies themselves are private/local payloads, normally stored under "
        "the platform Mira Core state root at `library/texts/`; this file records only metadata and logical text URIs.",
        "",
        "- Registry: `library-registry.json`",
        f"- Text bodies indexed: {len(rows)}",
        f"- Registry ID: `{registry.get('registry_id', 'unknown')}`",
        "",
        "| Source ID | Author | Registry title | Work / body | Edition | Language | License | Bytes | Text URI |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]

    for row in rows:
        cells = {key: escape_cell(value) for key, value in row.items()}
        lines.append(
            "| `{source_id}` | {author} | {registry_title} | {work_title} | {edition} | "
            "{language} | {license} | {bytes} | `{uri}` |".format(**cells)
        )

    lines.extend(["", "## Coverage Notes", ""])
    for row in rows:
        lines.append(
            f"- `{escape_cell(row['body_id'])}` ({escape_cell(row['author'])}, "
            f"{escape_cell(row['work_title'])}): {escape_cell(row['coverage'])}"
        )

    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {INDEX_PATH} with {len(rows)} text bodies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
