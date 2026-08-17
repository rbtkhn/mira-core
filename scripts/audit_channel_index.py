from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
CHANNEL_INDEX_PATH = REPO_ROOT / "narrative-geopolitics" / "channels" / "channel-index.md"
ROW_RE = re.compile(r"^\| `(?P<slug>[^`]+)` \| (?P<rest>.+) \|$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare channel-index counts with manifest host_slug routes."
    )
    parser.add_argument("--check", action="store_true", help="Exit nonzero when active local shelf rows drift.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_manifest_stats() -> dict[str, dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    rows = manifest.get("sources", [])
    by_host: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        host = row.get("host_slug")
        if isinstance(host, str) and host:
            by_host.setdefault(host, []).append(row)

    stats: dict[str, dict[str, object]] = {}
    for host, host_rows in by_host.items():
        dates = sorted(str(row.get("date", "")) for row in host_rows if row.get("date"))
        stats[host] = {
            "files": len(host_rows),
            "days": len(set(dates)),
            "first_day": dates[0] if dates else "",
            "last_day": dates[-1] if dates else "",
        }
    return stats


def parse_channel_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in CHANNEL_INDEX_PATH.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 11 or cells[0] == "Channel slug":
            continue
        slug = cells[0].strip("`")
        try:
            files = int(cells[5])
            days = int(cells[6])
        except ValueError:
            continue
        rows.append(
            {
                "slug": slug,
                "status": cells[2].strip("`"),
                "shelf": cells[4],
                "files": files,
                "days": days,
                "first_day": cells[9].strip("`"),
                "last_day": cells[10].strip("`"),
            }
        )
    return rows


def audit_rows() -> list[dict[str, object]]:
    manifest_stats = load_manifest_stats()
    findings: list[dict[str, object]] = []
    for row in parse_channel_rows():
        slug = str(row["slug"])
        expected = manifest_stats.get(slug)
        if not expected:
            continue
        actual = {
            "files": row["files"],
            "days": row["days"],
            "first_day": row["first_day"],
            "last_day": row["last_day"],
        }
        mismatches = {
            key: {"index": actual[key], "manifest": expected[key]}
            for key in actual
            if actual[key] != expected[key]
        }
        if mismatches:
            findings.append(
                {
                    "slug": slug,
                    "status": row["status"],
                    "active_local_shelf": str(row["shelf"]).startswith("["),
                    "mismatches": mismatches,
                }
            )
    return findings


def main() -> None:
    args = parse_args()
    findings = audit_rows()
    if args.json:
        print(json.dumps({"findings": findings}, indent=2, ensure_ascii=False))
    elif not findings:
        print("channel_index_drift=0")
    else:
        print(f"channel_index_drift={len(findings)}")
        for finding in findings:
            print(f"{finding['slug']}: {finding['mismatches']}")

    if args.check and any(finding["active_local_shelf"] for finding in findings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
