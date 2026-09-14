from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract one exact, provenance-preserving segment from a UTF-8 library candidate."
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--include-end", action="store_true")
    parser.add_argument("--prefix-through", default="")
    args = parser.parse_args()

    source_bytes = args.source.read_bytes()
    text = source_bytes.decode("utf-8")
    start = text.find(args.start)
    if start < 0 or text.find(args.start, start + 1) >= 0:
        raise SystemExit("start marker must occur exactly once")
    end = text.find(args.end, start + len(args.start))
    if end < 0 or text.find(args.end, end + 1) >= 0:
        raise SystemExit("end marker must occur exactly once after start")
    if args.include_end:
        end += len(args.end)

    prefix = ""
    if args.prefix_through:
        prefix_end = text.find(args.prefix_through)
        if prefix_end < 0 or prefix_end >= start:
            raise SystemExit("prefix marker must occur before the segment")
        prefix = text[: prefix_end + len(args.prefix_through)].rstrip() + "\n\n"

    output_text = prefix + text[start:end].strip() + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text, encoding="utf-8", newline="\n")
    output_bytes = args.output.read_bytes()
    print(
        json.dumps(
            {
                "source": str(args.source.resolve()),
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "output": str(args.output.resolve()),
                "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
                "output_bytes": len(output_bytes),
                "start_offset": start,
                "end_offset": end,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
