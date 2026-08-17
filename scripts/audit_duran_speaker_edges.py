"""Read-only audit of Cristoforou evidence in The Duran derivatives."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from role_aware_archive import canonical_slug, load_manifest

ROOT = Path(__file__).resolve().parent.parent
DERIVED = ROOT / "archive" / "geopolitics" / "derived" / "speaker-labeled"


def scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\r\n]+)", text)
    return match.group(1).strip() if match else ""


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = {row.get("local_path"): row for row in load_manifest().get("sources", [])}
    records = []
    statuses: Counter[str] = Counter()
    for path in sorted(DERIVED.rglob("*.md")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if "christoforou" not in text.casefold() or "the-duran" not in text.casefold():
            continue
        provenance = re.search(r"speaker_labeling_provenance:\s*(\{.*\})", text)
        payload = {}
        if provenance:
            try:
                payload = json.loads(provenance.group(1))
            except json.JSONDecodeError:
                pass
        source_path = str(payload.get("source_path") or scalar(text, "source_path"))
        labeled = int(payload.get("labeled_turn_count", 0) or 0)
        unknown = int(payload.get("unknown_turn_count", 0) or 0)
        explicit_turns = len(re.findall(r"(?im)^\*\*(?:Alex )?Christoforou\*\*:", text))
        metadata_host = bool(re.search(r"(?im)^host:\s*Alex Christoforou\s*$", text))
        manifest_row = manifest.get(source_path, {})
        status = "turn-labeled" if explicit_turns or labeled else ("metadata-host" if metadata_host else "candidate-only")
        statuses[status] += 1
        records.append({"derived": path.relative_to(ROOT).as_posix(), "source": source_path, "manifest_host": manifest_row.get("host_slug"), "manifest_voices": manifest_row.get("voice_slugs", []), "explicit_christoforou_turns": explicit_turns, "labeled_turns": labeled, "unknown_turns": unknown, "metadata_host": metadata_host, "status": status})
    print(json.dumps({"derivative_count": len(records), "statuses": statuses, "manifest_backed": sum(bool(item["source"]) and item["source"] in manifest for item in records), "records": records}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
