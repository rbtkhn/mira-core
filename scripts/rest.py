from __future__ import annotations

import argparse
import json

import mira_continuity
import rest_receipts


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Close one Mira Core session without requiring permanent finality.")
    root.add_argument("--inbox")
    root.add_argument("--check", action="store_true")
    root.add_argument("--json", action="store_true")
    root.add_argument("--debt", action="append", choices=sorted(rest_receipts.DEBT_CLASSES), default=[])
    root.add_argument("--review", action="append", choices=sorted(rest_receipts.REVIEW_STATES), default=[])
    commands = root.add_subparsers(dest="command")
    for name in ("status", "verify"):
        item = commands.add_parser(name)
        item.add_argument("--inbox")
        item.add_argument("--json", action="store_true")
    return root


def current_source(*, required: bool = True):
    session = rest_receipts.session_uuid()
    source = mira_continuity.find_session_source(session)
    if source is None and required:
        raise rest_receipts.RestError("current repository session source is unavailable")
    return session, source


def emit(value: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2))
        return
    print(f"Rest state: {value.get('current_state', value.get('status', 'unknown'))}")
    if value.get("closure_debt"):
        print("Visible debt: " + ", ".join(value["closure_debt"]))
    print(f"Mutation performed: {'yes' if value.get('mutation_performed') else 'no'}")


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        inbox = rest_receipts.resolve_inbox(args.inbox)
        if args.command in {"status", "verify"}:
            session, source = current_source(required=False)
            value = rest_receipts.projection(inbox, session, source)
            value["status"] = "verified" if args.command == "verify" else "ok"
            emit(value, args.json)
            return 0
        session, source = current_source()
        directory = rest_receipts.session_dir(inbox, session)
        existing = rest_receipts.load_events(inbox, session)
        additions = rest_receipts.planned_events(source, existing, args.debt, args.review)
        value = rest_receipts.projection(inbox, session, source)
        value.update({"status": "ready" if args.check else "written", "planned_events": additions})
        if not args.check and additions:
            with rest_receipts.session_lock(directory):
                existing = rest_receipts.load_events(inbox, session)
                additions = rest_receipts.planned_events(source, existing, args.debt, args.review)
                rest_receipts.write_events(inbox, session, additions)
            value = rest_receipts.projection(inbox, session, source)
            value.update({"status": "written", "mutation_performed": bool(additions)})
        emit(value, args.json)
        return 0
    except (OSError, ValueError, rest_receipts.RestError) as error:
        print(f"rest error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
