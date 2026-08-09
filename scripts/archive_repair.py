from __future__ import annotations

import argparse
import json
import sys

import archive_repair_engine as engine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or execute one bounded Narrative Geopolitics archive repair class."
    )
    parser.add_argument("--class", dest="repair_class", choices=engine.REPAIR_CLASSES, required=True)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--path",
        dest="paths",
        action="append",
        help="Repository-relative archive source path; repeat for multiple files.",
    )
    target.add_argument(
        "--list-file",
        help="Repository-relative text file containing archive source paths, one per line.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Render the exact plan without writing.")
    mode.add_argument("--execute", action="store_true", help="Apply the reviewed plan.")
    parser.add_argument("--plan-digest", help="SHA-256 emitted by the reviewed dry-run plan.")
    parser.add_argument(
        "--body-file",
        help="Supplied transcript body used only by the bounded body-merge class.",
    )
    parser.add_argument(
        "--resection",
        action="store_true",
        help="Allow sectioning to replace existing transcript section headings.",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(arguments)
    if args.execute and not args.plan_digest:
        parser.error("--execute requires --plan-digest")
    if not args.execute and args.plan_digest:
        parser.error("--plan-digest is valid only with --execute")
    if args.resection and args.repair_class != "sectioning":
        parser.error("--resection is valid only with --class sectioning")
    if args.repair_class == "body-merge" and not args.body_file:
        parser.error("--class body-merge requires --body-file")
    if args.repair_class != "body-merge" and args.body_file:
        parser.error("--body-file is valid only with --class body-merge")
    return args


def target_paths(args: argparse.Namespace) -> list[str]:
    if args.paths:
        return list(args.paths)
    return engine.read_list_file(args.list_file)


def emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(engine.render_markdown(payload), end="")


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        plan = engine.build_plan(
            target_paths(args),
            args.repair_class,
            resection=args.resection,
            replacement_body_path=args.body_file,
        )
        if args.execute:
            payload = engine.apply_plan(plan, expected_digest=args.plan_digest)
        else:
            payload = plan.public()
        emit(payload, args.format)
        return 0
    except (OSError, engine.ArchiveRepairError) as error:
        print(f"archive repair blocked: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
