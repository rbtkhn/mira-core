from __future__ import annotations

import argparse
import sys

import archive_repair


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deprecated adapter for bounded ASR-only archive repair."
    )
    parser.add_argument("--list-file", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--plan-digest")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(arguments)
    if args.execute and not args.plan_digest:
        parser.error("--execute requires --plan-digest")
    if not args.execute and args.plan_digest:
        parser.error("--plan-digest is valid only with --execute")
    return args


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    print(
        "DEPRECATED: use tools/run.ps1 archive-repair --class asr instead.",
        file=sys.stderr,
    )
    forwarded = ["--class", "asr", "--list-file", args.list_file]
    forwarded.append("--execute" if args.execute else "--dry-run")
    if args.plan_digest:
        forwarded.extend(("--plan-digest", args.plan_digest))
    forwarded.extend(("--format", args.format))
    return archive_repair.main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
