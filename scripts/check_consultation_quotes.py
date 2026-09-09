"""Read-only literal quotation checks; passing does not establish meaning or truth."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def check_quotes(index: object, quotes: object) -> dict:
    """Validate pilot source/paragraph records and {paragraph_id, quotation} rows."""
    def invalid(reason: str) -> dict:
        return {"status": "invalid input", "reason": reason, "results": []}

    if not isinstance(index, list) or not index:
        return invalid("index must be a nonempty list")
    paragraphs = {}
    source_ids = set()
    for source in index:
        if not isinstance(source, dict):
            return invalid("source must be an object")
        sid = source.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in source_ids:
            return invalid("source IDs must be nonempty and unique")
        source_ids.add(sid)
        rows = source.get("paragraphs")
        if not isinstance(rows, list) or not rows:
            return invalid("source paragraphs must be a nonempty list")
        for row in rows:
            if not isinstance(row, dict):
                return invalid("paragraph must be an object")
            pid, body = row.get("id"), row.get("text")
            if not isinstance(pid, str) or not pid.strip() or pid in paragraphs:
                return invalid("paragraph IDs must be nonempty and globally unique")
            if not isinstance(body, str) or not body.strip():
                return invalid("paragraph text must be nonempty")
            paragraphs[pid] = body
    if not isinstance(quotes, list) or not quotes:
        return invalid("quotes must be a nonempty list")
    for row in quotes:
        if not isinstance(row, dict) or any(
            not isinstance(row.get(key), str) or not row[key].strip()
            for key in ("paragraph_id", "quotation")
        ):
            return invalid("quote rows require nonempty paragraph_id and quotation strings")
    results = []
    for number, row in enumerate(quotes, 1):
        body = paragraphs.get(row["paragraph_id"])
        status = ("missing paragraph" if body is None else
                  "passed" if row["quotation"] in body else "quotation mismatch")
        # Row numbers identify inputs without echoing private source text or identifiers.
        results.append({"row": number, "status": status})
    return {"status": "passed" if all(r["status"] == "passed" for r in results)
            else "failed", "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--quotes", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        index = json.loads(args.index.read_text(encoding="utf-8-sig"))
        quotes = json.loads(args.quotes.read_text(encoding="utf-8-sig"))
        result = check_quotes(index, quotes)
    except (OSError, UnicodeError, ValueError, RecursionError):
        result = {"status": "invalid input", "reason": "cannot read valid UTF-8 JSON inputs", "results": []}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["status"] == "passed" else 2 if result["status"] == "invalid input" else 1


if __name__ == "__main__":
    raise SystemExit(main())
