from __future__ import annotations

import argparse
import json
from pathlib import Path

import voice_indexes


def collect_overrides(
    manifest: dict, repo_root: Path, voices_root: Path
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for slug, index_path in sorted(voice_indexes.shelves(voices_root).items()):
        text = index_path.read_text(encoding="utf-8")
        if slug == "pape":
            existing, _ = voice_indexes.parse_pape(index_path, text, repo_root)
        else:
            existing, _, _ = voice_indexes.parse_standard(index_path, text, repo_root)
        rows = voice_indexes.all_manifest_rows_for_voice(manifest, slug)
        for row in rows:
            old = existing.get(row["local_path"])
            if old is None:
                continue
            default = voice_indexes.derive_role(row, slug)
            if slug == "pape":
                default = "authored" if default == "authored" else "guest"
            if old["role"] != default:
                result.append(
                    {
                        "voice_slug": slug,
                        "local_path": row["local_path"],
                        "role": old["role"],
                    }
                )
    return sorted(result, key=lambda item: (item["voice_slug"], item["local_path"]))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture curated voice roles that differ from deterministic derivation."
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    voices_root = voice_indexes.default_voices_root()
    manifest = voice_indexes.load_manifest()
    overrides = collect_overrides(manifest, voice_indexes.REPO_ROOT, voices_root)
    payload = {"schema_version": 1, "overrides": overrides}
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    target = voices_root / voice_indexes.ROLE_OVERRIDES_NAME
    if args.write:
        target.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {len(overrides)} overrides to {target}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
